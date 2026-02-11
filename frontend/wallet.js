// Wallet Connection Simulation

const Wallet = {
    init() {
        const btn = document.getElementById('connectWalletBtn');
        btn.addEventListener('click', () => this.handleClick());

        // Restore state from App
        if (App.state.walletConnected) {
            this.showConnectedState(App.state.walletAddress);
        }
    },

    handleClick() {
        if (App.state.walletConnected) {
            this.disconnect();
        } else {
            this.showWalletModal();
        }
    },

    showWalletModal() {
        const wallets = [
            { name: 'Phantom', icon: 'P', detected: true },
            { name: 'Solflare', icon: 'S', detected: false },
            { name: 'Backpack', icon: 'B', detected: false },
        ];

        const optionsHtml = wallets.map(w => `
            <div class="wallet-option" data-wallet="${w.name}">
                <div class="wallet-option-icon">${w.icon}</div>
                <div>
                    <div class="wallet-option-name">${w.name}</div>
                    ${w.detected ? '<div class="wallet-option-detected">Detected</div>' : ''}
                </div>
            </div>
        `).join('');

        App.showModal(`
            <h2 class="modal-title">Connect Wallet</h2>
            <div class="modal-body">
                <div class="wallet-options">
                    ${optionsHtml}
                </div>
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
            </div>
        `);

        // Attach click handlers
        document.querySelectorAll('.wallet-option').forEach(option => {
            option.addEventListener('click', () => {
                this.connect(option.dataset.wallet);
            });
        });
    },

    connect(walletName) {
        const modal = document.getElementById('modalContent');
        modal.innerHTML = `
            <h2 class="modal-title">Connecting...</h2>
            <div class="modal-body" style="text-align:center; padding:20px 0;">
                <div class="strategy-dot" style="width:24px;height:24px;margin:0 auto 12px;background:var(--accent-purple);"></div>
                <p style="color:var(--text-secondary);">Waiting for ${walletName} approval...</p>
            </div>
        `;

        // Simulate connection delay
        setTimeout(() => {
            const address = MockData.user.walletAddress;
            App.saveWalletState(address);
            this.showConnectedState(address);
            App.closeModal();
            App.toast(`Connected via ${walletName}`, 'success');
        }, 1000);
    },

    showConnectedState(address) {
        const section = document.getElementById('walletSection');
        const truncated = App.truncateAddress(address);
        section.innerHTML = `
            <div class="wallet-address">
                <span class="wallet-dot"></span>
                <span>${truncated}</span>
            </div>
            <button class="btn btn-secondary btn-sm" id="disconnectWalletBtn">Disconnect</button>
        `;

        document.getElementById('disconnectWalletBtn').addEventListener('click', () => {
            this.disconnect();
        });
    },

    disconnect() {
        App.clearWalletState();
        const section = document.getElementById('walletSection');
        section.innerHTML = `
            <button class="btn btn-primary" id="connectWalletBtn">Connect Wallet</button>
        `;
        document.getElementById('connectWalletBtn').addEventListener('click', () => {
            this.handleClick();
        });
        App.toast('Wallet disconnected', 'info');
    },
};
