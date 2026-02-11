from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Integer, SmallInteger, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("type IN ('SOL_TO_USDC', 'USDC_TO_SOL')", name="ck_transaction_type"),
        CheckConstraint("status IN ('confirmed', 'pending', 'failed')", name="ck_transaction_status"),
        Index("ix_transactions_owner_date", "owner", "date"),
        Index("ix_transactions_owner_status", "owner", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner: Mapped[str] = mapped_column(String(44), ForeignKey("user_profiles.owner"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    type: Mapped[str] = mapped_column(String(20))
    amount_in: Mapped[int] = mapped_column(BigInteger)
    amount_out: Mapped[int] = mapped_column(BigInteger)
    token_in: Mapped[str] = mapped_column(String(44))
    token_out: Mapped[str] = mapped_column(String(44))
    slippage_bps: Mapped[int] = mapped_column(SmallInteger)
    fee: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    signature: Mapped[str | None] = mapped_column(String(88), unique=True, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    profile: Mapped["UserProfile"] = relationship(back_populates="transactions")  # noqa: F821
