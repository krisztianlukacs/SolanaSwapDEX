from unittest.mock import AsyncMock, patch

import pytest

from src.common.exceptions import SlippageExceededError
from src.jupiter.models import QuoteResponse
from src.jupiter.route_builder import validate_route, get_quote, build_swap_transaction
from src.jupiter.constants import WSOL_MINT, USDC_MINT


def _mock_quote(**overrides) -> QuoteResponse:
    defaults = {
        "input_mint": WSOL_MINT,
        "in_amount": "2500000000",
        "output_mint": USDC_MINT,
        "out_amount": "370000000",
        "other_amount_threshold": "368150000",
        "swap_mode": "ExactIn",
        "slippage_bps": 50,
        "price_impact_pct": "0.01",
        "route_plan": [],
    }
    defaults.update(overrides)
    return QuoteResponse(**defaults)


class TestValidateRoute:
    def test_valid_route(self):
        quote = _mock_quote()
        assert validate_route(quote, max_slippage_bps=50) is True

    def test_slippage_exceeded(self):
        # Threshold is very low relative to out_amount -> high slippage
        quote = _mock_quote(
            out_amount="1000000",
            other_amount_threshold="900000",  # 10% slippage = 1000 bps
        )
        with pytest.raises(SlippageExceededError):
            validate_route(quote, max_slippage_bps=50)

    def test_zero_output(self):
        quote = _mock_quote(out_amount="0", other_amount_threshold="0")
        assert validate_route(quote, max_slippage_bps=50) is False


@pytest.mark.asyncio
class TestGetQuote:
    @patch("src.jupiter.route_builder._client")
    async def test_get_quote_success(self, mock_client):
        mock_client.get = AsyncMock(
            return_value={
                "inputMint": WSOL_MINT,
                "inAmount": "2500000000",
                "outputMint": USDC_MINT,
                "outAmount": "370000000",
                "otherAmountThreshold": "368150000",
                "swapMode": "ExactIn",
                "slippageBps": 50,
                "priceImpactPct": "0.01",
                "routePlan": [],
            }
        )

        quote = await get_quote(WSOL_MINT, USDC_MINT, 2_500_000_000, 50)
        assert quote.in_amount == "2500000000"
        assert quote.out_amount == "370000000"


@pytest.mark.asyncio
class TestBuildSwapTransaction:
    @patch("src.jupiter.route_builder._client")
    async def test_build_swap(self, mock_client):
        mock_client.post = AsyncMock(
            return_value={
                "swapTransaction": "base64encodedtransaction==",
                "lastValidBlockHeight": 123456789,
            }
        )

        quote = _mock_quote()
        swap = await build_swap_transaction(quote, "7xK3mBf9rQvZ8nJp4sW2yL6hT1cX5dA8kF3gN9fPq")
        assert swap.swap_transaction == "base64encodedtransaction=="
