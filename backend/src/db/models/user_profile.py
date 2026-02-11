from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Integer, SmallInteger, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.base import Base
from src.common.constants import (
    DEFAULT_TRADE_SIZE_SOL,
    DEFAULT_TRADE_SIZE_USDC,
    DEFAULT_MIN_FEE_POOL,
    DEFAULT_TARGET_FEE_POOL,
    DEFAULT_MAX_SLIPPAGE_BPS,
    DEFAULT_PROTOCOL_FEE_BPS,
    DEFAULT_RELAYER_REFUND,
    DEFAULT_DAILY_LIMIT,
)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    owner: Mapped[str] = mapped_column(String(44), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    trade_size_sol: Mapped[int] = mapped_column(BigInteger, default=DEFAULT_TRADE_SIZE_SOL)
    trade_size_usdc: Mapped[int] = mapped_column(BigInteger, default=DEFAULT_TRADE_SIZE_USDC)
    min_fee_pool: Mapped[int] = mapped_column(BigInteger, default=DEFAULT_MIN_FEE_POOL)
    target_fee_pool: Mapped[int] = mapped_column(BigInteger, default=DEFAULT_TARGET_FEE_POOL)
    max_slippage_bps: Mapped[int] = mapped_column(SmallInteger, default=DEFAULT_MAX_SLIPPAGE_BPS)
    protocol_fee_bps: Mapped[int] = mapped_column(SmallInteger, default=DEFAULT_PROTOCOL_FEE_BPS)
    relayer_refund_lamports: Mapped[int] = mapped_column(BigInteger, default=DEFAULT_RELAYER_REFUND)
    keeper_allowlist: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    daily_limit: Mapped[int | None] = mapped_column(Integer, nullable=True, default=DEFAULT_DAILY_LIMIT)
    last_execution: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    nonce: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    vault_balance: Mapped["VaultBalance"] = relationship(back_populates="profile")  # noqa: F821
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="profile")  # noqa: F821
    pnl_snapshots: Mapped[list["PnlSnapshot"]] = relationship(back_populates="profile")  # noqa: F821
