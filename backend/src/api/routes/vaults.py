from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user_wallet
from src.api.schemas.vaults import VaultBalanceResponse, DepositWithdrawRequest, DepositWithdrawResponse
from src.common.constants import lamports_to_sol, sol_to_lamports, usdc_base_to_human, usdc_human_to_base
from src.common.exceptions import InsufficientBalanceError, ValidationError
from src.db.repositories.vault_repo import VaultRepository

router = APIRouter(prefix="/vaults", tags=["vaults"])

SOL_PRICE_USD = 148.32


@router.get("/balances", response_model=VaultBalanceResponse)
async def get_vault_balances(
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> VaultBalanceResponse:
    vault_repo = VaultRepository(db)
    vault = await vault_repo.get_or_create(wallet)

    sol_human = lamports_to_sol(vault.sol_balance)
    usdc_human = usdc_base_to_human(vault.usdc_balance)
    fee_human = lamports_to_sol(vault.fee_pool_balance)

    # Determine fee pool status based on min/target thresholds
    from src.db.repositories.user_repo import UserRepository

    user_repo = UserRepository(db)
    profile = await user_repo.get_or_create(wallet)

    if vault.fee_pool_balance >= profile.target_fee_pool:
        fee_status = "healthy"
    elif vault.fee_pool_balance >= profile.min_fee_pool:
        fee_status = "low"
    else:
        fee_status = "critical"

    return VaultBalanceResponse(
        sol_balance=round(sol_human, 9),
        sol_balance_usd=round(sol_human * SOL_PRICE_USD, 2),
        usdc_balance=round(usdc_human, 6),
        usdc_balance_usd=round(usdc_human, 2),
        fee_pool_balance=round(fee_human, 9),
        fee_pool_balance_usd=round(fee_human * SOL_PRICE_USD, 2),
        fee_pool_status=fee_status,
    )


@router.post("/{token}/deposit", response_model=DepositWithdrawResponse)
async def deposit(
    token: str,
    request: DepositWithdrawRequest,
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> DepositWithdrawResponse:
    vault_repo = VaultRepository(db)
    await vault_repo.get_or_create(wallet)

    if token == "sol":
        delta = sol_to_lamports(request.amount)
        await vault_repo.adjust_sol_balance(wallet, delta)
        vault = await vault_repo.get_by_owner(wallet)
        return DepositWithdrawResponse(
            success=True, new_balance=lamports_to_sol(vault.sol_balance), token="SOL"
        )
    elif token == "usdc":
        delta = usdc_human_to_base(request.amount)
        await vault_repo.adjust_usdc_balance(wallet, delta)
        vault = await vault_repo.get_by_owner(wallet)
        return DepositWithdrawResponse(
            success=True, new_balance=usdc_base_to_human(vault.usdc_balance), token="USDC"
        )
    elif token == "fee":
        delta = sol_to_lamports(request.amount)
        await vault_repo.adjust_fee_pool_balance(wallet, delta)
        vault = await vault_repo.get_by_owner(wallet)
        return DepositWithdrawResponse(
            success=True, new_balance=lamports_to_sol(vault.fee_pool_balance), token="FEE"
        )
    else:
        raise ValidationError(f"Invalid token: {token}. Must be sol, usdc, or fee")


@router.post("/{token}/withdraw", response_model=DepositWithdrawResponse)
async def withdraw(
    token: str,
    request: DepositWithdrawRequest,
    wallet: str = Depends(get_current_user_wallet),
    db: AsyncSession = Depends(get_db_session),
) -> DepositWithdrawResponse:
    vault_repo = VaultRepository(db)
    vault = await vault_repo.get_or_create(wallet)

    if token == "sol":
        delta = sol_to_lamports(request.amount)
        if vault.sol_balance < delta:
            raise InsufficientBalanceError("Insufficient SOL balance")
        await vault_repo.adjust_sol_balance(wallet, -delta)
        vault = await vault_repo.get_by_owner(wallet)
        return DepositWithdrawResponse(
            success=True, new_balance=lamports_to_sol(vault.sol_balance), token="SOL"
        )
    elif token == "usdc":
        delta = usdc_human_to_base(request.amount)
        if vault.usdc_balance < delta:
            raise InsufficientBalanceError("Insufficient USDC balance")
        await vault_repo.adjust_usdc_balance(wallet, -delta)
        vault = await vault_repo.get_by_owner(wallet)
        return DepositWithdrawResponse(
            success=True, new_balance=usdc_base_to_human(vault.usdc_balance), token="USDC"
        )
    elif token == "fee":
        delta = sol_to_lamports(request.amount)
        if vault.fee_pool_balance < delta:
            raise InsufficientBalanceError("Insufficient fee pool balance")
        await vault_repo.adjust_fee_pool_balance(wallet, -delta)
        vault = await vault_repo.get_by_owner(wallet)
        return DepositWithdrawResponse(
            success=True, new_balance=lamports_to_sol(vault.fee_pool_balance), token="FEE"
        )
    else:
        raise ValidationError(f"Invalid token: {token}. Must be sol, usdc, or fee")
