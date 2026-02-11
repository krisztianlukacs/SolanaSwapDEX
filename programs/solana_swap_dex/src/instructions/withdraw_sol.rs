use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

use crate::errors::SwapDexError;
use crate::events::WithdrawalMade;
use crate::state::UserProfile;

#[derive(Accounts)]
pub struct WithdrawSol<'info> {
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

    /// Program's SOL vault PDA (source)
    #[account(
        mut,
        seeds = [b"sol_vault", user.key().as_ref()],
        bump,
    )]
    pub sol_vault: Account<'info, TokenAccount>,

    /// User's wSOL token account (destination)
    #[account(mut)]
    pub user_sol_account: Account<'info, TokenAccount>,

    pub token_program: Program<'info, Token>,
}

pub fn handler(ctx: Context<WithdrawSol>, amount: u64) -> Result<()> {
    require!(amount > 0, SwapDexError::InsufficientBalance);
    require!(
        ctx.accounts.sol_vault.amount >= amount,
        SwapDexError::InsufficientBalance
    );

    let user_key = ctx.accounts.user.key();
    let seeds = &[
        b"sol_vault",
        user_key.as_ref(),
        &[ctx.bumps.sol_vault],
    ];
    let signer_seeds = &[&seeds[..]];

    let cpi_accounts = Transfer {
        from: ctx.accounts.sol_vault.to_account_info(),
        to: ctx.accounts.user_sol_account.to_account_info(),
        authority: ctx.accounts.sol_vault.to_account_info(),
    };
    let cpi_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        cpi_accounts,
        signer_seeds,
    );
    token::transfer(cpi_ctx, amount)?;

    msg!("Withdrew {} lamports SOL for user {}", amount, ctx.accounts.user.key());

    emit!(WithdrawalMade {
        user: ctx.accounts.user.key(),
        vault_type: "sol".to_string(),
        amount,
        timestamp: Clock::get()?.unix_timestamp,
    });

    Ok(())
}
