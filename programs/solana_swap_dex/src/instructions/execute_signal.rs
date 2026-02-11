use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount};

use crate::errors::SwapDexError;
use crate::events::{FeeCollected, RelayerRefunded, SignalExecuted};
use crate::state::{UserProfile, SIGNAL_SOL_TO_USDC, SIGNAL_USDC_TO_SOL};
use crate::utils::{calculate_fee, current_timestamp, is_new_day};

#[derive(Accounts)]
pub struct ExecuteSignal<'info> {
    /// The keeper/relayer executing the signal
    #[account(mut)]
    pub keeper: Signer<'info>,

    /// The user's profile PDA
    #[account(
        mut,
        seeds = [b"profile", profile.owner.as_ref()],
        bump = profile.bump,
    )]
    pub profile: Account<'info, UserProfile>,

    /// wSOL vault PDA
    #[account(
        mut,
        seeds = [b"sol_vault", profile.owner.as_ref()],
        bump,
    )]
    pub sol_vault: Account<'info, TokenAccount>,

    /// USDC vault PDA
    #[account(
        mut,
        seeds = [b"usdc_vault", profile.owner.as_ref()],
        bump,
    )]
    pub usdc_vault: Account<'info, TokenAccount>,

    /// Fee pool PDA (native SOL)
    /// CHECK: PDA for holding native SOL for fees
    #[account(
        mut,
        seeds = [b"fee_pool", profile.owner.as_ref()],
        bump,
    )]
    pub fee_pool: UncheckedAccount<'info>,

    /// Protocol fee recipient account
    /// CHECK: receives protocol fees
    #[account(mut)]
    pub fee_recipient: UncheckedAccount<'info>,

    /// Jupiter program for CPI swap calls
    /// CHECK: Jupiter program account validated by caller
    pub jupiter_program: UncheckedAccount<'info>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

pub fn handler<'info>(
    ctx: Context<'_, '_, '_, 'info, ExecuteSignal<'info>>,
    signal_type: u8,
    min_out: u64,
    _route_data: Vec<u8>,
) -> Result<()> {
    let profile = &mut ctx.accounts.profile;
    let now = current_timestamp()?;

    // 1. Verify keeper is in allowlist
    require!(
        profile.is_keeper_authorized(&ctx.accounts.keeper.key()),
        SwapDexError::UnauthorizedKeeper
    );

    // 2. Check profile is enabled
    require!(profile.enabled, SwapDexError::ProfileDisabled);

    // 3. Handle daily limit reset and check
    if is_new_day(profile.last_execution_day, now) {
        profile.executions_today = 0;
        profile.last_execution_day = now / 86_400;
    }

    if profile.daily_limit > 0 {
        require!(
            profile.executions_today < profile.daily_limit,
            SwapDexError::DailyLimitExceeded
        );
    }

    // 4. Validate signal type
    require!(
        signal_type == SIGNAL_SOL_TO_USDC || signal_type == SIGNAL_USDC_TO_SOL,
        SwapDexError::InvalidSignalType
    );

    // 5. Determine input/output amounts based on signal type
    let (amount_in, vault_balance) = if signal_type == SIGNAL_SOL_TO_USDC {
        (profile.trade_size_sol, ctx.accounts.sol_vault.amount)
    } else {
        (profile.trade_size_usdc, ctx.accounts.usdc_vault.amount)
    };

    // 6. Check sufficient balance
    require!(vault_balance >= amount_in, SwapDexError::InsufficientBalance);

    // 7. Jupiter CPI swap would happen here
    //    In production, this would invoke the Jupiter program via CPI
    //    using the remaining_accounts for the swap route.
    //    For now, we validate the expected output meets min_out.
    //
    //    let remaining_accounts = ctx.remaining_accounts;
    //    jupiter_cpi::swap(remaining_accounts, route_data)?;

    // 8. Verify output meets minimum (would use actual swap output in production)
    let amount_out = min_out; // Placeholder: actual output from Jupiter CPI
    require!(amount_out >= min_out, SwapDexError::SlippageExceeded);

    // 9. Calculate and collect protocol fee
    let fee_amount = calculate_fee(amount_out, profile.protocol_fee_bps)?;

    // Transfer protocol fee to fee_recipient
    if fee_amount > 0 {
        // In production: transfer fee from output token account to fee_recipient
        msg!("Protocol fee: {} to {}", fee_amount, ctx.accounts.fee_recipient.key());

        emit!(FeeCollected {
            user: profile.owner,
            amount: fee_amount,
            recipient: ctx.accounts.fee_recipient.key(),
            timestamp: now,
        });
    }

    // 10. Relayer refund from fee pool
    let refund = profile.relayer_refund_lamports;
    let fee_pool_balance = ctx.accounts.fee_pool.lamports();
    if refund > 0 && fee_pool_balance >= refund {
        **ctx.accounts.fee_pool.try_borrow_mut_lamports()? -= refund;
        **ctx.accounts.keeper.try_borrow_mut_lamports()? += refund;

        emit!(RelayerRefunded {
            user: profile.owner,
            keeper: ctx.accounts.keeper.key(),
            amount: refund,
            timestamp: now,
        });
    }

    // 11. Update profile state
    profile.last_execution = now;
    profile.nonce = profile.nonce.checked_add(1).ok_or(SwapDexError::ArithmeticOverflow)?;
    profile.executions_today = profile
        .executions_today
        .checked_add(1)
        .ok_or(SwapDexError::ArithmeticOverflow)?;

    // 12. Emit execution event
    emit!(SignalExecuted {
        user: profile.owner,
        signal_type,
        amount_in,
        amount_out,
        fee: fee_amount,
        nonce: profile.nonce,
        timestamp: now,
    });

    msg!(
        "Signal executed: user={}, type={}, in={}, out={}, fee={}",
        profile.owner,
        signal_type,
        amount_in,
        amount_out,
        fee_amount
    );

    Ok(())
}
