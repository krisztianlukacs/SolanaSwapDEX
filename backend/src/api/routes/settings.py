from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user_wallet
from src.api.schemas.settings import SettingsResponse, SettingsUpdateRequest
from src.common.constants import (
    DEFAULT_TRADE_SIZE_SOL,
    DEFAULT_TRADE_SIZE_USDC,
    DEFAULT_MIN_FEE_POOL,
    DEFAULT_TARGET_FEE_POOL,
    DEFAULT_MAX_SLIPPAGE_BPS,
    DEFAULT_RELAYER_REFUND,
    DEFAULT_DAILY_LIMIT,
)
from src.db.repositories.user_repo import UserRepository

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> SettingsResponse:
    user_repo = UserRepository(db)
    profile = await user_repo.get_or_create(wallet)

    return SettingsResponse(
        owner=profile.owner,
        enabled=profile.enabled,
        trade_size_sol=profile.trade_size_sol,
        trade_size_usdc=profile.trade_size_usdc,
        min_fee_pool=profile.min_fee_pool,
        target_fee_pool=profile.target_fee_pool,
        max_slippage_bps=profile.max_slippage_bps,
        protocol_fee_bps=profile.protocol_fee_bps,
        relayer_refund_lamports=profile.relayer_refund_lamports,
        keeper_allowlist=profile.keeper_allowlist,
        daily_limit=profile.daily_limit,
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    request: SettingsUpdateRequest,
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> SettingsResponse:
    user_repo = UserRepository(db)
    await user_repo.get_or_create(wallet)

    update_data = request.model_dump(exclude_unset=True)
    profile = await user_repo.update(wallet, **update_data)

    return SettingsResponse(
        owner=profile.owner,
        enabled=profile.enabled,
        trade_size_sol=profile.trade_size_sol,
        trade_size_usdc=profile.trade_size_usdc,
        min_fee_pool=profile.min_fee_pool,
        target_fee_pool=profile.target_fee_pool,
        max_slippage_bps=profile.max_slippage_bps,
        protocol_fee_bps=profile.protocol_fee_bps,
        relayer_refund_lamports=profile.relayer_refund_lamports,
        keeper_allowlist=profile.keeper_allowlist,
        daily_limit=profile.daily_limit,
    )


@router.post("/reset", response_model=SettingsResponse)
async def reset_settings(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> SettingsResponse:
    user_repo = UserRepository(db)
    await user_repo.get_or_create(wallet)

    profile = await user_repo.update(
        wallet,
        enabled=True,
        trade_size_sol=DEFAULT_TRADE_SIZE_SOL,
        trade_size_usdc=DEFAULT_TRADE_SIZE_USDC,
        min_fee_pool=DEFAULT_MIN_FEE_POOL,
        target_fee_pool=DEFAULT_TARGET_FEE_POOL,
        max_slippage_bps=DEFAULT_MAX_SLIPPAGE_BPS,
        relayer_refund_lamports=DEFAULT_RELAYER_REFUND,
        daily_limit=DEFAULT_DAILY_LIMIT,
        keeper_allowlist=None,
    )

    return SettingsResponse(
        owner=profile.owner,
        enabled=profile.enabled,
        trade_size_sol=profile.trade_size_sol,
        trade_size_usdc=profile.trade_size_usdc,
        min_fee_pool=profile.min_fee_pool,
        target_fee_pool=profile.target_fee_pool,
        max_slippage_bps=profile.max_slippage_bps,
        protocol_fee_bps=profile.protocol_fee_bps,
        relayer_refund_lamports=profile.relayer_refund_lamports,
        keeper_allowlist=profile.keeper_allowlist,
        daily_limit=profile.daily_limit,
    )
