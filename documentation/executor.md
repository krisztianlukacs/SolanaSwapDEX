# Relayer/Executor

## Core Functionalities

### Transaction Handling
- Assemble transactions for execution.
- Sign transactions securely.
- Submit transactions to the Solana blockchain.

### Retry Policy
- Implement robust retry mechanisms to handle:
  - **Blockhash Refresh**: Refresh blockhashes to ensure transactions remain valid.
  - **Transient RPC Errors**: Retry on temporary RPC failures to improve reliability.

### Fee Payer SOL Management
- Manage the SOL balance of the fee payer account.
- Handle user fee pool refunds and maintain accurate accounting for refunds.