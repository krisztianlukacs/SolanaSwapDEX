from pydantic import BaseModel


class VaultBalanceResponse(BaseModel):
    sol_balance: float
    sol_balance_usd: float
    usdc_balance: float
    usdc_balance_usd: float
    fee_pool_balance: float
    fee_pool_balance_usd: float
    fee_pool_status: str  # "healthy", "low", "critical"


class DepositWithdrawRequest(BaseModel):
    amount: float  # Human-readable (SOL or USDC)


class DepositWithdrawResponse(BaseModel):
    success: bool
    new_balance: float
    token: str
