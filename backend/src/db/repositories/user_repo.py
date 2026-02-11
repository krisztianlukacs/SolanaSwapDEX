from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user_profile import UserProfile


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_owner(self, owner: str) -> UserProfile | None:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.owner == owner)
        )
        return result.scalar_one_or_none()

    async def create(self, owner: str, **kwargs) -> UserProfile:
        profile = UserProfile(owner=owner, **kwargs)
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_or_create(self, owner: str) -> UserProfile:
        profile = await self.get_by_owner(owner)
        if profile is None:
            profile = await self.create(owner)
        return profile

    async def update(self, owner: str, **kwargs) -> UserProfile | None:
        kwargs["updated_at"] = datetime.now(timezone.utc)
        await self.session.execute(
            update(UserProfile).where(UserProfile.owner == owner).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_owner(owner)

    async def get_enabled_users(self) -> list[UserProfile]:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.enabled.is_(True))
        )
        return list(result.scalars().all())

    async def update_last_execution(self, owner: str, timestamp: datetime) -> None:
        await self.session.execute(
            update(UserProfile)
            .where(UserProfile.owner == owner)
            .values(last_execution=timestamp, nonce=UserProfile.nonce + 1)
        )
        await self.session.flush()
