from sqlalchemy import Boolean, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BroodstockCage(Base):
    __tablename__ = "broodstock_cages"
    __table_args__ = (
        UniqueConstraint("hatchery_id", "cage_code", name="uq_hatchery_cage_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hatchery_id: Mapped[int] = mapped_column(ForeignKey("hatcheries.id"), nullable=False, index=True)
    cage_code: Mapped[str] = mapped_column(String(64), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    occupied: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    hatchery: Mapped["Hatchery"] = relationship("Hatchery", back_populates="cages")
