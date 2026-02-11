from datetime import date, timedelta

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.pnl_snapshot import PnlSnapshot


class PnlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> PnlSnapshot:
        snapshot = PnlSnapshot(**kwargs)
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    async def get_latest(self, owner: str) -> PnlSnapshot | None:
        result = await self.session.execute(
            select(PnlSnapshot)
            .where(PnlSnapshot.owner == owner)
            .order_by(desc(PnlSnapshot.date))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(
        self, owner: str, days: int | None = None
    ) -> list[PnlSnapshot]:
        query = select(PnlSnapshot).where(PnlSnapshot.owner == owner)

        if days is not None:
            cutoff = date.today() - timedelta(days=days)
            query = query.where(PnlSnapshot.date >= cutoff)

        query = query.order_by(PnlSnapshot.date)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_date(self, owner: str, target_date: date) -> PnlSnapshot | None:
        result = await self.session.execute(
            select(PnlSnapshot).where(
                PnlSnapshot.owner == owner, PnlSnapshot.date == target_date
            )
        )
        return result.scalar_one_or_none()
