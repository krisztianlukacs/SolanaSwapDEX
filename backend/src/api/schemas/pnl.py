from datetime import date

from pydantic import BaseModel


class PnlDataPoint(BaseModel):
    date: date
    daily_pnl: float
    cumulative_pnl: float
    daily_sol_pnl: float
    cumulative_sol_pnl: float
    daily_usdc_pnl: float
    cumulative_usdc_pnl: float
    sol_price: float


class PnlHistoryResponse(BaseModel):
    history: list[PnlDataPoint]
    range_days: int | None
