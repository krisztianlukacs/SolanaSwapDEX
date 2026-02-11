from pydantic import BaseModel, Field


class SignalRequest(BaseModel):
    signal_type: str = Field(..., pattern="^(SOL_TO_USDC|USDC_TO_SOL)$")
    metadata: dict | None = None


class SignalResponse(BaseModel):
    id: int
    signal_type: str
    status: str
    message: str
