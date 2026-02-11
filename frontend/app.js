// App Core - SPA Router, State, Utilities

const App = {
    state: {
        currentPage: 'dashboard',
        walletConnected: false,
        walletAddress: null,
    },

    pages: ['dashboard', 'portfolio', 'transactions', 'settings'],

    init() {
        this.restoreWalletState();
        this.setupNavigation();
        this.setupMobileMenu();
        this.handleInitialRoute();

        // Initialize all page modules
        Dashboard.init();
        Portfolio.init();
        Transactions.init();
        Settings.init();
        Wallet.init();
    },

    // ===== Routing =====
    setupNavigation() {
        // Nav click handlers
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.navigateTo(page);
            });
        });

        // Hash change handler
        window.addEventListener('hashchange', () => {
            const page = location.hash.replace('#', '') || 'dashboard';
            if (this.pages.includes(page)) {
                this.showPage(page);
            }
        });
    },

    handleInitialRoute() {
        const hash = location.hash.replace('#', '');
        const page = this.pages.includes(hash) ? hash : 'dashboard';
        this.showPage(page);
    },

    navigateTo(page) {
        location.hash = page;
        this.showPage(page);
        // Close mobile sidebar
        document.getElementById('sidebar').classList.remove('open');
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) overlay.classList.remove('show');
    },

    showPage(page) {
        this.state.currentPage = page;

        // Update nav active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });

        // Show/hide pages
        document.querySelectorAll('.page').forEach(section => {
            const id = section.id.replace('page-', '');
            section.classList.toggle('hidden', id !== page);
        });

        // Trigger chart resize on page show (Chart.js needs this)
        if (page === 'dashboard') {
            Charts.resize();
        }
    },

    // ===== Mobile Menu =====
    setupMobileMenu() {
        const btn = document.getElementById('mobileMenuBtn');
        const sidebar = document.getElementById('sidebar');

        // Create overlay element
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);

        btn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('show');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        });
    },

    // ===== Wallet State Persistence =====
    restoreWalletState() {
        const saved = localStorage.getItem('solswap_wallet');
        if (saved) {
            const data = JSON.parse(saved);
            this.state.walletConnected = true;
            this.state.walletAddress = data.address;
        }
    },

    saveWalletState(address) {
        this.state.walletConnected = true;
        this.state.walletAddress = address;
        localStorage.setItem('solswap_wallet', JSON.stringify({ address }));
    },

    clearWalletState() {
        this.state.walletConnected = false;
        this.state.walletAddress = null;
        localStorage.removeItem('solswap_wallet');
    },

    // ===== Toast Notifications =====
    toast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const icons = {
            success: '\u2713',
            error: '\u2717',
            info: '\u2139',
        };

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('removing');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // ===== Modal =====
    showModal(html) {
        const overlay = document.getElementById('modalOverlay');
        const content = document.getElementById('modalContent');
        content.innerHTML = html;
        overlay.classList.remove('hidden');

        // Close on overlay click
        overlay.onclick = (e) => {
            if (e.target === overlay) this.closeModal();
        };

        // Close on Escape
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    },

    closeModal() {
        document.getElementById('modalOverlay').classList.add('hidden');
    },

    // ===== Formatting Utilities =====
    formatUsd(value) {
        return '$' + Number(value).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    },

    formatSol(value) {
        return Number(value).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 4,
        }) + ' SOL';
    },

    formatUsdc(value) {
        return Number(value).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }) + ' USDC';
    },

    formatNumber(value, decimals = 2) {
        return Number(value).toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        });
    },

    formatDate(isoString) {
        const d = new Date(isoString);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    },

    formatDateShort(isoString) {
        const d = new Date(isoString);
        return d.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
        });
    },

    timeAgo(isoString) {
        const now = new Date();
        const then = new Date(isoString);
        const diffMs = now - then;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    },

    truncateAddress(addr) {
        if (!addr) return '';
        return addr.slice(0, 4) + '...' + addr.slice(-4);
    },

    truncateSig(sig) {
        if (!sig) return '';
        return sig.slice(0, 8) + '...' + sig.slice(-4);
    },
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => App.init());
