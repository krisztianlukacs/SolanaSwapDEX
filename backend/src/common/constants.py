# Solana token mints
WSOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Conversion factors
LAMPORTS_PER_SOL = 1_000_000_000
USDC_BASE_UNITS = 1_000_000  # USDC has 6 decimals

# Signal types
SIGNAL_SOL_TO_USDC = "SOL_TO_USDC"
SIGNAL_USDC_TO_SOL = "USDC_TO_SOL"

# Transaction statuses
TX_CONFIRMED = "confirmed"
TX_PENDING = "pending"
TX_FAILED = "failed"

# Signal log statuses
SIGNAL_RECEIVED = "received"
SIGNAL_PROCESSING = "processing"
SIGNAL_COMPLETED = "completed"
SIGNAL_FAILED = "failed"

# Default profile values
DEFAULT_TRADE_SIZE_SOL = 2_500_000_000  # 2.5 SOL
DEFAULT_TRADE_SIZE_USDC = 500_000_000  # 500 USDC
DEFAULT_MIN_FEE_POOL = 50_000_000  # 0.05 SOL
DEFAULT_TARGET_FEE_POOL = 150_000_000  # 0.15 SOL
DEFAULT_MAX_SLIPPAGE_BPS = 50
DEFAULT_PROTOCOL_FEE_BPS = 10
DEFAULT_RELAYER_REFUND = 5_000  # lamports
DEFAULT_DAILY_LIMIT = 10


def lamports_to_sol(lamports: int) -> float:
    return lamports / LAMPORTS_PER_SOL


def sol_to_lamports(sol: float) -> int:
    return int(sol * LAMPORTS_PER_SOL)


def usdc_base_to_human(base_units: int) -> float:
    return base_units / USDC_BASE_UNITS


def usdc_human_to_base(human: float) -> int:
    return int(human * USDC_BASE_UNITS)
