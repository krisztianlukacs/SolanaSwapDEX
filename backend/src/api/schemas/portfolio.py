from pydantic import BaseModel


class PortfolioMetrics(BaseModel):
    total_value_usd: float
    sol_value_usd: float
    usdc_value_usd: float
    fee_pool_value_usd: float
    pnl_all_time: float
    pnl_all_time_pct: float
    pnl_24h: float
    pnl_24h_pct: float
    pnl_30d: float
    pnl_30d_pct: float
    sol_pnl: float
    usdc_pnl: float
