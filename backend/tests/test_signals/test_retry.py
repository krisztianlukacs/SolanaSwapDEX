import pytest

from src.signals.retry import with_retry


@pytest.mark.asyncio
class TestRetryDecorator:
    async def test_success_no_retry(self):
        call_count = 0

        @with_retry(max_retries=3, base_delay=0.01)
        async def succeeds():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await succeeds()
        assert result == "ok"
        assert call_count == 1

    async def test_retry_then_success(self):
        call_count = 0

        @with_retry(max_retries=3, base_delay=0.01)
        async def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "ok"

        result = await fails_twice()
        assert result == "ok"
        assert call_count == 3

    async def test_all_retries_exhausted(self):
        call_count = 0

        @with_retry(max_retries=2, base_delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("always fails")

        with pytest.raises(ValueError, match="always fails"):
            await always_fails()

        assert call_count == 3  # initial + 2 retries
