from datetime import datetime, timezone

from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.signal_log import SignalLog


class SignalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> SignalLog:
        log = SignalLog(**kwargs)
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_by_id(self, log_id: int) -> SignalLog | None:
        result = await self.session.execute(
            select(SignalLog).where(SignalLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        log_id: int,
        status: str,
        *,
        error_message: str | None = None,
        affected_users: int | None = None,
    ) -> None:
        values: dict = {"status": status}
        if status in ("completed", "failed"):
            values["processed_at"] = datetime.now(timezone.utc)
        if error_message is not None:
            values["error_message"] = error_message
        if affected_users is not None:
            values["affected_users"] = affected_users

        await self.session.execute(
            update(SignalLog).where(SignalLog.id == log_id).values(**values)
        )
        await self.session.flush()

    async def get_recent(self, limit: int = 20) -> list[SignalLog]:
        result = await self.session.execute(
            select(SignalLog).order_by(desc(SignalLog.received_at)).limit(limit)
        )
        return list(result.scalars().all())
