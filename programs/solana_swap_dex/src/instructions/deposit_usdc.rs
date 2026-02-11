use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

use crate::errors::SwapDexError;
use crate::events::DepositMade;
use crate::state::UserProfile;

#[derive(Accounts)]
pub struct DepositUsdc<'info> {
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

    /// User's USDC token account (source)
    #[account(mut)]
    pub user_usdc_account: Account<'info, TokenAccount>,

    /// Program's USDC vault PDA (destination)
    #[account(
        mut,
        seeds = [b"usdc_vault", user.key().as_ref()],
        bump,
    )]
    pub usdc_vault: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<DepositUsdc>, amount: u64) -> Result<()> {
    require!(amount > 0, SwapDexError::InsufficientBalance);

    let cpi_accounts = Transfer {
        from: ctx.accounts.user_usdc_account.to_account_info(),
        to: ctx.accounts.usdc_vault.to_account_info(),
        authority: ctx.accounts.user.to_account_info(),
    };
    let cpi_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), cpi_accounts);
    token::transfer(cpi_ctx, amount)?;

    msg!("Deposited {} USDC base units for user {}", amount, ctx.accounts.user.key());

    emit!(DepositMade {
        user: ctx.accounts.user.key(),
        vault_type: "usdc".to_string(),
        amount,
        timestamp: Clock::get()?.unix_timestamp,
    });

    Ok(())
}
