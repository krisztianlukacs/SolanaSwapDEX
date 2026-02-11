from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user_wallet
from src.api.schemas.strategy import StrategyStatus
from src.config.settings import settings
from src.db.models.transaction import Transaction
from src.db.repositories.user_repo import UserRepository
from src.db.repositories.vault_repo import VaultRepository

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.get("/status", response_model=StrategyStatus)
async def get_strategy_status(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> StrategyStatus:
    user_repo = UserRepository(db)
    vault_repo = VaultRepository(db)

    profile = await user_repo.get_or_create(wallet)
    vault = await vault_repo.get_or_create(wallet)

    # Determine current position based on vault balances
    if vault.sol_balance > vault.usdc_balance:
        position = "SOL"
    elif vault.usdc_balance > vault.sol_balance:
        position = "USDC"
    else:
        position = "mixed"

    # Count total executions
    total_result = await db.execute(
        select(func.count()).select_from(Transaction).where(Transaction.owner == wallet)
    )
    total_executions = total_result.scalar_one()

    # Count today's executions
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_result = await db.execute(
        select(func.count())
        .select_from(Transaction)
        .where(Transaction.owner == wallet, Transaction.date >= today_start)
    )
    daily_executions = daily_result.scalar_one()

    # Calculate next execution ETA
    next_eta = None
    if profile.last_execution and profile.enabled:
        cooldown_end = profile.last_execution + timedelta(seconds=settings.signal_cooldown_seconds)
        now = datetime.now(timezone.utc)
        if cooldown_end > now:
            remaining = cooldown_end - now
            minutes = int(remaining.total_seconds() // 60)
            next_eta = f"~{minutes}m"
        else:
            next_eta = "Ready"

    return StrategyStatus(
        enabled=profile.enabled,
        current_position=position,
        last_execution=profile.last_execution,
        next_execution_eta=next_eta,
        total_executions=total_executions,
        daily_executions=daily_executions,
        daily_limit=profile.daily_limit,
    )
