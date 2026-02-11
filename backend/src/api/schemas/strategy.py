from datetime import datetime

from pydantic import BaseModel


class StrategyStatus(BaseModel):
    enabled: bool
    current_position: str  # "SOL" or "USDC" or "mixed"
    last_execution: datetime | None
    next_execution_eta: str | None
    total_executions: int
    daily_executions: int
    daily_limit: int | None
