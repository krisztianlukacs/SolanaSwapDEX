import asyncio
from datetime import datetime, timezone

from sqlalchemy import func, select

from src.common.logging import setup_logger
from src.common.exceptions import CooldownActiveError, DailyLimitExceededError
from src.db.base import async_session_factory
from src.db.models.transaction import Transaction
from src.db.repositories.signal_repo import SignalRepository
from src.db.repositories.user_repo import UserRepository
from src.signals.queue import get_execution_queue
from src.signals.validator import validate_user_for_signal

logger = setup_logger("signals")


def process_signal(signal_id: int, signal_type: str) -> None:
    """Entry point for RQ signal worker. Runs the async logic in an event loop."""
    asyncio.run(_process_signal_async(signal_id, signal_type))


async def _process_signal_async(signal_id: int, signal_type: str) -> None:
    """Fan out signal to all eligible users."""
    logger.info("Processing signal %d type=%s", signal_id, signal_type)

    async with async_session_factory() as session:
        signal_repo = SignalRepository(session)
        user_repo = UserRepository(session)

        await signal_repo.update_status(signal_id, "processing")

        enabled_users = await user_repo.get_enabled_users()
        eligible_count = 0

        for profile in enabled_users:
            try:
                # Count today's executions for this user
                today_start = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                result = await session.execute(
                    select(func.count())
                    .select_from(Transaction)
                    .where(
                        Transaction.owner == profile.owner,
                        Transaction.date >= today_start,
                    )
                )
                daily_count = result.scalar_one()

                if validate_user_for_signal(profile, daily_count):
                    # Enqueue execution for this user
                    execution_queue = get_execution_queue()
                    execution_queue.enqueue(
                        "src.signals.workers.execution_worker.execute_for_user",
                        signal_id,
                        signal_type,
                        profile.owner,
                        job_timeout="5m",
                    )
                    eligible_count += 1
                    logger.info("Enqueued execution for user %s", profile.owner)

            except (CooldownActiveError, DailyLimitExceededError) as e:
                logger.info("User %s skipped: %s", profile.owner, str(e))
            except Exception as e:
                logger.error("Error processing user %s: %s", profile.owner, str(e))

        await signal_repo.update_status(
            signal_id,
            "completed",
            affected_users=eligible_count,
        )
        await session.commit()

    logger.info("Signal %d completed: %d users enqueued", signal_id, eligible_count)
