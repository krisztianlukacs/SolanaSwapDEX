from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.base import Base


class VaultBalance(Base):
    __tablename__ = "vault_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner: Mapped[str] = mapped_column(
        String(44), ForeignKey("user_profiles.owner"), unique=True
    )
    sol_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    usdc_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    fee_pool_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    profile: Mapped["UserProfile"] = relationship(back_populates="vault_balance")  # noqa: F821
