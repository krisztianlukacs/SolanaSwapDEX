use anchor_lang::prelude::*;
use anchor_lang::system_program;

use crate::errors::SwapDexError;
use crate::events::DepositMade;
use crate::state::UserProfile;

#[derive(Accounts)]
pub struct DepositFee<'info> {
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

    pub system_program: Program<'info, System>,
}

pub fn handler(ctx: Context<DepositFee>, amount: u64) -> Result<()> {
    require!(amount > 0, SwapDexError::InsufficientBalance);

    // Transfer native SOL from user to fee pool PDA
    system_program::transfer(
        CpiContext::new(
            ctx.accounts.system_program.to_account_info(),
            system_program::Transfer {
                from: ctx.accounts.user.to_account_info(),
                to: ctx.accounts.fee_pool.to_account_info(),
            },
        ),
        amount,
    )?;

    msg!("Deposited {} lamports to fee pool for user {}", amount, ctx.accounts.user.key());

    emit!(DepositMade {
        user: ctx.accounts.user.key(),
        vault_type: "fee".to_string(),
        amount,
        timestamp: Clock::get()?.unix_timestamp,
    });

    Ok(())
}
