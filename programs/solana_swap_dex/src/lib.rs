use anchor_lang::prelude::*;

pub mod errors;
pub mod events;
pub mod instructions;
pub mod state;
pub mod utils;

use instructions::*;

declare_id!("DEXSwp1111111111111111111111111111111111111");

#[program]
pub mod solana_swap_dex {
    use super::*;

    pub fn initialize_user(ctx: Context<InitializeUser>) -> Result<()> {
        instructions::initialize_user::handler(ctx)
    }

    pub fn update_profile(ctx: Context<UpdateProfile>, params: UpdateProfileParams) -> Result<()> {
        instructions::update_profile::handler(ctx, params)
    }

    pub fn deposit_sol(ctx: Context<DepositSol>, amount: u64) -> Result<()> {
        instructions::deposit_sol::handler(ctx, amount)
    }

    pub fn withdraw_sol(ctx: Context<WithdrawSol>, amount: u64) -> Result<()> {
        instructions::withdraw_sol::handler(ctx, amount)
    }

    pub fn deposit_usdc(ctx: Context<DepositUsdc>, amount: u64) -> Result<()> {
        instructions::deposit_usdc::handler(ctx, amount)
    }

    pub fn withdraw_usdc(ctx: Context<WithdrawUsdc>, amount: u64) -> Result<()> {
        instructions::withdraw_usdc::handler(ctx, amount)
    }

    pub fn deposit_fee(ctx: Context<DepositFee>, amount: u64) -> Result<()> {
        instructions::deposit_fee::handler(ctx, amount)
    }

    pub fn withdraw_fee(ctx: Context<WithdrawFee>, amount: u64) -> Result<()> {
        instructions::withdraw_fee::handler(ctx, amount)
    }

    pub fn execute_signal<'info>(
        ctx: Context<'_, '_, '_, 'info, ExecuteSignal<'info>>,
        signal_type: u8,
        min_out: u64,
        route_data: Vec<u8>,
    ) -> Result<()> {
        instructions::execute_signal::handler(ctx, signal_type, min_out, route_data)
    }
}
