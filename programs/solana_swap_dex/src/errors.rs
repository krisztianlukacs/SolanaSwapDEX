use anchor_lang::prelude::*;

#[error_code]
pub enum SwapDexError {
    #[msg("Profile is disabled")]
    ProfileDisabled,

    #[msg("Unauthorized keeper")]
    UnauthorizedKeeper,

    #[msg("Daily execution limit exceeded")]
    DailyLimitExceeded,

    #[msg("Insufficient balance")]
    InsufficientBalance,

    #[msg("Insufficient fee pool balance")]
    InsufficientFeePool,

    #[msg("Slippage exceeded maximum allowed")]
    SlippageExceeded,

    #[msg("Invalid signal type")]
    InvalidSignalType,

    #[msg("Cooldown period is still active")]
    CooldownActive,

    #[msg("Invalid token mint")]
    InvalidMint,

    #[msg("Arithmetic overflow")]
    ArithmeticOverflow,
}
