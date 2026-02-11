from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.db.base import Base


class PnlSnapshot(Base):
    __tablename__ = "pnl_snapshots"
    __table_args__ = (
        UniqueConstraint("owner", "date", name="uq_pnl_owner_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner: Mapped[str] = mapped_column(String(44), ForeignKey("user_profiles.owner"))
    date: Mapped[date] = mapped_column(Date)
    daily_pnl: Mapped[float] = mapped_column(Numeric(18, 2))
    cumulative_pnl: Mapped[float] = mapped_column(Numeric(18, 2))
    daily_sol_pnl: Mapped[float] = mapped_column(Numeric(18, 9))
    cumulative_sol_pnl: Mapped[float] = mapped_column(Numeric(18, 9))
    daily_usdc_pnl: Mapped[float] = mapped_column(Numeric(18, 6))
    cumulative_usdc_pnl: Mapped[float] = mapped_column(Numeric(18, 6))
    sol_price: Mapped[float] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    profile: Mapped["UserProfile"] = relationship(back_populates="pnl_snapshots")  # noqa: F821
