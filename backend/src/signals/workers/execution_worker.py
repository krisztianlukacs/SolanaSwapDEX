import asyncio
from datetime import datetime, timezone

from src.common.constants import (
    WSOL_MINT,
    USDC_MINT,
    SIGNAL_SOL_TO_USDC,
    SIGNAL_USDC_TO_SOL,
    TX_PENDING,
    TX_CONFIRMED,
    TX_FAILED,
)
from src.common.logging import setup_logger
from src.db.base import async_session_factory
from src.db.repositories.transaction_repo import TransactionRepository
from src.db.repositories.user_repo import UserRepository
from src.db.repositories.vault_repo import VaultRepository
from src.jupiter.route_builder import get_quote, validate_route, build_swap_transaction

logger = setup_logger("signals")


def execute_for_user(signal_id: int, signal_type: str, owner: str) -> None:
    """Entry point for RQ execution worker."""
    asyncio.run(_execute_for_user_async(signal_id, signal_type, owner))


async def _execute_for_user_async(signal_id: int, signal_type: str, owner: str) -> None:
    """Build Jupiter route and prepare transaction for a single user."""
    logger.info("Executing signal %d for user %s type=%s", signal_id, owner, signal_type)

    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        vault_repo = VaultRepository(session)
        tx_repo = TransactionRepository(session)

        profile = await user_repo.get_by_owner(owner)
        if not profile:
            logger.error("User %s not found", owner)
            return

        vault = await vault_repo.get_by_owner(owner)
        if not vault:
            logger.error("Vault for user %s not found", owner)
            return

        # Determine swap parameters
        if signal_type == SIGNAL_SOL_TO_USDC:
            input_mint = WSOL_MINT
            output_mint = USDC_MINT
            amount = profile.trade_size_sol
            if vault.sol_balance < amount:
                logger.warning("User %s: insufficient SOL balance", owner)
                return
        elif signal_type == SIGNAL_USDC_TO_SOL:
            input_mint = USDC_MINT
            output_mint = WSOL_MINT
            amount = profile.trade_size_usdc
            if vault.usdc_balance < amount:
                logger.warning("User %s: insufficient USDC balance", owner)
                return
        else:
            logger.error("Invalid signal type: %s", signal_type)
            return

        # Create pending transaction
        tx = await tx_repo.create(
            owner=owner,
            date=datetime.now(timezone.utc),
            type=signal_type,
            amount_in=amount,
            amount_out=0,
            token_in=input_mint,
            token_out=output_mint,
            slippage_bps=profile.max_slippage_bps,
            fee=0,
            status=TX_PENDING,
        )
        await session.commit()

        try:
            # Get Jupiter quote
            quote = await get_quote(
                input_mint, output_mint, amount, profile.max_slippage_bps
            )

            # Validate route
            validate_route(quote, profile.max_slippage_bps)

            # Build swap transaction
            swap = await build_swap_transaction(quote, owner)

            # Update transaction with quote results
            tx.amount_out = int(quote.out_amount)
            tx.status = TX_CONFIRMED

            # Update vault balances
            if signal_type == SIGNAL_SOL_TO_USDC:
                await vault_repo.adjust_sol_balance(owner, -amount)
                await vault_repo.adjust_usdc_balance(owner, int(quote.out_amount))
            else:
                await vault_repo.adjust_usdc_balance(owner, -amount)
                await vault_repo.adjust_sol_balance(owner, int(quote.out_amount))

            # Update last execution
            await user_repo.update_last_execution(owner, datetime.now(timezone.utc))

            await session.commit()
            logger.info(
                "Signal %d executed for user %s: %s -> %s (tx=%s)",
                signal_id,
                owner,
                quote.in_amount,
                quote.out_amount,
                swap.swap_transaction[:20],
            )

        except Exception as e:
            logger.error("Execution failed for user %s: %s", owner, str(e))
            await tx_repo.update_status(tx.id, TX_FAILED, error_message=str(e))
            await session.commit()
