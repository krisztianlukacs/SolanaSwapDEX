from src.common.exceptions import SlippageExceededError
from src.common.logging import setup_logger
from src.jupiter.client import JupiterClient
from src.jupiter.constants import WSOL_MINT, USDC_MINT
from src.jupiter.models import QuoteResponse, SwapResponse

logger = setup_logger("jupiter")

_client = JupiterClient()


async def get_quote(
    input_mint: str,
    output_mint: str,
    amount: int,
    slippage_bps: int = 50,
) -> QuoteResponse:
    """Get a swap quote from Jupiter v6."""
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": str(amount),
        "slippageBps": slippage_bps,
    }

    data = await _client.get("/quote", params=params)
    quote = QuoteResponse(**data)

    logger.info(
        "Quote: %s -> %s | in=%s out=%s | slippage=%d bps",
        input_mint[:8],
        output_mint[:8],
        quote.in_amount,
        quote.out_amount,
        slippage_bps,
    )

    return quote


def validate_route(quote: QuoteResponse, max_slippage_bps: int) -> bool:
    """Validate that the route meets slippage requirements.

    Checks that other_amount_threshold (minimum output) is acceptable
    given the quoted out_amount and max allowed slippage.
    """
    out_amount = int(quote.out_amount)
    threshold = int(quote.other_amount_threshold)

    if out_amount == 0:
        return False

    actual_slippage_bps = ((out_amount - threshold) * 10000) // out_amount

    if actual_slippage_bps > max_slippage_bps:
        logger.warning(
            "Route slippage %d bps exceeds max %d bps",
            actual_slippage_bps,
            max_slippage_bps,
        )
        raise SlippageExceededError(
            f"Route slippage {actual_slippage_bps} bps exceeds max {max_slippage_bps} bps"
        )

    return True


async def build_swap_transaction(
    quote: QuoteResponse,
    user_pubkey: str,
) -> SwapResponse:
    """Build the swap transaction using Jupiter's /swap endpoint."""
    payload = {
        "quoteResponse": quote.model_dump(),
        "userPublicKey": user_pubkey,
        "wrapAndUnwrapSol": True,
    }

    data = await _client.post("/swap", json=payload)
    swap = SwapResponse(**data)

    logger.info("Swap transaction built for user %s", user_pubkey[:8])

    return swap


async def get_sol_to_usdc_route(
    amount_lamports: int,
    slippage_bps: int = 50,
) -> QuoteResponse:
    """Convenience: get SOL -> USDC quote."""
    return await get_quote(WSOL_MINT, USDC_MINT, amount_lamports, slippage_bps)


async def get_usdc_to_sol_route(
    amount_base_units: int,
    slippage_bps: int = 50,
) -> QuoteResponse:
    """Convenience: get USDC -> SOL quote."""
    return await get_quote(USDC_MINT, WSOL_MINT, amount_base_units, slippage_bps)
