// Chart.js Configurations

const Charts = {
    pnlChart: null,
    allocationChart: null,
    volumeChart: null,
    currentRange: 90,

    init() {
        this.setupGlobalDefaults();
        this.createPnlChart();
        this.createAllocationChart();
        this.createVolumeChart();
        this.setupToggles();
    },

    setupGlobalDefaults() {
        Chart.defaults.color = '#9ca3af';
        Chart.defaults.borderColor = 'rgba(31, 41, 55, 0.5)';
        Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    },

    // ===== PnL Line Chart (3 lines, dual Y-axis) =====
    createPnlChart() {
        const ctx = document.getElementById('pnlChart').getContext('2d');
        const data = this.getPnlData(this.currentRange);

        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.2)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

        this.pnlChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Total PnL ($)',
                        data: data.totalValues,
                        borderColor: '#8b5cf6',
                        backgroundColor: gradient,
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#8b5cf6',
                        pointHoverBorderColor: '#fff',
                        pointHoverBorderWidth: 2,
                        yAxisID: 'y',
                    },
                    {
                        label: 'USDC Profit ($)',
                        data: data.usdcValues,
                        borderColor: '#10b981',
                        borderWidth: 2,
                        borderDash: [6, 3],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        pointHoverBackgroundColor: '#10b981',
                        pointHoverBorderColor: '#fff',
                        pointHoverBorderWidth: 2,
                        yAxisID: 'y',
                    },
                    {
                        label: 'SOL Profit (SOL)',
                        data: data.solValues,
                        borderColor: '#f59e0b',
                        borderWidth: 2,
                        borderDash: [6, 3],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5,
                        pointHoverBackgroundColor: '#f59e0b',
                        pointHoverBorderColor: '#fff',
                        pointHoverBorderWidth: 2,
                        yAxisID: 'ySol',
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 16,
                            font: { size: 11 },
                        },
                    },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        titleColor: '#f9fafb',
                        bodyColor: '#f9fafb',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            label: (ctx) => {
                                if (ctx.datasetIndex === 2) {
                                    return `${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 4 })} SOL`;
                                }
                                return `${ctx.dataset.label}: $${ctx.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { maxTicksLimit: 8 },
                    },
                    y: {
                        position: 'left',
                        grid: { color: 'rgba(31, 41, 55, 0.5)' },
                        ticks: {
                            callback: (v) => '$' + v.toLocaleString(),
                        },
                    },
                    ySol: {
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: {
                            callback: (v) => v.toLocaleString('en-US', { maximumFractionDigits: 2 }) + ' SOL',
                        },
                    },
                },
            },
        });
    },

    getPnlData(days) {
        let history = MockData.pnlHistory;
        if (days !== 'all') {
            history = history.slice(-days);
        }
        return {
            labels: history.map(d => {
                const date = new Date(d.date);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }),
            totalValues: history.map(d => d.cumulativePnl),
            usdcValues: history.map(d => d.cumulativeUsdcPnl),
            solValues: history.map(d => d.cumulativeSolPnl),
        };
    },

    updatePnlChart(range) {
        this.currentRange = range;
        const data = this.getPnlData(range);

        const ctx = document.getElementById('pnlChart').getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.2)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

        this.pnlChart.data.labels = data.labels;
        this.pnlChart.data.datasets[0].data = data.totalValues;
        this.pnlChart.data.datasets[0].backgroundColor = gradient;
        this.pnlChart.data.datasets[1].data = data.usdcValues;
        this.pnlChart.data.datasets[2].data = data.solValues;
        this.pnlChart.update();
    },

    setupToggles() {
        document.querySelectorAll('#pnlToggles .toggle-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('#pnlToggles .toggle-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const range = btn.dataset.range === 'all' ? 'all' : parseInt(btn.dataset.range);
                this.updatePnlChart(range);
            });
        });
    },

    // ===== Allocation Doughnut =====
    createAllocationChart() {
        const ctx = document.getElementById('allocationChart').getContext('2d');
        const solValue = MockData.vaults.sol.usdValue;
        const usdcValue = MockData.vaults.usdc.usdValue;

        this.allocationChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['SOL', 'USDC'],
                datasets: [{
                    data: [solValue, usdcValue],
                    backgroundColor: ['#8b5cf6', '#10b981'],
                    borderColor: ['#7c3aed', '#059669'],
                    borderWidth: 2,
                    hoverOffset: 8,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle',
                        },
                    },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        titleColor: '#f9fafb',
                        bodyColor: '#f9fafb',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: (ctx) => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                                return `${ctx.label}: $${ctx.parsed.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${pct}%)`;
                            },
                        },
                    },
                },
            },
        });
    },

    // ===== Volume Bar Chart =====
    createVolumeChart() {
        const ctx = document.getElementById('volumeChart').getContext('2d');
        const volumeData = this.getVolumeData();

        this.volumeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: volumeData.labels,
                datasets: [
                    {
                        label: 'SOL \u2192 USDC',
                        data: volumeData.solToUsdc,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)',
                        borderColor: '#10b981',
                        borderWidth: 1,
                        borderRadius: 3,
                    },
                    {
                        label: 'USDC \u2192 SOL',
                        data: volumeData.usdcToSol,
                        backgroundColor: 'rgba(139, 92, 246, 0.7)',
                        borderColor: '#8b5cf6',
                        borderWidth: 1,
                        borderRadius: 3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle',
                        },
                    },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        titleColor: '#f9fafb',
                        bodyColor: '#f9fafb',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12,
                    },
                },
                scales: {
                    x: {
                        stacked: true,
                        grid: { display: false },
                        ticks: { maxTicksLimit: 8 },
                    },
                    y: {
                        stacked: true,
                        grid: { color: 'rgba(31, 41, 55, 0.5)' },
                        ticks: {
                            callback: (v) => '$' + v.toLocaleString(),
                        },
                    },
                },
            },
        });
    },

    getVolumeData() {
        // Aggregate transactions by week for last 30 days
        const now = new Date('2026-02-11');
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 86400000);
        const txs = MockData.transactions.filter(tx => new Date(tx.date) >= thirtyDaysAgo);

        // Group by week
        const weeks = {};
        txs.forEach(tx => {
            const d = new Date(tx.date);
            const weekStart = new Date(d);
            weekStart.setDate(d.getDate() - d.getDay());
            const key = weekStart.toISOString().split('T')[0];
            if (!weeks[key]) weeks[key] = { solToUsdc: 0, usdcToSol: 0 };

            const usdValue = tx.type === 'SOL_TO_USDC'
                ? tx.amountOut
                : tx.amountIn;

            if (tx.type === 'SOL_TO_USDC') {
                weeks[key].solToUsdc += usdValue;
            } else {
                weeks[key].usdcToSol += usdValue;
            }
        });

        const sortedKeys = Object.keys(weeks).sort();
        return {
            labels: sortedKeys.map(k => {
                const d = new Date(k);
                return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }),
            solToUsdc: sortedKeys.map(k => Math.round(weeks[k].solToUsdc)),
            usdcToSol: sortedKeys.map(k => Math.round(weeks[k].usdcToSol)),
        };
    },

    resize() {
        if (this.pnlChart) this.pnlChart.resize();
        if (this.allocationChart) this.allocationChart.resize();
        if (this.volumeChart) this.volumeChart.resize();
    },
};
