from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.api.schemas.signals import SignalRequest, SignalResponse
from src.common.logging import setup_logger
from src.db.repositories.signal_repo import SignalRepository

router = APIRouter(prefix="/signals", tags=["signals"])
logger = setup_logger("signals")


@router.post("", response_model=SignalResponse)
async def receive_signal(
    request: SignalRequest,
    db: AsyncSession = Depends(get_db_session),
) -> SignalResponse:
    signal_repo = SignalRepository(db)

    # Log the signal to DB
    signal_log = await signal_repo.create(
        signal_type=request.signal_type,
        status="received",
        metadata_=request.metadata,
    )

    logger.info("Signal received: id=%d type=%s", signal_log.id, request.signal_type)

    # Enqueue to Redis for processing
    try:
        from src.signals.receiver import enqueue_signal

        enqueue_signal(signal_log.id, request.signal_type)
        message = "Signal received and queued for processing"
    except Exception as e:
        logger.warning("Failed to enqueue signal %d: %s", signal_log.id, str(e))
        message = "Signal received but queuing failed — will retry"

    return SignalResponse(
        id=signal_log.id,
        signal_type=request.signal_type,
        status="received",
        message=message,
    )
