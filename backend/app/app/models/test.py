from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.package_test import package_tests


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    lab_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    home_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    original_lab_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    original_home_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    tat: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    status: Mapped[int] = mapped_column(Integer, default=1,comment="1: Active, 2: Inactive, -1: Deleted")  # 1: Active, 2: inactive,-1 deleted
    

    packages = relationship("Package", secondary=package_tests, back_populates="tests")
