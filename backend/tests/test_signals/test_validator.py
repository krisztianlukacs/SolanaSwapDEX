from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from src.common.exceptions import CooldownActiveError, DailyLimitExceededError
from src.signals.validator import validate_user_for_signal


def _make_profile(**overrides):
    """Create a mock UserProfile for testing."""
    defaults = {
        "owner": "test_wallet_address_here_12345678901",
        "enabled": True,
        "last_execution": None,
        "daily_limit": 10,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


class TestSignalValidator:
    def test_eligible_user(self):
        profile = _make_profile()
        assert validate_user_for_signal(profile, daily_executions=0) is True

    def test_disabled_user(self):
        profile = _make_profile(enabled=False)
        assert validate_user_for_signal(profile, daily_executions=0) is False

    def test_cooldown_active(self):
        profile = _make_profile(
            last_execution=datetime.now(timezone.utc) - timedelta(seconds=60)
        )
        with pytest.raises(CooldownActiveError):
            validate_user_for_signal(profile, daily_executions=0)

    def test_cooldown_expired(self):
        profile = _make_profile(
            last_execution=datetime.now(timezone.utc) - timedelta(seconds=600)
        )
        assert validate_user_for_signal(profile, daily_executions=0) is True

    def test_daily_limit_exceeded(self):
        profile = _make_profile(daily_limit=5)
        with pytest.raises(DailyLimitExceededError):
            validate_user_for_signal(profile, daily_executions=5)

    def test_daily_limit_not_exceeded(self):
        profile = _make_profile(daily_limit=5)
        assert validate_user_for_signal(profile, daily_executions=4) is True

    def test_no_daily_limit(self):
        profile = _make_profile(daily_limit=None)
        assert validate_user_for_signal(profile, daily_executions=100) is True
