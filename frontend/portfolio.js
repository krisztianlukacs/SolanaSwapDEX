// Portfolio / Vault Management

const Portfolio = {
    init() {
        this.render();
    },

    render() {
        const container = document.getElementById('portfolioGrid');
        const solVault = MockData.vaults.sol;
        const usdcVault = MockData.vaults.usdc;
        const feePool = MockData.vaults.feePool;
        const totalUsd = MockData.portfolio.totalValueUsd;

        const solPct = ((solVault.usdValue / totalUsd) * 100).toFixed(1);
        const usdcPct = ((usdcVault.usdValue / totalUsd) * 100).toFixed(1);

        // Fee pool progress
        const feeMax = feePool.targetThreshold;
        const feePct = Math.min((feePool.balance / feeMax) * 100, 100);
        const minPct = (feePool.minThreshold / feeMax) * 100;

        let feeColor = 'var(--accent-green)';
        if (feePool.balance < feePool.minThreshold) feeColor = 'var(--accent-red)';
        else if (feePool.balance < feePool.targetThreshold) feeColor = 'var(--accent-yellow)';

        container.innerHTML = `
            <!-- SOL Vault -->
            <div class="vault-card">
                <div class="vault-card-header">
                    <div class="vault-token">
                        <div class="vault-token-icon sol">SOL</div>
                        <div class="vault-token-name">SOL Vault</div>
                    </div>
                    <span class="vault-pct">${solPct}%</span>
                </div>
                <div class="vault-balance">${App.formatNumber(solVault.balance, 4)} SOL</div>
                <div class="vault-usd">${App.formatUsd(solVault.usdValue)}</div>
                <div class="vault-actions">
                    <button class="btn btn-primary" onclick="Portfolio.openModal('SOL', 'deposit')">Deposit</button>
                    <button class="btn btn-secondary" onclick="Portfolio.openModal('SOL', 'withdraw')">Withdraw</button>
                </div>
            </div>

            <!-- USDC Vault -->
            <div class="vault-card">
                <div class="vault-card-header">
                    <div class="vault-token">
                        <div class="vault-token-icon usdc">USDC</div>
                        <div class="vault-token-name">USDC Vault</div>
                    </div>
                    <span class="vault-pct">${usdcPct}%</span>
                </div>
                <div class="vault-balance">${App.formatNumber(usdcVault.balance, 2)} USDC</div>
                <div class="vault-usd">${App.formatUsd(usdcVault.usdValue)}</div>
                <div class="vault-actions">
                    <button class="btn btn-primary" onclick="Portfolio.openModal('USDC', 'deposit')">Deposit</button>
                    <button class="btn btn-secondary" onclick="Portfolio.openModal('USDC', 'withdraw')">Withdraw</button>
                </div>
            </div>

            <!-- Fee Pool -->
            <div class="vault-card">
                <div class="vault-card-header">
                    <div class="vault-token">
                        <div class="vault-token-icon fee">FEE</div>
                        <div class="vault-token-name">Fee Pool</div>
                    </div>
                </div>
                <div class="vault-balance">${App.formatNumber(feePool.balance, 4)} SOL</div>
                <div class="vault-usd">${App.formatUsd(feePool.balance * MockData.vaults.sol.usdPrice)}</div>

                <div class="fee-progress-wrapper">
                    <div class="fee-progress-labels">
                        <span>0 SOL</span>
                        <span>Min: ${feePool.minThreshold} SOL</span>
                        <span>Target: ${feePool.targetThreshold} SOL</span>
                    </div>
                    <div class="fee-progress-bar">
                        <div class="fee-progress-fill" style="width:${feePct}%; background:${feeColor}"></div>
                        <div class="fee-progress-marker" style="left:${minPct}%" title="Min threshold"></div>
                    </div>
                </div>

                <div class="vault-actions">
                    <button class="btn btn-success" onclick="Portfolio.openModal('SOL', 'deposit', true)">Top Up Fee Pool</button>
                </div>
            </div>
        `;
    },

    openModal(token, action, isFeePool = false) {
        const isDeposit = action === 'deposit';
        const title = isFeePool ? 'Top Up Fee Pool'
            : `${isDeposit ? 'Deposit' : 'Withdraw'} ${token}`;

        const balance = token === 'SOL'
            ? MockData.vaults.sol.balance
            : MockData.vaults.usdc.balance;

        const maxAmount = isDeposit ? 100 : balance;
        const decimals = token === 'SOL' ? 4 : 2;

        App.showModal(`
            <h2 class="modal-title">${title}</h2>
            <div class="modal-body">
                <p style="color:var(--text-secondary); margin-bottom:4px;">
                    ${isDeposit ? 'Enter amount to deposit' : 'Enter amount to withdraw'}
                </p>
                <div class="balance-display">
                    Available: ${App.formatNumber(balance, decimals)} ${token}
                </div>
                <div class="amount-input-wrapper">
                    <input type="number" id="modalAmount" placeholder="0.00" step="any" min="0" max="${maxAmount}">
                    <button class="max-btn" onclick="document.getElementById('modalAmount').value='${isDeposit ? '' : balance}'">MAX</button>
                </div>
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn ${isDeposit ? 'btn-primary' : 'btn-danger'}" id="modalConfirmBtn">
                    ${isDeposit ? 'Deposit' : 'Withdraw'}
                </button>
            </div>
        `);

        document.getElementById('modalConfirmBtn').addEventListener('click', () => {
            const amount = parseFloat(document.getElementById('modalAmount').value);
            if (!amount || amount <= 0) {
                App.toast('Please enter a valid amount', 'error');
                return;
            }
            this.simulateTransaction(token, action, amount, isFeePool);
        });
    },

    simulateTransaction(token, action, amount, isFeePool) {
        const modal = document.getElementById('modalContent');
        modal.innerHTML = `
            <h2 class="modal-title">Processing...</h2>
            <div class="modal-body" style="text-align:center; padding:24px 0;">
                <div class="strategy-dot" style="width:24px;height:24px;margin:0 auto 12px;background:var(--accent-purple);"></div>
                <p style="color:var(--text-secondary);">Confirming transaction on Solana...</p>
            </div>
        `;

        setTimeout(() => {
            App.closeModal();
            const label = isFeePool ? 'Fee pool topped up' : `${action === 'deposit' ? 'Deposited' : 'Withdrew'} ${App.formatNumber(amount)} ${token}`;
            App.toast(`${label} successfully`, 'success');
        }, 1500);
    },
};
