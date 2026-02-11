use anchor_lang::prelude::*;

use crate::state::{UserProfile, MAX_KEEPERS};

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct UpdateProfileParams {
    pub enabled: Option<bool>,
    pub trade_size_sol: Option<u64>,
    pub trade_size_usdc: Option<u64>,
    pub min_fee_pool: Option<u64>,
    pub target_fee_pool: Option<u64>,
    pub max_slippage_bps: Option<u16>,
    pub relayer_refund_lamports: Option<u64>,
    pub keeper_allowlist: Option<Vec<Pubkey>>,
    pub daily_limit: Option<u16>,
}

#[derive(Accounts)]
pub struct UpdateProfile<'info> {
    #[account(mut)]
    pub user: Signer<'info>,

    #[account(
        mut,
        seeds = [b"profile", user.key().as_ref()],
        bump = profile.bump,
        has_one = owner @ crate::errors::SwapDexError::UnauthorizedKeeper,
    )]
    pub profile: Account<'info, UserProfile>,

    /// CHECK: validated via has_one
    pub owner: UncheckedAccount<'info>,
}

pub fn handler(ctx: Context<UpdateProfile>, params: UpdateProfileParams) -> Result<()> {
    let profile = &mut ctx.accounts.profile;

    if let Some(enabled) = params.enabled {
        profile.enabled = enabled;
    }
    if let Some(trade_size_sol) = params.trade_size_sol {
        profile.trade_size_sol = trade_size_sol;
    }
    if let Some(trade_size_usdc) = params.trade_size_usdc {
        profile.trade_size_usdc = trade_size_usdc;
    }
    if let Some(min_fee_pool) = params.min_fee_pool {
        profile.min_fee_pool = min_fee_pool;
    }
    if let Some(target_fee_pool) = params.target_fee_pool {
        profile.target_fee_pool = target_fee_pool;
    }
    if let Some(max_slippage_bps) = params.max_slippage_bps {
        profile.max_slippage_bps = max_slippage_bps;
    }
    if let Some(relayer_refund_lamports) = params.relayer_refund_lamports {
        profile.relayer_refund_lamports = relayer_refund_lamports;
    }
    if let Some(keeper_list) = params.keeper_allowlist {
        let count = keeper_list.len().min(MAX_KEEPERS);
        let mut new_list = [Pubkey::default(); MAX_KEEPERS];
        for (i, key) in keeper_list.iter().take(count).enumerate() {
            new_list[i] = *key;
        }
        profile.keeper_allowlist = new_list;
        profile.keeper_count = count as u8;
    }
    if let Some(daily_limit) = params.daily_limit {
        profile.daily_limit = daily_limit;
    }

    msg!("Profile updated for user: {}", profile.owner);

    Ok(())
}
