from src.common.logging import setup_logger
from src.signals.queue import get_signal_queue

logger = setup_logger("signals")


def enqueue_signal(signal_id: int, signal_type: str) -> None:
    """Enqueue a signal for processing by the signal worker."""
    queue = get_signal_queue()
    job = queue.enqueue(
        "src.signals.workers.signal_worker.process_signal",
        signal_id,
        signal_type,
        job_timeout="5m",
    )
    logger.info("Signal %d enqueued as job %s", signal_id, job.id)
