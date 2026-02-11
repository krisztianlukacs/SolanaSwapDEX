import redis
from rq import Queue

from src.config.settings import settings
from src.common.logging import setup_logger

logger = setup_logger("signals")

_redis_conn: redis.Redis | None = None


def get_redis_connection() -> redis.Redis:
    global _redis_conn
    if _redis_conn is None:
        _redis_conn = redis.from_url(settings.redis_url)
        logger.info("Redis connection established: %s", settings.redis_url)
    return _redis_conn


def get_signal_queue() -> Queue:
    return Queue("signals", connection=get_redis_connection())


def get_execution_queue() -> Queue:
    return Queue("executions", connection=get_redis_connection())
