# Frontend (Web)

Static single-page application (HTML + CSS + JS) with mock data. Open `frontend/index.html` in any browser - no server required.

## Architecture

- **SPA with hash-based routing** (`#dashboard`, `#portfolio`, `#transactions`, `#settings`)
- **Dark DeFi theme** with CSS custom properties and responsive breakpoints
- **Chart.js** loaded from CDN for data visualization
- **Mock data** simulates real wallet balances, PnL history, and transaction records
- **localStorage** persists wallet connection state across sessions

## File Structure

```
frontend/
├── index.html          # SPA shell: sidebar, topbar, page sections, modals
├── styles.css          # Full dark theme CSS with responsive grid layout
├── app.js              # Router, state management, toast/modal systems, formatters
├── mock-data.js        # Generated mock data (user, vaults, 90d PnL, 55 transactions)
├── charts.js           # Chart.js configs (PnL line, allocation doughnut, volume bars)
├── wallet.js           # Wallet connect/disconnect simulation with modal
├── dashboard.js        # Metric cards, strategy status, chart initialization
├── portfolio.js        # Vault cards with deposit/withdraw modals
├── transactions.js     # Transaction table with filters, sorting, pagination, CSV export
├── settings.js         # Settings form with live hints, toggle, save simulation
└── logo.svg            # SVG logo
```

## Pages & Features

### Dashboard
- **6 metric cards**: Total Portfolio Value (24h change), SOL Vault, USDC Vault, Fee Pool (health status), All-Time PnL (% return), Last Execution (time ago)
- **PnL chart**: Line chart with gradient fill, time range toggles (7D / 30D / 90D / ALL)
- **Asset allocation**: Doughnut chart showing SOL vs USDC split with percentages
- **Trade volume**: Stacked bar chart grouped by swap direction (last 30 days)
- **Strategy status**: Current position, enabled/disabled state, last execution, next signal ETA

### Portfolio
- **SOL Vault card**: Balance in SOL + USD equivalent, % of portfolio, deposit/withdraw buttons
- **USDC Vault card**: Balance in USDC + USD equivalent, % of portfolio, deposit/withdraw buttons
- **Fee Pool card**: Balance with progress bar visualization (min threshold marker, color-coded health), top-up button
- **Deposit/Withdraw modal**: Amount input with MAX button, available balance display, simulated confirmation flow (1.5s processing animation + success toast)

### Transactions
- **Full transaction table**: Date, Type (color-coded SOL→USDC / USDC→SOL), Amount In, Amount Out, Slippage (bps), Fee, Status badge (confirmed/pending/failed), Tx Signature (truncated, links to Solscan)
- **Filters**: Type dropdown, Status dropdown, Date range (from/to)
- **Column sorting**: Click headers to sort ascending/descending
- **Pagination**: 10/25/50 per page with page navigation
- **CSV export**: Downloads filtered transaction data as CSV file

### Settings
- **Profile status**: Toggle switch with disable confirmation dialog
- **Trade size**: SOL input (shows lamports equivalent), USDC input
- **Fee pool**: Minimum balance, target balance (both in SOL)
- **Risk settings**: Max slippage (bps input, shows % equivalent), protocol fee (read-only), relayer refund (lamports)
- **Save/Reset buttons**: Simulated save with loading state + success toast

## Core Functionalities

### Wallet Connect
- "Connect Wallet" button in top bar opens modal with wallet options (Phantom, Solflare, Backpack)
- Selecting a wallet triggers simulated connection (1s delay) showing approval animation
- Connected state displays truncated address (`7xK3...9fPq`) with disconnect button
- Connection state persisted in localStorage across sessions

### User Settings
- Allow users to configure:
  - **Trade Size**: Set the desired trade size for SOL and USDC transactions
  - **Fee Pool Settings**: Define minimum and target balances for the fee pool
  - **Enable/Disable**: Toggle the profile's active status with confirmation
  - **Max Slippage**: Set maximum acceptable slippage in basis points
  - **Relayer Refund**: Configure refund amount per transaction in lamports

### Deposit/Withdraw UI
- Provide an intuitive interface for users to:
  - Deposit funds into their SOL or USDC vaults
  - Withdraw funds from their vaults
  - Top up the fee pool
  - View available balances and use MAX button for quick input
  - See processing animation and confirmation toasts

### Status Displays
- Show real-time information about:
  - **Vault Balances**: Current balances in SOL and USDC vaults with USD equivalents
  - **Fee Pool**: Balance with health indicator (healthy/low/critical) and progress bar
  - **Last Execution**: Timestamp with relative time display ("5m ago")
  - **PnL (Profit and Loss)**: Interactive charts with time range selection
  - **Strategy Status**: Current position, enabled state, and next signal ETA

## Responsive Design

- **Desktop** (>1024px): Full sidebar + multi-column grid layouts
- **Tablet** (768-1024px): Single-column charts, reduced grid columns
- **Mobile** (<768px): Collapsible sidebar (hamburger menu), stacked layouts, full-width cards

## Mock Data

- **User profile**: Wallet address, trade sizes, fee pool thresholds, slippage settings
- **Vault balances**: SOL (24.5 SOL), USDC (3,842.50 USDC), Fee Pool (0.085 SOL)
- **PnL history**: 90 days of generated daily PnL data (~11.5% monthly return pattern)
- **Transactions**: 55 mock transactions with realistic amounts, fees, slippage, and status distribution
