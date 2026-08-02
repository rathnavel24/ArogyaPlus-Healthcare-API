from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class TestParameter(Base):
    __tablename__ = "test_parameters"

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True)
    parameter_id: Mapped[int] = mapped_column(ForeignKey("parameters.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    test: Mapped["Test"] = relationship("Test", back_populates="parameter_links")
    parameter: Mapped["Parameter"] = relationship("Parameter")
