from datetime import datetime, timedelta, timezone

from src.common.exceptions import CooldownActiveError, DailyLimitExceededError
from src.common.logging import setup_logger
from src.config.settings import settings
from src.db.models.user_profile import UserProfile

logger = setup_logger("signals")


def validate_user_for_signal(profile: UserProfile, daily_executions: int) -> bool:
    """Check if a user is eligible to receive a signal execution.

    Raises CooldownActiveError or DailyLimitExceededError if not eligible.
    Returns True if eligible.
    """
    # Check enabled
    if not profile.enabled:
        logger.info("User %s is disabled, skipping", profile.owner)
        return False

    # Check cooldown
    if profile.last_execution:
        cooldown_end = profile.last_execution + timedelta(seconds=settings.signal_cooldown_seconds)
        now = datetime.now(timezone.utc)
        if cooldown_end > now:
            remaining = (cooldown_end - now).total_seconds()
            raise CooldownActiveError(
                f"Cooldown active for user {profile.owner}: {remaining:.0f}s remaining"
            )

    # Check daily limit
    if profile.daily_limit is not None and daily_executions >= profile.daily_limit:
        raise DailyLimitExceededError(
            f"User {profile.owner} has reached daily limit of {profile.daily_limit}"
        )

    return True
