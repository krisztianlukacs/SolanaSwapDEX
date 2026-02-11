// Dashboard Page Logic

const Dashboard = {
    init() {
        this.renderMetrics();
        this.renderStrategyStatus();
        Charts.init();
    },

    renderMetrics() {
        const container = document.getElementById('dashboardMetrics');
        const totalValue = MockData.portfolio.totalValueUsd;
        const solVault = MockData.vaults.sol;
        const usdcVault = MockData.vaults.usdc;
        const feePool = MockData.vaults.feePool;
        const pnl = MockData.portfolio;
        const lastExec = MockData.strategy.lastExecution;

        const feeStatus = feePool.balance >= feePool.targetThreshold ? 'healthy'
            : feePool.balance >= feePool.minThreshold ? 'low'
            : 'critical';

        const feeStatusColors = {
            healthy: 'var(--accent-green)',
            low: 'var(--accent-yellow)',
            critical: 'var(--accent-red)',
        };

        const metrics = [
            {
                label: 'Total Portfolio Value',
                value: App.formatUsd(totalValue),
                sub: `${pnl.change24h >= 0 ? '+' : ''}${pnl.change24h}% (24h)`,
                subClass: pnl.change24h >= 0 ? 'positive' : 'negative',
            },
            {
                label: 'SOL Vault',
                value: App.formatSol(solVault.balance),
                sub: App.formatUsd(solVault.usdValue),
                subClass: '',
            },
            {
                label: 'USDC Vault',
                value: App.formatUsdc(usdcVault.balance),
                sub: App.formatUsd(usdcVault.usdValue),
                subClass: '',
            },
            {
                label: 'Fee Pool',
                value: App.formatSol(feePool.balance),
                sub: `<span style="color:${feeStatusColors[feeStatus]}">${feeStatus.charAt(0).toUpperCase() + feeStatus.slice(1)}</span>`,
                subClass: '',
                rawSub: true,
            },
            {
                label: 'All-Time PnL',
                value: App.formatUsd(pnl.allTimePnl),
                sub: `+${pnl.allTimePnlPercent}% return`,
                subClass: 'positive',
                cardClass: 'total-pnl',
            },
            {
                label: 'SOL Profit',
                value: `${pnl.allTimeSolPnl.toLocaleString('en-US', { minimumFractionDigits: 4 })} SOL`,
                sub: `+${((pnl.allTimeSolPnl / 5) * 100).toFixed(1)}% return`,
                subClass: 'positive',
                cardClass: 'sol-pnl',
            },
            {
                label: 'USDC Profit',
                value: `${pnl.allTimeUsdcPnl.toLocaleString('en-US', { minimumFractionDigits: 2 })} USDC`,
                sub: `+${((pnl.allTimeUsdcPnl / 1200) * 100).toFixed(1)}% return`,
                subClass: 'positive',
                cardClass: 'usdc-pnl',
            },
            {
                label: 'Last Execution',
                value: App.timeAgo(lastExec),
                sub: App.formatDate(lastExec),
                subClass: '',
            },
        ];

        container.innerHTML = metrics.map(m => `
            <div class="metric-card${m.cardClass ? ' ' + m.cardClass : ''}">
                <div class="metric-label">${m.label}</div>
                <div class="metric-value">${m.value}</div>
                <div class="metric-sub ${m.subClass}">${m.sub}</div>
            </div>
        `).join('');
    },

    renderStrategyStatus() {
        const container = document.getElementById('strategyInfo');
        const s = MockData.strategy;

        const positionColors = {
            'SOL-heavy': 'var(--accent-purple)',
            'USDC-heavy': 'var(--accent-green)',
            'balanced': 'var(--accent-blue)',
        };

        container.innerHTML = `
            <div class="strategy-item">
                <span class="strategy-item-label">Current Position</span>
                <span class="strategy-item-value" style="color:${positionColors[s.currentPosition] || 'inherit'}">${s.currentPosition}</span>
            </div>
            <div class="strategy-item">
                <span class="strategy-item-label">Strategy</span>
                <span class="strategy-item-value" style="color:${s.enabled ? 'var(--accent-green)' : 'var(--accent-red)'}">${s.enabled ? 'Enabled' : 'Disabled'}</span>
            </div>
            <div class="strategy-item">
                <span class="strategy-item-label">Last Execution</span>
                <span class="strategy-item-value">${App.formatDate(s.lastExecution)}</span>
            </div>
            <div class="strategy-item">
                <span class="strategy-item-label">Next Signal ETA</span>
                <span class="strategy-item-value">${s.nextSignalEta}</span>
            </div>
        `;
    },
};
