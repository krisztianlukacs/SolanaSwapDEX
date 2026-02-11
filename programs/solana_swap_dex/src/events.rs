use anchor_lang::prelude::*;

#[event]
pub struct SignalExecuted {
    pub user: Pubkey,
    pub signal_type: u8,
    pub amount_in: u64,
    pub amount_out: u64,
    pub fee: u64,
    pub nonce: u64,
    pub timestamp: i64,
}

#[event]
pub struct DepositMade {
    pub user: Pubkey,
    pub vault_type: String,
    pub amount: u64,
    pub timestamp: i64,
}

#[event]
pub struct WithdrawalMade {
    pub user: Pubkey,
    pub vault_type: String,
    pub amount: u64,
    pub timestamp: i64,
}

#[event]
pub struct FeeCollected {
    pub user: Pubkey,
    pub amount: u64,
    pub recipient: Pubkey,
    pub timestamp: i64,
}

#[event]
pub struct RelayerRefunded {
    pub user: Pubkey,
    pub keeper: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
}
