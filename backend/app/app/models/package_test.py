from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base_class import Base

package_tests = Table(
    "package_tests",
    Base.metadata,
    Column("package_id", Integer, ForeignKey("packages.id", ondelete="CASCADE"), primary_key=True),
    Column("test_id", Integer, ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True),
)
