// Mock Data for SolanaSwapDEX Frontend

const MockData = {
    user: {
        walletAddress: '7xK3mBf9rQvZ8nJp4sW2yL6hT1cX5dA8kF3gN9fPq',
        enabled: true,
        tradeSize: {
            sol: 2.5,
            solLamports: 2500000000,
            usdc: 500,
        },
        feePool: {
            minBalance: 0.05,
            targetBalance: 0.15,
        },
        slippageBps: 50,
        protocolFeeBps: 10,
        relayerRefundLamports: 5000,
    },

    vaults: {
        sol: {
            balance: 24.5,
            usdPrice: 148.32,
            get usdValue() { return this.balance * this.usdPrice; },
        },
        usdc: {
            balance: 3842.50,
            usdPrice: 1.0,
            get usdValue() { return this.balance * this.usdPrice; },
        },
        feePool: {
            balance: 0.085,
            minThreshold: 0.05,
            targetThreshold: 0.15,
        },
    },

    portfolio: {
        get totalValueUsd() {
            return MockData.vaults.sol.usdValue + MockData.vaults.usdc.usdValue;
        },
        change24h: 2.34,
        change30d: 11.5,
        allTimePnl: 4281.75,
        allTimePnlPercent: 68.2,
        get allTimeSolPnl() {
            const h = MockData.pnlHistory;
            return h.length ? h[h.length - 1].cumulativeSolPnl : 0;
        },
        get allTimeUsdcPnl() {
            const h = MockData.pnlHistory;
            return h.length ? h[h.length - 1].cumulativeUsdcPnl : 0;
        },
    },

    strategy: {
        currentPosition: 'USDC-heavy',
        enabled: true,
        lastExecution: '2026-02-11T08:42:15Z',
        nextSignalEta: '~15 min',
    },

    // Generate 90 days of PnL data
    pnlHistory: generatePnlHistory(),

    // Generate 50+ transactions
    transactions: generateTransactions(),
};

function generatePnlHistory() {
    const data = [];
    const startDate = new Date('2025-11-14');
    const endDate = new Date('2026-02-11');
    const phase2Start = new Date('2025-12-16');
    const phase3Start = new Date('2026-01-16');
    const dayMs = 86400000;

    let cumulativePnl = 0;
    let cumulativeSolPnl = 0;
    let cumulativeUsdcPnl = 0;

    // Seed a simple deterministic-ish random for reproducibility
    let seed = 42;
    function seededRandom() {
        seed = (seed * 16807 + 0) % 2147483647;
        return (seed - 1) / 2147483646;
    }

    // SOL price starts ~$95 in Nov, rises to ~$148 by Feb
    const baseSolPrice = 95;
    const solPriceEnd = 148.32;
    const totalDays = Math.round((endDate - startDate) / dayMs);

    for (let d = new Date(startDate); d <= endDate; d = new Date(d.getTime() + dayMs)) {
        const dayIndex = Math.round((d - startDate) / dayMs);
        const progress = dayIndex / totalDays;

        // SOL price: gradual rise with noise
        const solPrice = baseSolPrice + (solPriceEnd - baseSolPrice) * progress
            + (seededRandom() - 0.5) * 4;

        let dailySolPnl = 0;  // in SOL
        let dailyUsdcPnl = 0; // in USDC

        if (d < phase2Start) {
            // Phase 1 (Nov 14 – Dec 15): USDC-dominant
            dailyUsdcPnl = (1200 + cumulativeUsdcPnl) * ((seededRandom() * 0.5 + 0.1) / 100);
            dailySolPnl = (seededRandom() - 0.45) * 0.002; // near-zero SOL noise
        } else if (d < phase3Start) {
            // Phase 2 (Dec 16 – Jan 15): Both tokens profitable
            dailyUsdcPnl = (1200 + cumulativeUsdcPnl) * ((seededRandom() * 0.35 + 0.05) / 100);
            dailySolPnl = (5 + cumulativeSolPnl) * ((seededRandom() * 0.6 + 0.1) / 100);
        } else {
            // Phase 3 (Jan 16 – Feb 11): SOL-dominant
            dailyUsdcPnl = (seededRandom() - 0.45) * 0.5; // near-zero USDC noise
            dailySolPnl = (5 + cumulativeSolPnl) * ((seededRandom() * 1.2 + 0.4) / 100);
        }

        cumulativeSolPnl += dailySolPnl;
        cumulativeUsdcPnl += dailyUsdcPnl;

        // Total PnL in USD: USDC PnL (1:1) + SOL PnL converted at current price
        const dailyPnl = dailyUsdcPnl + dailySolPnl * solPrice;
        cumulativePnl += dailyPnl;

        data.push({
            date: new Date(d).toISOString().split('T')[0],
            dailyPnl: Math.round(dailyPnl * 100) / 100,
            cumulativePnl: Math.round(cumulativePnl * 100) / 100,
            dailySolPnl: Math.round(dailySolPnl * 10000) / 10000,
            cumulativeSolPnl: Math.round(cumulativeSolPnl * 10000) / 10000,
            dailyUsdcPnl: Math.round(dailyUsdcPnl * 100) / 100,
            cumulativeUsdcPnl: Math.round(cumulativeUsdcPnl * 100) / 100,
            solPrice: Math.round(solPrice * 100) / 100,
        });
    }
    return data;
}

function generateTransactions() {
    const txTypes = ['SOL_TO_USDC', 'USDC_TO_SOL'];
    const statuses = ['confirmed', 'confirmed', 'confirmed', 'confirmed', 'confirmed', 'confirmed', 'confirmed', 'confirmed', 'pending', 'failed'];
    const transactions = [];

    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz123456789';
    function randomSig() {
        let sig = '';
        for (let i = 0; i < 88; i++) {
            sig += chars[Math.floor(Math.random() * chars.length)];
        }
        return sig;
    }

    const startDate = new Date('2025-11-14');
    for (let i = 0; i < 55; i++) {
        const dayOffset = Math.floor(Math.random() * 90);
        const date = new Date(startDate.getTime() + dayOffset * 86400000);
        date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60));

        const type = txTypes[Math.floor(Math.random() * txTypes.length)];
        const status = statuses[Math.floor(Math.random() * statuses.length)];
        const slippageBps = Math.floor(Math.random() * 30) + 5;

        let amountIn, amountOut, fee;
        if (type === 'SOL_TO_USDC') {
            amountIn = Math.round((Math.random() * 4 + 0.5) * 1000) / 1000;
            amountOut = Math.round(amountIn * (148.32 + (Math.random() - 0.5) * 20) * 100) / 100;
            fee = Math.round(amountIn * 0.001 * 100000) / 100000;
        } else {
            amountIn = Math.round((Math.random() * 600 + 50) * 100) / 100;
            amountOut = Math.round((amountIn / (148.32 + (Math.random() - 0.5) * 20)) * 1000) / 1000;
            fee = Math.round(amountOut * 0.001 * 100000) / 100000;
        }

        transactions.push({
            id: i + 1,
            date: date.toISOString(),
            type,
            amountIn,
            amountOut,
            tokenIn: type === 'SOL_TO_USDC' ? 'SOL' : 'USDC',
            tokenOut: type === 'SOL_TO_USDC' ? 'USDC' : 'SOL',
            slippageBps,
            fee,
            status,
            signature: randomSig(),
        });
    }

    // Sort by date descending
    transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
    return transactions;
}

// Freeze data to prevent accidental mutation
Object.freeze(MockData.user);
Object.freeze(MockData.strategy);
