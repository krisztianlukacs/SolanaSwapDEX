# On-chain (Rust Program)

## Core Functionalities

### Program-Derived Addresses (PDAs)
- Define and manage PDAs for:
  - **Vaults**: Secure storage of user funds (SOL and USDC).
  - **Fee Pool**: Account for managing execution fees and refunds.
- Ensure PDAs are deterministic and derived securely to prevent unauthorized access.

### Vaults
- Implement vaults for:
  - **SOL (wSOL)**: Store wrapped SOL for user transactions.
  - **USDC**: Store USDC for swaps and liquidity management.
- Provide deposit and withdrawal mechanisms with proper validation.

### Permissions
- Enforce strict access controls:
  - Ensure only authorized entities (e.g., relayers, users) can interact with vaults and fee pools.
  - Validate signatures and ownership for all operations.

### Fee and Refund Handling
- Deduct protocol fees during transactions and transfer them to the designated fee recipient account.
- Process relayer refunds from the fee pool to incentivize execution.
- Maintain accurate accounting for all fee and refund operations.

### Jupiter CPI Calls
- Integrate with the Jupiter protocol via Cross-Program Invocations (CPIs):
  - Execute token swaps between SOL and USDC.
  - Pass necessary parameters such as routes, slippage, and minimum output values.
- Ensure CPI calls are optimized and adhere to Solana’s compute budget constraints.