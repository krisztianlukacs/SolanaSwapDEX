# Concept Overview

This document outlines the core components and flow of a Solana-based strategy execution system for rotating between SOL and USDC based on market signals. The architecture is designed to be modular, with clear responsibilities for each block, enabling efficient execution and maintenance.

Users have two wallet amounts: SOL and USDC (or USDT). The algorithm can generate USDC profit from USDC holdings and generate SOL profit from SOL holdings.

From March 2025 to November 2025, we generated 11.5% monthly USDC profit on USDC AUM.
From November 2025 to February 2026, we generated 40% SOL profit on SOL AUM.

## 1. User Profile (Configuration & State)

**Role:** Per-user settings and state management. All other blocks read from this profile.

### Inputs for User Profile

- **owner**: The owner of the profile.
- **enabled**: Whether the profile is active.
- **trade_size_sol (lamports)**: The trade size in SOL, specified in lamports.
- **trade_size_usdc (base units)**: The trade size in USDC, specified in base units.
- **min_fee_pool, target_fee_pool (lamports)**: Minimum and target balances for the fee pool, in lamports.
- **max_slippage_bps**: Maximum allowable slippage, in basis points.
- **keeper_allowlist**: A list of allowed keepers (or a global keeper with an allowlist).
- **protocol_fee_bps**: Protocol fee, in basis points.
- **relayer_refund_lamports**: Fixed refund per transaction, in lamports.
- **(Optional)**: Daily limit, last execution timestamp, nonce.

### Outputs for User Profile

- No token movements; only data used during execution.

---

## 2. SOL Capital Vault (wSOL Vault)

**Role:** Manage the user’s SOL capital in a swap-compatible manner.

### Inputs for SOL Vault

- **deposit_sol**: Converts user SOL to wSOL and deposits it into the vault.
- **swap_out_wsol**: Receives wSOL when swapping USDC to wSOL.

### Outputs for SOL Vault

- **swap_in_wsol**: Sends wSOL out when swapping wSOL to USDC.
- **withdraw_sol**: Converts wSOL back to SOL and returns it to the user.

---

## 3. USDC Capital Vault (USDC Vault)

**Role:** Store the user’s USDC position during SOL↔USDC rotations.

### Inputs for USDC Vault

- **swap_out_usdc**: Receives USDC when swapping wSOL to USDC.
- **(Optional)**: **deposit_usdc**: Allows additional USDC deposits.

### Outputs for USDC Vault

- **swap_in_usdc**: Sends USDC out when swapping USDC to wSOL.
- **withdraw_usdc**: Returns USDC to the user.

---

## 4. Fee Pool (SOL Balance for Execution Costs)

**Role:** Maintain a SOL balance provided by the user to cover relayer costs without manual intervention.

### Inputs for Fee Pool

- **deposit_fee_sol**: User transfers SOL to the fee pool PDA.
- **auto_topup_from_usdc**: (Optional) Converts USDC to SOL for topping up the fee pool.

### Outputs for Fee Pool

- **relayer_refund**: Fixed lamports transferred to the relayer after each successful execution.

---

## 5. Top-Up Manager (Fee Pool Maintenance)

**Role:** Ensure the fee pool does not deplete.

### Trigger for Top-Up Manager

Runs before the `execute_signal` function.

### Inputs for Top-Up Manager

- **fee_pool_balance**: Current balance of the fee pool.
- **min_fee_pool, target_fee_pool**: Minimum and target balances for the fee pool.
- **usdc_vault_balance**: Current balance of the USDC vault.
- **Jupiter route (USDC→wSOL)**: Route and minimum output for the top-up swap.

### Outputs for Top-Up Manager

- **fee_pool_balance_increased**: Increases SOL lamports in the fee pool.
- **topup_skipped/failed**: Logs the result if the top-up is skipped or fails.

**Note:** If the user only deposits SOL, the top-up can still work because USDC can be generated after a SOL→USDC swap.

---

## 6. Jupiter Swap Engine (Swap Execution)

**Role:** Execute swaps between SOL and USDC.

### Inputs for Swap Engine

- **direction**:
  - **SOL_TO_USDC**: Defensive strategy when SOL is expected to fall.
  - **USDC_TO_SOL**: Offensive strategy when SOL is expected to rise.
- **amount_in**: Trade size from the profile (either `trade_size_sol` or `trade_size_usdc`).
- **min_out**: Minimum output to protect against slippage.
- **Jupiter route/account metas**: Generated off-chain.

### Outputs for Swap Engine

- Token movements between the two vaults:
  - **SOL_TO_USDC**: Decreases wSOL vault, increases USDC vault.
  - **USDC_TO_SOL**: Decreases USDC vault, increases wSOL vault.

---

## 7. Strategy Executor (Signal Handler)

**Role:** The single entry point called by the bot, chaining top-up, swap, fee, and refund steps.

### Inputs for Strategy Executor

- **signal_type**: Either `SOL_TO_USDC` or `USDC_TO_SOL`.
- **min_out**: Minimum output and Jupiter route.
- **user_profile**: User profile data.
- **vault accounts + fee pool account**: Relevant accounts for execution.

### Outputs for Strategy Executor

- Updated vault balances.
- Protocol fee payment.
- Relayer refund payment.
- Event/log for the backend.

### Gating/Checks for Strategy Executor (Critical)

- Keeper allowlist.
- Sufficient input balance (wSOL or USDC).
- Slippage/min_out validation.
- Profile enabled/limits.

---

## 8. Fee Collector (Protocol Revenue)

**Role:** Deduct and transfer volume-based fees to the protocol owner.

### Inputs for Fee Collector

- **protocol_fee_bps**: Protocol fee in basis points.
- **swap outcome**: Either input or output amount (configurable).

### Outputs for Fee Collector

- USDC or wSOL transfer to the fee recipient account.

**Recommendation:** Deduct fees from the output token for transparency and easier auditing.

---

## 9. Relayer Refund (Execution Incentive)

**Role:** Motivate and reimburse the relayer.

### Inputs for Relayer Refund

- **relayer_refund_lamports**: Fixed refund amount.
- **fee_pool_balance**: Current balance of the fee pool.

### Outputs for Relayer Refund

- SOL transfer to the relayer’s fee payer address.

**Why Fixed?** On Solana, fixed refunds are more stable and less exploitable than compute-based refunds.

---

## The Two Main Processes (SOL Yield Cycle)

### Flow A — Defensive: SOL → USDC

**When:** SOL is expected to fall versus USDC.

**Blocks:** Strategy Executor → (Top-Up Manager) → Jupiter Swap Engine → Fee Collector → Relayer Refund → Events.

**Input:** `trade_size_sol` in wSOL.

**Output:** Increased USDC in the USDC vault.

---

### Flow B — Offensive: USDC → SOL

**When:** Time to re-enter SOL.

**Blocks:** Strategy Executor → (Top-Up Manager) → Jupiter Swap Engine → Fee Collector → Relayer Refund → Events.

**Input:** `trade_size_usdc` in USDC.

**Output:** Increased wSOL in the wSOL vault (experienced by the user as SOL).
