from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RoutePlanStep(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    swap_info: dict | None = None
    percent: int | None = None


class QuoteResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    input_mint: str
    in_amount: str
    output_mint: str
    out_amount: str
    other_amount_threshold: str
    swap_mode: str
    slippage_bps: int
    price_impact_pct: str
    route_plan: list[RoutePlanStep] = []
    context_slot: int | None = None
    time_taken: float | None = None


class SwapResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    swap_transaction: str  # base64 encoded transaction
    last_valid_block_height: int | None = None
    prioritization_fee_lamports: int | None = None
