use anchor_lang::prelude::*;

use crate::errors::SwapDexError;
use crate::events::WithdrawalMade;
use crate::state::UserProfile;

#[derive(Accounts)]
pub struct WithdrawFee<'info> {
    #[account(mut)]
    pub user: Signer<'info>,

    #[account(
        seeds = [b"profile", user.key().as_ref()],
        bump = profile.bump,
        has_one = owner,
    )]
    pub profile: Account<'info, UserProfile>,

    /// CHECK: validated via has_one
    pub owner: UncheckedAccount<'info>,

    /// Fee pool PDA (native SOL)
    /// CHECK: PDA for holding native SOL
    #[account(
        mut,
        seeds = [b"fee_pool", user.key().as_ref()],
        bump,
    )]
    pub fee_pool: UncheckedAccount<'info>,
}

pub fn handler(ctx: Context<WithdrawFee>, amount: u64) -> Result<()> {
    require!(amount > 0, SwapDexError::InsufficientBalance);

    let fee_pool_balance = ctx.accounts.fee_pool.lamports();
    let rent = Rent::get()?;
    let min_rent = rent.minimum_balance(0);
    let available = fee_pool_balance.saturating_sub(min_rent);

    require!(available >= amount, SwapDexError::InsufficientFeePool);

    // Transfer native SOL from fee pool PDA to user
    // Since the fee_pool is a PDA, we transfer lamports directly
    **ctx.accounts.fee_pool.try_borrow_mut_lamports()? -= amount;
    **ctx.accounts.user.try_borrow_mut_lamports()? += amount;

    msg!("Withdrew {} lamports from fee pool for user {}", amount, ctx.accounts.user.key());

    emit!(WithdrawalMade {
        user: ctx.accounts.user.key(),
        vault_type: "fee".to_string(),
        amount,
        timestamp: Clock::get()?.unix_timestamp,
    });

    Ok(())
}
