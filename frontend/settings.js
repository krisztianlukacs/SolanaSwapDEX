// Settings Page Logic

const Settings = {
    // Local copy of settings for editing
    formData: null,

    init() {
        this.formData = {
            enabled: MockData.user.enabled,
            solTradeSize: MockData.user.tradeSize.sol,
            usdcTradeSize: MockData.user.tradeSize.usdc,
            feePoolMin: MockData.user.feePool.minBalance,
            feePoolTarget: MockData.user.feePool.targetBalance,
            maxSlippageBps: MockData.user.slippageBps,
            relayerRefundLamports: MockData.user.relayerRefundLamports,
        };
        this.render();
    },

    render() {
        const container = document.getElementById('settingsGrid');
        const user = MockData.user;

        container.innerHTML = `
            <!-- Profile Status -->
            <div class="settings-card">
                <div class="settings-card-title">Profile Status</div>
                <div class="settings-group">
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">Strategy Enabled</div>
                            <div class="settings-hint">Toggle to enable or disable automated trading</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="settingsEnabled" ${this.formData.enabled ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>
            </div>

            <!-- Trade Size -->
            <div class="settings-card">
                <div class="settings-card-title">Trade Size</div>
                <div class="settings-group">
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">SOL Trade Size</div>
                            <div class="settings-hint" id="solLamportsHint">${this.toLamports(this.formData.solTradeSize)} lamports</div>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <input type="number" id="settingsSolSize" value="${this.formData.solTradeSize}" step="0.1" min="0">
                            <span style="color:var(--text-muted)">SOL</span>
                        </div>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">USDC Trade Size</div>
                            <div class="settings-hint">Amount per trade in USDC</div>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <input type="number" id="settingsUsdcSize" value="${this.formData.usdcTradeSize}" step="1" min="0">
                            <span style="color:var(--text-muted)">USDC</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Fee Pool Settings -->
            <div class="settings-card">
                <div class="settings-card-title">Fee Pool</div>
                <div class="settings-group">
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">Minimum Balance</div>
                            <div class="settings-hint">Alert threshold for fee pool</div>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <input type="number" id="settingsFeeMin" value="${this.formData.feePoolMin}" step="0.01" min="0">
                            <span style="color:var(--text-muted)">SOL</span>
                        </div>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">Target Balance</div>
                            <div class="settings-hint">Optimal fee pool balance</div>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <input type="number" id="settingsFeeTarget" value="${this.formData.feePoolTarget}" step="0.01" min="0">
                            <span style="color:var(--text-muted)">SOL</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Risk Settings -->
            <div class="settings-card">
                <div class="settings-card-title">Risk Settings</div>
                <div class="settings-group">
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">Max Slippage</div>
                            <div class="settings-hint" id="slippagePctHint">${this.bpsToPercent(this.formData.maxSlippageBps)}%</div>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <input type="number" id="settingsSlippage" value="${this.formData.maxSlippageBps}" step="1" min="1" max="1000">
                            <span style="color:var(--text-muted)">bps</span>
                        </div>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">Protocol Fee</div>
                            <div class="settings-hint">${user.protocolFeeBps} bps (${this.bpsToPercent(user.protocolFeeBps)}%)</div>
                        </div>
                        <div class="settings-value">Read-only</div>
                    </div>
                    <div class="settings-row">
                        <div>
                            <div class="settings-label">Relayer Refund</div>
                            <div class="settings-hint">Refund amount per transaction</div>
                        </div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <input type="number" id="settingsRelayer" value="${this.formData.relayerRefundLamports}" step="1000" min="0">
                            <span style="color:var(--text-muted)">lamports</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Save Button (full width) -->
            <div style="grid-column: 1 / -1; display:flex; justify-content:flex-end; gap:12px;">
                <button class="btn btn-secondary" id="settingsResetBtn">Reset</button>
                <button class="btn btn-primary" id="settingsSaveBtn">Save Settings</button>
            </div>
        `;

        this.attachListeners();
    },

    attachListeners() {
        // Toggle with confirmation
        document.getElementById('settingsEnabled').addEventListener('change', (e) => {
            const newState = e.target.checked;
            if (!newState) {
                // Confirm disable
                const confirmed = confirm('Are you sure you want to disable the strategy? No automated trades will be executed.');
                if (!confirmed) {
                    e.target.checked = true;
                    return;
                }
            }
            this.formData.enabled = newState;
            this.updateStrategyBadge(newState);
        });

        // SOL size -> lamports hint
        document.getElementById('settingsSolSize').addEventListener('input', (e) => {
            const val = parseFloat(e.target.value) || 0;
            this.formData.solTradeSize = val;
            document.getElementById('solLamportsHint').textContent = `${this.toLamports(val)} lamports`;
        });

        // Slippage -> percent hint
        document.getElementById('settingsSlippage').addEventListener('input', (e) => {
            const val = parseInt(e.target.value) || 0;
            this.formData.maxSlippageBps = val;
            document.getElementById('slippagePctHint').textContent = `${this.bpsToPercent(val)}%`;
        });

        // Other inputs
        document.getElementById('settingsUsdcSize').addEventListener('input', (e) => {
            this.formData.usdcTradeSize = parseFloat(e.target.value) || 0;
        });
        document.getElementById('settingsFeeMin').addEventListener('input', (e) => {
            this.formData.feePoolMin = parseFloat(e.target.value) || 0;
        });
        document.getElementById('settingsFeeTarget').addEventListener('input', (e) => {
            this.formData.feePoolTarget = parseFloat(e.target.value) || 0;
        });
        document.getElementById('settingsRelayer').addEventListener('input', (e) => {
            this.formData.relayerRefundLamports = parseInt(e.target.value) || 0;
        });

        // Save
        document.getElementById('settingsSaveBtn').addEventListener('click', () => {
            this.save();
        });

        // Reset
        document.getElementById('settingsResetBtn').addEventListener('click', () => {
            this.init(); // Re-initialize from mock data
            App.toast('Settings reset to defaults', 'info');
        });
    },

    save() {
        const btn = document.getElementById('settingsSaveBtn');
        btn.disabled = true;
        btn.textContent = 'Saving...';

        // Simulate save delay
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = 'Save Settings';
            App.toast('Settings saved successfully', 'success');
        }, 800);
    },

    updateStrategyBadge(enabled) {
        const badge = document.getElementById('strategyBadge');
        if (enabled) {
            badge.classList.remove('disabled');
            badge.innerHTML = '<span class="strategy-dot"></span><span>Strategy Active</span>';
        } else {
            badge.classList.add('disabled');
            badge.innerHTML = '<span class="strategy-dot"></span><span>Strategy Disabled</span>';
        }
    },

    toLamports(sol) {
        return Math.round(sol * 1e9).toLocaleString();
    },

    bpsToPercent(bps) {
        return (bps / 100).toFixed(2);
    },
};
