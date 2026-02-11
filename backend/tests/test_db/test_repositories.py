from datetime import date, datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.constants import SIGNAL_SOL_TO_USDC, WSOL_MINT, USDC_MINT, TX_PENDING, TX_CONFIRMED
from src.db.repositories.user_repo import UserRepository
from src.db.repositories.vault_repo import VaultRepository
from src.db.repositories.transaction_repo import TransactionRepository
from src.db.repositories.pnl_repo import PnlRepository
from src.db.repositories.signal_repo import SignalRepository

from tests.conftest import TEST_WALLET


@pytest.mark.asyncio
class TestUserRepository:
    async def test_create_user(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        profile = await repo.create(TEST_WALLET)
        await db_session.commit()

        assert profile.owner == TEST_WALLET
        assert profile.enabled is True
        assert profile.trade_size_sol == 2_500_000_000

    async def test_get_or_create(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        p1 = await repo.get_or_create(TEST_WALLET)
        await db_session.commit()
        p2 = await repo.get_or_create(TEST_WALLET)
        assert p1.owner == p2.owner

    async def test_update_user(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        await repo.create(TEST_WALLET)
        await db_session.commit()

        updated = await repo.update(TEST_WALLET, enabled=False, max_slippage_bps=100)
        await db_session.commit()

        assert updated.enabled is False
        assert updated.max_slippage_bps == 100

    async def test_get_enabled_users(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        await repo.create("wallet_1_aaaaaaaaaaaaaaaaaaaaaaaaaaa")
        await repo.create("wallet_2_bbbbbbbbbbbbbbbbbbbbbbbbbbb")
        await db_session.commit()
        await repo.update("wallet_2_bbbbbbbbbbbbbbbbbbbbbbbbbbb", enabled=False)
        await db_session.commit()

        enabled = await repo.get_enabled_users()
        assert len(enabled) == 1
        assert enabled[0].owner == "wallet_1_aaaaaaaaaaaaaaaaaaaaaaaaaaa"


@pytest.mark.asyncio
class TestVaultRepository:
    async def test_create_and_get(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        repo = VaultRepository(db_session)
        vault = await repo.get_or_create(TEST_WALLET)
        await db_session.commit()

        assert vault.sol_balance == 0
        assert vault.usdc_balance == 0
        assert vault.fee_pool_balance == 0

    async def test_adjust_balances(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        repo = VaultRepository(db_session)
        await repo.create(TEST_WALLET)
        await db_session.commit()

        await repo.adjust_sol_balance(TEST_WALLET, 1_000_000_000)
        await repo.adjust_usdc_balance(TEST_WALLET, 500_000_000)
        await repo.adjust_fee_pool_balance(TEST_WALLET, 50_000_000)
        await db_session.commit()

        vault = await repo.get_by_owner(TEST_WALLET)
        assert vault.sol_balance == 1_000_000_000
        assert vault.usdc_balance == 500_000_000
        assert vault.fee_pool_balance == 50_000_000


@pytest.mark.asyncio
class TestTransactionRepository:
    async def test_create_and_list(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        repo = TransactionRepository(db_session)
        await repo.create(
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
            signature="abc123def456" * 7 + "abcd",
        )
        await db_session.commit()

        txs, total = await repo.list_for_owner(TEST_WALLET)
        assert total == 1
        assert txs[0].type == SIGNAL_SOL_TO_USDC

    async def test_filter_by_status(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        repo = TransactionRepository(db_session)
        for status in [TX_CONFIRMED, TX_PENDING, TX_CONFIRMED]:
            await repo.create(
                owner=TEST_WALLET,
                date=datetime.now(timezone.utc),
                type=SIGNAL_SOL_TO_USDC,
                amount_in=1_000_000_000,
                amount_out=150_000_000,
                token_in=WSOL_MINT,
                token_out=USDC_MINT,
                slippage_bps=50,
                fee=10_000,
                status=status,
            )
        await db_session.commit()

        txs, total = await repo.list_for_owner(TEST_WALLET, status_filter=TX_CONFIRMED)
        assert total == 2


@pytest.mark.asyncio
class TestPnlRepository:
    async def test_create_and_get_history(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        await user_repo.create(TEST_WALLET)
        await db_session.commit()

        repo = PnlRepository(db_session)
        await repo.create(
            owner=TEST_WALLET,
            date=date(2026, 2, 10),
            daily_pnl=50.00,
            cumulative_pnl=1000.00,
            daily_sol_pnl=0.5,
            cumulative_sol_pnl=10.0,
            daily_usdc_pnl=25.0,
            cumulative_usdc_pnl=500.0,
            sol_price=148.32,
        )
        await repo.create(
            owner=TEST_WALLET,
            date=date(2026, 2, 11),
            daily_pnl=75.00,
            cumulative_pnl=1075.00,
            daily_sol_pnl=0.3,
            cumulative_sol_pnl=10.3,
            daily_usdc_pnl=30.0,
            cumulative_usdc_pnl=530.0,
            sol_price=149.00,
        )
        await db_session.commit()

        history = await repo.get_history(TEST_WALLET, days=7)
        assert len(history) == 2

        latest = await repo.get_latest(TEST_WALLET)
        assert latest.date == date(2026, 2, 11)
        assert float(latest.cumulative_pnl) == 1075.00


@pytest.mark.asyncio
class TestSignalRepository:
    async def test_create_and_update(self, db_session: AsyncSession):
        repo = SignalRepository(db_session)
        log = await repo.create(
            signal_type=SIGNAL_SOL_TO_USDC,
            status="received",
        )
        await db_session.commit()

        assert log.id is not None
        assert log.status == "received"

        await repo.update_status(log.id, "completed", affected_users=5)
        await db_session.commit()

        updated = await repo.get_by_id(log.id)
        assert updated.status == "completed"
        assert updated.affected_users == 5
