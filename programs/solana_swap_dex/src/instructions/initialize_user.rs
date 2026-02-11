use anchor_lang::prelude::*;
use anchor_spl::token::{Mint, Token, TokenAccount};

use crate::events::DepositMade;
use crate::state::UserProfile;

/// wSOL mint address
pub const WSOL_MINT: &str = "So11111111111111111111111111111111111111112";
/// USDC mint address
pub const USDC_MINT: &str = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";

#[derive(Accounts)]
pub struct InitializeUser<'info> {
    #[account(mut)]
    pub user: Signer<'info>,

    #[account(
        init,
        payer = user,
        space = UserProfile::LEN,
        seeds = [b"profile", user.key().as_ref()],
        bump,
    )]
    pub profile: Account<'info, UserProfile>,

    /// wSOL vault PDA token account
    #[account(
        init,
        payer = user,
        token::mint = wsol_mint,
        token::authority = sol_vault,
        seeds = [b"sol_vault", user.key().as_ref()],
        bump,
    )]
    pub sol_vault: Account<'info, TokenAccount>,

    /// USDC vault PDA token account
    #[account(
        init,
        payer = user,
        token::mint = usdc_mint,
        token::authority = usdc_vault,
        seeds = [b"usdc_vault", user.key().as_ref()],
        bump,
    )]
    pub usdc_vault: Account<'info, TokenAccount>,

    /// Fee pool PDA (native SOL, just a system account)
    /// CHECK: This is a PDA used to hold native SOL for fee payments
    #[account(
        mut,
        seeds = [b"fee_pool", user.key().as_ref()],
        bump,
    )]
    pub fee_pool: UncheckedAccount<'info>,

    pub wsol_mint: Account<'info, Mint>,
    pub usdc_mint: Account<'info, Mint>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub rent: Sysvar<'info, Rent>,
}

pub fn handler(ctx: Context<InitializeUser>) -> Result<()> {
    let profile = &mut ctx.accounts.profile;
    let bump = ctx.bumps.profile;

    profile.owner = ctx.accounts.user.key();
    profile.enabled = true;
    profile.trade_size_sol = 2_500_000_000; // 2.5 SOL
    profile.trade_size_usdc = 500_000_000; // 500 USDC
    profile.min_fee_pool = 50_000_000; // 0.05 SOL
    profile.target_fee_pool = 150_000_000; // 0.15 SOL
    profile.max_slippage_bps = 50;
    profile.protocol_fee_bps = 10;
    profile.relayer_refund_lamports = 5_000;
    profile.keeper_allowlist = [Pubkey::default(); 5];
    profile.keeper_count = 0;
    profile.daily_limit = 10;
    profile.executions_today = 0;
    profile.last_execution_day = 0;
    profile.last_execution = 0;
    profile.nonce = 0;
    profile.bump = bump;

    msg!("User profile initialized: {}", ctx.accounts.user.key());

    emit!(DepositMade {
        user: ctx.accounts.user.key(),
        vault_type: "initialization".to_string(),
        amount: 0,
        timestamp: Clock::get()?.unix_timestamp,
    });

    Ok(())
}
