from datetime import datetime

from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Transaction:
        tx = Transaction(**kwargs)
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def get_by_id(self, tx_id: int) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == tx_id)
        )
        return result.scalar_one_or_none()

    async def get_by_signature(self, signature: str) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction).where(Transaction.signature == signature)
        )
        return result.scalar_one_or_none()

    async def list_for_owner(
        self,
        owner: str,
        *,
        type_filter: str | None = None,
        status_filter: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: str = "date",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Transaction], int]:
        query = select(Transaction).where(Transaction.owner == owner)
        count_query = select(func.count()).select_from(Transaction).where(Transaction.owner == owner)

        if type_filter:
            query = query.where(Transaction.type == type_filter)
            count_query = count_query.where(Transaction.type == type_filter)
        if status_filter:
            query = query.where(Transaction.status == status_filter)
            count_query = count_query.where(Transaction.status == status_filter)
        if date_from:
            query = query.where(Transaction.date >= date_from)
            count_query = count_query.where(Transaction.date >= date_from)
        if date_to:
            query = query.where(Transaction.date <= date_to)
            count_query = count_query.where(Transaction.date <= date_to)

        # Sorting
        sort_column = getattr(Transaction, sort_by, Transaction.date)
        order_func = desc if sort_dir == "desc" else asc
        query = query.order_by(order_func(sort_column))

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)

        return list(result.scalars().all()), total_result.scalar_one()

    async def update_status(self, tx_id: int, status: str, signature: str | None = None, error_message: str | None = None) -> None:
        tx = await self.get_by_id(tx_id)
        if tx:
            tx.status = status
            if signature:
                tx.signature = signature
            if error_message:
                tx.error_message = error_message
            await self.session.flush()
