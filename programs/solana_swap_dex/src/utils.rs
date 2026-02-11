use anchor_lang::prelude::*;

use crate::errors::SwapDexError;

/// Calculate protocol fee: amount * fee_bps / 10000
pub fn calculate_fee(amount: u64, fee_bps: u16) -> Result<u64> {
    let fee = (amount as u128)
        .checked_mul(fee_bps as u128)
        .ok_or(SwapDexError::ArithmeticOverflow)?
        .checked_div(10_000)
        .ok_or(SwapDexError::ArithmeticOverflow)? as u64;
    Ok(fee)
}

/// Get current unix timestamp from Clock sysvar
pub fn current_timestamp() -> Result<i64> {
    let clock = Clock::get()?;
    Ok(clock.unix_timestamp)
}

/// Check if a new day has started (UTC-based)
pub fn is_new_day(last_timestamp: i64, current_timestamp: i64) -> bool {
    let last_day = last_timestamp / 86_400;
    let current_day = current_timestamp / 86_400;
    current_day > last_day
}
