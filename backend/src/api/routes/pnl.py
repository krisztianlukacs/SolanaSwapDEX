from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user_wallet
from src.api.schemas.pnl import PnlDataPoint, PnlHistoryResponse
from src.db.repositories.pnl_repo import PnlRepository

router = APIRouter(prefix="/pnl", tags=["pnl"])

RANGE_MAP = {"7": 7, "30": 30, "90": 90, "all": None}


@router.get("/history", response_model=PnlHistoryResponse)
async def get_pnl_history(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
    range: str = Query("30", description="Time range: 7, 30, 90, or all"),
) -> PnlHistoryResponse:
    days = RANGE_MAP.get(range, 30)

    pnl_repo = PnlRepository(db)
    snapshots = await pnl_repo.get_history(wallet, days=days)

    history = [
        PnlDataPoint(
            date=s.date,
            daily_pnl=float(s.daily_pnl),
            cumulative_pnl=float(s.cumulative_pnl),
            daily_sol_pnl=float(s.daily_sol_pnl),
            cumulative_sol_pnl=float(s.cumulative_sol_pnl),
            daily_usdc_pnl=float(s.daily_usdc_pnl),
            cumulative_usdc_pnl=float(s.cumulative_usdc_pnl),
            sol_price=float(s.sol_price),
        )
        for s in snapshots
    ]

    return PnlHistoryResponse(history=history, range_days=days)
