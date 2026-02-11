// Transaction History with Filtering, Sorting, Pagination

const Transactions = {
    state: {
        filterType: 'all',
        filterStatus: 'all',
        dateFrom: null,
        dateTo: null,
        sortField: 'date',
        sortDir: 'desc',
        page: 1,
        pageSize: 25,
    },

    init() {
        this.setupFilters();
        this.setupSorting();
        this.setupPagination();
        this.setupExport();
        this.render();
    },

    getFilteredData() {
        let data = [...MockData.transactions];

        // Filter by type
        if (this.state.filterType !== 'all') {
            data = data.filter(tx => tx.type === this.state.filterType);
        }

        // Filter by status
        if (this.state.filterStatus !== 'all') {
            data = data.filter(tx => tx.status === this.state.filterStatus);
        }

        // Filter by date range
        if (this.state.dateFrom) {
            const from = new Date(this.state.dateFrom);
            data = data.filter(tx => new Date(tx.date) >= from);
        }
        if (this.state.dateTo) {
            const to = new Date(this.state.dateTo);
            to.setHours(23, 59, 59);
            data = data.filter(tx => new Date(tx.date) <= to);
        }

        // Sort
        data.sort((a, b) => {
            let valA = a[this.state.sortField];
            let valB = b[this.state.sortField];

            if (this.state.sortField === 'date') {
                valA = new Date(valA).getTime();
                valB = new Date(valB).getTime();
            } else if (typeof valA === 'string') {
                valA = valA.toLowerCase();
                valB = valB.toLowerCase();
            }

            if (valA < valB) return this.state.sortDir === 'asc' ? -1 : 1;
            if (valA > valB) return this.state.sortDir === 'asc' ? 1 : -1;
            return 0;
        });

        return data;
    },

    render() {
        const data = this.getFilteredData();
        const totalItems = data.length;
        const totalPages = Math.max(1, Math.ceil(totalItems / this.state.pageSize));

        // Clamp current page
        if (this.state.page > totalPages) this.state.page = totalPages;

        const startIdx = (this.state.page - 1) * this.state.pageSize;
        const pageData = data.slice(startIdx, startIdx + this.state.pageSize);

        // Render table body
        const tbody = document.getElementById('txTableBody');
        if (pageData.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-muted);">
                    No transactions found
                </td></tr>
            `;
        } else {
            tbody.innerHTML = pageData.map(tx => {
                const typeClass = tx.type === 'SOL_TO_USDC' ? 'sol-to-usdc' : 'usdc-to-sol';
                const typeLabel = tx.type === 'SOL_TO_USDC' ? 'SOL \u2192 USDC' : 'USDC \u2192 SOL';
                const inLabel = `${App.formatNumber(tx.amountIn, tx.tokenIn === 'SOL' ? 4 : 2)} ${tx.tokenIn}`;
                const outLabel = `${App.formatNumber(tx.amountOut, tx.tokenOut === 'SOL' ? 4 : 2)} ${tx.tokenOut}`;
                const sigTruncated = App.truncateSig(tx.signature);
                const explorerUrl = `https://solscan.io/tx/${tx.signature}`;

                return `
                    <tr>
                        <td>${App.formatDate(tx.date)}</td>
                        <td><span class="tx-type ${typeClass}">${typeLabel}</span></td>
                        <td>${inLabel}</td>
                        <td>${outLabel}</td>
                        <td>${tx.slippageBps} bps</td>
                        <td>${App.formatNumber(tx.fee, 5)}</td>
                        <td>
                            <span class="status-badge ${tx.status}">
                                <span class="status-dot"></span>
                                ${tx.status.charAt(0).toUpperCase() + tx.status.slice(1)}
                            </span>
                        </td>
                        <td><a class="tx-sig" href="${explorerUrl}" target="_blank" rel="noopener">${sigTruncated}</a></td>
                    </tr>
                `;
            }).join('');
        }

        // Update pagination info
        const endIdx = Math.min(startIdx + this.state.pageSize, totalItems);
        document.getElementById('paginationInfo').textContent =
            totalItems > 0 ? `Showing ${startIdx + 1}-${endIdx} of ${totalItems}` : 'No results';
        document.getElementById('pageIndicator').textContent = `Page ${this.state.page} of ${totalPages}`;
        document.getElementById('prevPage').disabled = this.state.page <= 1;
        document.getElementById('nextPage').disabled = this.state.page >= totalPages;
    },

    setupFilters() {
        document.getElementById('filterType').addEventListener('change', (e) => {
            this.state.filterType = e.target.value;
            this.state.page = 1;
            this.render();
        });

        document.getElementById('filterStatus').addEventListener('change', (e) => {
            this.state.filterStatus = e.target.value;
            this.state.page = 1;
            this.render();
        });

        document.getElementById('filterDateFrom').addEventListener('change', (e) => {
            this.state.dateFrom = e.target.value || null;
            this.state.page = 1;
            this.render();
        });

        document.getElementById('filterDateTo').addEventListener('change', (e) => {
            this.state.dateTo = e.target.value || null;
            this.state.page = 1;
            this.render();
        });
    },

    setupSorting() {
        document.querySelectorAll('.tx-table th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const field = th.dataset.sort;
                if (this.state.sortField === field) {
                    this.state.sortDir = this.state.sortDir === 'asc' ? 'desc' : 'asc';
                } else {
                    this.state.sortField = field;
                    this.state.sortDir = 'desc';
                }

                // Update sort indicators
                document.querySelectorAll('.tx-table th.sortable').forEach(h => {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                    h.querySelector('.sort-arrow').textContent = '';
                });
                th.classList.add(this.state.sortDir === 'asc' ? 'sorted-asc' : 'sorted-desc');
                th.querySelector('.sort-arrow').textContent = this.state.sortDir === 'asc' ? '\u25B4' : '\u25BE';

                this.state.page = 1;
                this.render();
            });
        });
    },

    setupPagination() {
        document.getElementById('prevPage').addEventListener('click', () => {
            if (this.state.page > 1) {
                this.state.page--;
                this.render();
            }
        });

        document.getElementById('nextPage').addEventListener('click', () => {
            const totalPages = Math.ceil(this.getFilteredData().length / this.state.pageSize);
            if (this.state.page < totalPages) {
                this.state.page++;
                this.render();
            }
        });

        document.getElementById('pageSize').addEventListener('change', (e) => {
            this.state.pageSize = parseInt(e.target.value);
            this.state.page = 1;
            this.render();
        });
    },

    setupExport() {
        document.getElementById('exportCsvBtn').addEventListener('click', () => {
            this.exportCsv();
        });
    },

    exportCsv() {
        const data = this.getFilteredData();
        const headers = ['Date', 'Type', 'Amount In', 'Token In', 'Amount Out', 'Token Out', 'Slippage (bps)', 'Fee', 'Status', 'Signature'];

        const rows = data.map(tx => [
            new Date(tx.date).toISOString(),
            tx.type,
            tx.amountIn,
            tx.tokenIn,
            tx.amountOut,
            tx.tokenOut,
            tx.slippageBps,
            tx.fee,
            tx.status,
            tx.signature,
        ]);

        const csv = [
            headers.join(','),
            ...rows.map(r => r.map(v => `"${v}"`).join(',')),
        ].join('\n');

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `solswap-transactions-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        App.toast('CSV exported successfully', 'success');
    },
};
