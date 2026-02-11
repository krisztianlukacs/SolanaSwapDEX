import asyncio
import functools
from collections.abc import Callable

from src.common.logging import setup_logger

logger = setup_logger("signals")


def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for exponential backoff retry on async functions."""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            "Retry %d/%d for %s: %s (waiting %.1fs)",
                            attempt + 1,
                            max_retries,
                            func.__name__,
                            str(e),
                            delay,
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            "All %d retries exhausted for %s: %s",
                            max_retries,
                            func.__name__,
                            str(e),
                        )
            raise last_exc

        return wrapper

    return decorator
