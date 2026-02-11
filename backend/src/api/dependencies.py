from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


async def get_current_user_wallet(
    x_wallet_address: str = Header(..., description="Solana wallet address"),
) -> str:
    if not x_wallet_address or len(x_wallet_address) < 32 or len(x_wallet_address) > 44:
        raise HTTPException(status_code=401, detail="Invalid wallet address")
    return x_wallet_address
