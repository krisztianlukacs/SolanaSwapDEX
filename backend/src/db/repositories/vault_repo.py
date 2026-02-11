from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.vault_balance import VaultBalance


class VaultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_owner(self, owner: str) -> VaultBalance | None:
        result = await self.session.execute(
            select(VaultBalance).where(VaultBalance.owner == owner)
        )
        return result.scalar_one_or_none()

    async def create(self, owner: str, **kwargs) -> VaultBalance:
        vault = VaultBalance(owner=owner, **kwargs)
        self.session.add(vault)
        await self.session.flush()
        return vault

    async def get_or_create(self, owner: str) -> VaultBalance:
        vault = await self.get_by_owner(owner)
        if vault is None:
            vault = await self.create(owner)
        return vault

    async def update_sol_balance(self, owner: str, amount: int) -> None:
        await self.session.execute(
            update(VaultBalance)
            .where(VaultBalance.owner == owner)
            .values(sol_balance=amount)
        )
        await self.session.flush()

    async def update_usdc_balance(self, owner: str, amount: int) -> None:
        await self.session.execute(
            update(VaultBalance)
            .where(VaultBalance.owner == owner)
            .values(usdc_balance=amount)
        )
        await self.session.flush()

    async def update_fee_pool_balance(self, owner: str, amount: int) -> None:
        await self.session.execute(
            update(VaultBalance)
            .where(VaultBalance.owner == owner)
            .values(fee_pool_balance=amount)
        )
        await self.session.flush()

    async def adjust_sol_balance(self, owner: str, delta: int) -> None:
        await self.session.execute(
            update(VaultBalance)
            .where(VaultBalance.owner == owner)
            .values(sol_balance=VaultBalance.sol_balance + delta)
        )
        await self.session.flush()

    async def adjust_usdc_balance(self, owner: str, delta: int) -> None:
        await self.session.execute(
            update(VaultBalance)
            .where(VaultBalance.owner == owner)
            .values(usdc_balance=VaultBalance.usdc_balance + delta)
        )
        await self.session.flush()

    async def adjust_fee_pool_balance(self, owner: str, delta: int) -> None:
        await self.session.execute(
            update(VaultBalance)
            .where(VaultBalance.owner == owner)
            .values(fee_pool_balance=VaultBalance.fee_pool_balance + delta)
        )
        await self.session.flush()
