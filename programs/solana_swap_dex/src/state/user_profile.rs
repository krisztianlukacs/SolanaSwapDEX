use anchor_lang::prelude::*;

/// Signal types
pub const SIGNAL_SOL_TO_USDC: u8 = 0;
pub const SIGNAL_USDC_TO_SOL: u8 = 1;

/// Max keepers in allowlist
pub const MAX_KEEPERS: usize = 5;

/// UserProfile PDA: seeds = [b"profile", user.key()]
#[account]
pub struct UserProfile {
    /// Owner wallet address
    pub owner: Pubkey,
    /// Whether the profile is enabled for signal execution
    pub enabled: bool,
    /// Trade size for SOL->USDC swaps (in lamports)
    pub trade_size_sol: u64,
    /// Trade size for USDC->SOL swaps (in USDC base units)
    pub trade_size_usdc: u64,
    /// Minimum fee pool balance before top-up triggers (lamports)
    pub min_fee_pool: u64,
    /// Target fee pool balance after top-up (lamports)
    pub target_fee_pool: u64,
    /// Maximum allowed slippage in basis points
    pub max_slippage_bps: u16,
    /// Protocol fee in basis points
    pub protocol_fee_bps: u16,
    /// Lamports refunded to the keeper/relayer per execution
    pub relayer_refund_lamports: u64,
    /// Allowed keeper public keys (max 5)
    pub keeper_allowlist: [Pubkey; MAX_KEEPERS],
    /// Number of active keepers in the allowlist
    pub keeper_count: u8,
    /// Maximum executions per day (0 = unlimited)
    pub daily_limit: u16,
    /// Number of executions performed today
    pub executions_today: u16,
    /// Day (unix timestamp / 86400) of last execution — for daily reset
    pub last_execution_day: i64,
    /// Timestamp of last execution
    pub last_execution: i64,
    /// Monotonically increasing nonce
    pub nonce: u64,
    /// PDA bump seed
    pub bump: u8,
}

impl UserProfile {
    /// 8 (discriminator) + 32 + 1 + 8 + 8 + 8 + 8 + 2 + 2 + 8 + (32*5) + 1 + 2 + 2 + 8 + 8 + 8 + 1
    pub const LEN: usize = 8 + 32 + 1 + 8 + 8 + 8 + 8 + 2 + 2 + 8 + (32 * MAX_KEEPERS) + 1 + 2 + 2 + 8 + 8 + 8 + 1;

    pub fn is_keeper_authorized(&self, keeper: &Pubkey) -> bool {
        for i in 0..self.keeper_count as usize {
            if self.keeper_allowlist[i] == *keeper {
                return true;
            }
        }
        false
    }
}
