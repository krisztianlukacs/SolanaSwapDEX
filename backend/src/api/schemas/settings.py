from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    owner: str
    enabled: bool
    trade_size_sol: int
    trade_size_usdc: int
    min_fee_pool: int
    target_fee_pool: int
    max_slippage_bps: int
    protocol_fee_bps: int
    relayer_refund_lamports: int
    keeper_allowlist: list[str] | None
    daily_limit: int | None


class SettingsUpdateRequest(BaseModel):
    enabled: bool | None = None
    trade_size_sol: int | None = Field(None, gt=0)
    trade_size_usdc: int | None = Field(None, gt=0)
    min_fee_pool: int | None = Field(None, ge=0)
    target_fee_pool: int | None = Field(None, ge=0)
    max_slippage_bps: int | None = Field(None, ge=1, le=1000)
    relayer_refund_lamports: int | None = Field(None, ge=0)
    keeper_allowlist: list[str] | None = None
    daily_limit: int | None = Field(None, ge=1)
