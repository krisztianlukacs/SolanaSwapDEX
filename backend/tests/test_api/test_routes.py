from datetime import date, datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.constants import (
    SIGNAL_SOL_TO_USDC,
    SIGNAL_USDC_TO_SOL,
    WSOL_MINT,
    USDC_MINT,
    TX_CONFIRMED,
)
from src.db.repositories.user_repo import UserRepository
from src.db.repositories.vault_repo import VaultRepository
from src.db.repositories.pnl_repo import PnlRepository
from src.db.repositories.transaction_repo import TransactionRepository

from tests.conftest import TEST_WALLET, WALLET_HEADERS


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert "database" in data
        assert "redis" in data


@pytest.mark.asyncio
class TestPortfolioEndpoint:
    async def test_get_metrics(self, client: AsyncClient, db_session: AsyncSession):
        # Setup: create user and vault with balances
        user_repo = UserRepository(db_session)
        vault_repo = VaultRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()
        await vault_repo.create(TEST_WALLET, sol_balance=24_500_000_000, usdc_balance=3_842_500_000)
        await db_session.commit()

        response = await client.get("/api/portfolio/metrics", headers=WALLET_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["total_value_usd"] > 0
        assert "pnl_all_time" in data

    async def test_metrics_without_wallet_header(self, client: AsyncClient):
        response = await client.get("/api/portfolio/metrics")
        assert response.status_code == 422


@pytest.mark.asyncio
class TestVaultsEndpoint:
    async def test_get_balances(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        vault_repo = VaultRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()
        await vault_repo.create(
            TEST_WALLET,
            sol_balance=10_000_000_000,
            usdc_balance=1_000_000_000,
            fee_pool_balance=100_000_000,
        )
        await db_session.commit()

        response = await client.get("/api/vaults/balances", headers=WALLET_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["sol_balance"] == 10.0
        assert data["usdc_balance"] == 1000.0
        assert data["fee_pool_balance"] == 0.1

    async def test_deposit_sol(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        vault_repo = VaultRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()
        await vault_repo.create(TEST_WALLET)
        await db_session.commit()

        response = await client.post(
            "/api/vaults/sol/deposit",
            json={"amount": 5.0},
            headers=WALLET_HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["new_balance"] == 5.0
        assert data["token"] == "SOL"

    async def test_withdraw_insufficient_balance(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        vault_repo = VaultRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()
        await vault_repo.create(TEST_WALLET, sol_balance=1_000_000_000)
        await db_session.commit()

        response = await client.post(
            "/api/vaults/sol/withdraw",
            json={"amount": 10.0},
            headers=WALLET_HEADERS,
        )
        assert response.status_code == 400

    async def test_invalid_token(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        vault_repo = VaultRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()
        await vault_repo.create(TEST_WALLET)
        await db_session.commit()

        response = await client.post(
            "/api/vaults/invalid/deposit",
            json={"amount": 1.0},
            headers=WALLET_HEADERS,
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestTransactionsEndpoint:
    async def test_list_transactions(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        tx_repo = TransactionRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        for i in range(3):
            await tx_repo.create(
                owner=TEST_WALLET,
                date=datetime.now(timezone.utc),
                type=SIGNAL_SOL_TO_USDC,
                amount_in=2_500_000_000,
                amount_out=370_000_000,
                token_in=WSOL_MINT,
                token_out=USDC_MINT,
                slippage_bps=50,
                fee=25_000,
                status=TX_CONFIRMED,
            )
        await db_session.commit()

        response = await client.get("/api/transactions", headers=WALLET_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert len(data["transactions"]) == 3
        assert data["pagination"]["total"] == 3

    async def test_pagination(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        tx_repo = TransactionRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        for i in range(15):
            await tx_repo.create(
                owner=TEST_WALLET,
                date=datetime.now(timezone.utc),
                type=SIGNAL_SOL_TO_USDC,
                amount_in=1_000_000_000,
                amount_out=150_000_000,
                token_in=WSOL_MINT,
                token_out=USDC_MINT,
                slippage_bps=50,
                fee=10_000,
                status=TX_CONFIRMED,
            )
        await db_session.commit()

        response = await client.get(
            "/api/transactions?page=1&page_size=5", headers=WALLET_HEADERS
        )
        data = response.json()
        assert len(data["transactions"]) == 5
        assert data["pagination"]["total"] == 15
        assert data["pagination"]["total_pages"] == 3

    async def test_csv_export(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        tx_repo = TransactionRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        await tx_repo.create(
            owner=TEST_WALLET,
            date=datetime.now(timezone.utc),
            type=SIGNAL_SOL_TO_USDC,
            amount_in=2_500_000_000,
            amount_out=370_000_000,
            token_in=WSOL_MINT,
            token_out=USDC_MINT,
            slippage_bps=50,
            fee=25_000,
            status=TX_CONFIRMED,
        )
        await db_session.commit()

        response = await client.get("/api/transactions/export", headers=WALLET_HEADERS)
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
class TestPnlEndpoint:
    async def test_get_history(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        pnl_repo = PnlRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        await pnl_repo.create(
            owner=TEST_WALLET,
            date=date(2026, 2, 10),
            daily_pnl=50.0,
            cumulative_pnl=1000.0,
            daily_sol_pnl=0.5,
            cumulative_sol_pnl=10.0,
            daily_usdc_pnl=25.0,
            cumulative_usdc_pnl=500.0,
            sol_price=148.32,
        )
        await db_session.commit()

        response = await client.get("/api/pnl/history?range=7", headers=WALLET_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) == 1
        assert data["range_days"] == 7


@pytest.mark.asyncio
class TestSettingsEndpoint:
    async def test_get_settings(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        response = await client.get("/api/settings", headers=WALLET_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["owner"] == TEST_WALLET
        assert data["enabled"] is True
        assert data["max_slippage_bps"] == 50

    async def test_update_settings(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        response = await client.put(
            "/api/settings",
            json={"max_slippage_bps": 100, "enabled": False},
            headers=WALLET_HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["max_slippage_bps"] == 100
        assert data["enabled"] is False

    async def test_reset_settings(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()
        await user_repo.update(TEST_WALLET, max_slippage_bps=200, enabled=False)
        await db_session.commit()

        response = await client.post("/api/settings/reset", headers=WALLET_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["max_slippage_bps"] == 50
        assert data["enabled"] is True


@pytest.mark.asyncio
class TestSignalsEndpoint:
    async def test_receive_signal(self, client: AsyncClient, db_session: AsyncSession):
        response = await client.post(
            "/api/signals",
            json={"signal_type": "SOL_TO_USDC"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["signal_type"] == "SOL_TO_USDC"
        assert data["status"] == "received"

    async def test_invalid_signal_type(self, client: AsyncClient):
        response = await client.post(
            "/api/signals",
            json={"signal_type": "INVALID"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestStrategyEndpoint:
    async def test_get_status(self, client: AsyncClient, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        vault_repo = VaultRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()
        await vault_repo.create(TEST_WALLET, sol_balance=10_000_000_000)
        await db_session.commit()

        response = await client.get("/api/strategy/status", headers=WALLET_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["current_position"] == "SOL"
        assert data["total_executions"] == 0
