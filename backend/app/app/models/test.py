from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.package_test import package_tests
from app.models.parameter import Parameter
from app.models.test_parameter import TestParameter


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    sample_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lab_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    home_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    original_lab_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    original_home_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    tat: Mapped[str | None] = mapped_column(String(50), nullable=True)
    test_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    b2b_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    mrp: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    parameters_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tube1: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tube2: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tube3: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tube4: Mapped[str | None] = mapped_column(String(50), nullable=True)
    included_items: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    status: Mapped[int] = mapped_column(Integer, default=1,comment="1: Active, 2: Inactive, -1: Deleted")  # 1: Active, 2: inactive,-1 deleted


    packages = relationship("Package", secondary=package_tests, back_populates="tests")
    parameter_links: Mapped[list["TestParameter"]] = relationship(
        "TestParameter",
        back_populates="test",
        order_by="TestParameter.position",
        cascade="all, delete-orphan",
    )

    @property
    def parameters(self) -> list["Parameter"]:
        return [link.parameter for link in self.parameter_links]
