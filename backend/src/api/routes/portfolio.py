from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user_wallet
from src.api.schemas.portfolio import PortfolioMetrics
from src.common.constants import lamports_to_sol, usdc_base_to_human
from src.db.repositories.vault_repo import VaultRepository
from src.db.repositories.pnl_repo import PnlRepository

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

# Placeholder price — in production this comes from an oracle or price feed
SOL_PRICE_USD = 148.32


@router.get("/metrics", response_model=PortfolioMetrics)
async def get_portfolio_metrics(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> PortfolioMetrics:
    vault_repo = VaultRepository(db)
    pnl_repo = PnlRepository(db)

    vault = await vault_repo.get_or_create(wallet)
    latest_pnl = await pnl_repo.get_latest(wallet)

    sol_human = lamports_to_sol(vault.sol_balance)
    usdc_human = usdc_base_to_human(vault.usdc_balance)
    fee_human = lamports_to_sol(vault.fee_pool_balance)

    sol_usd = sol_human * SOL_PRICE_USD
    usdc_usd = usdc_human
    fee_usd = fee_human * SOL_PRICE_USD
    total_usd = sol_usd + usdc_usd + fee_usd

    pnl_all_time = float(latest_pnl.cumulative_pnl) if latest_pnl else 0.0
    sol_pnl = float(latest_pnl.cumulative_sol_pnl) if latest_pnl else 0.0
    usdc_pnl = float(latest_pnl.cumulative_usdc_pnl) if latest_pnl else 0.0

    # Get 24h and 30d PnL from history
    history_30d = await pnl_repo.get_history(wallet, days=30)
    pnl_24h = float(history_30d[-1].daily_pnl) if history_30d else 0.0
    pnl_30d = sum(float(s.daily_pnl) for s in history_30d) if history_30d else 0.0

    # Calculate percentages (avoid division by zero)
    initial_value = total_usd - pnl_all_time if total_usd - pnl_all_time > 0 else 1
    pnl_all_time_pct = (pnl_all_time / initial_value) * 100
    value_yesterday = total_usd - pnl_24h if total_usd - pnl_24h > 0 else 1
    pnl_24h_pct = (pnl_24h / value_yesterday) * 100
    value_30d_ago = total_usd - pnl_30d if total_usd - pnl_30d > 0 else 1
    pnl_30d_pct = (pnl_30d / value_30d_ago) * 100

    return PortfolioMetrics(
        total_value_usd=round(total_usd, 2),
        sol_value_usd=round(sol_usd, 2),
        usdc_value_usd=round(usdc_usd, 2),
        fee_pool_value_usd=round(fee_usd, 2),
        pnl_all_time=round(pnl_all_time, 2),
        pnl_all_time_pct=round(pnl_all_time_pct, 2),
        pnl_24h=round(pnl_24h, 2),
        pnl_24h_pct=round(pnl_24h_pct, 2),
        pnl_30d=round(pnl_30d, 2),
        pnl_30d_pct=round(pnl_30d_pct, 2),
        sol_pnl=round(sol_pnl, 9),
        usdc_pnl=round(usdc_pnl, 6),
    )
