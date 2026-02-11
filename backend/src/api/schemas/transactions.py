from datetime import datetime

from pydantic import BaseModel

from src.api.schemas.common import PaginationMeta


class TransactionResponse(BaseModel):
    id: int
    date: datetime
    type: str
    amount_in: float
    amount_out: float
    token_in: str
    token_out: str
    slippage_bps: int
    fee: float
    status: str
    signature: str | None
    error_message: str | None


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    pagination: PaginationMeta
