"""Import all models here so Alembic autogenerate can discover them via Base.metadata."""

from app.db.base_class import Base  # noqa: F401
from app.models.admin import Admin  # noqa: F401
from app.models.package import Package  # noqa: F401
from app.models.test import Test  # noqa: F401
from app.models.package_test import package_tests  # noqa: F401
from app.models.booking import Booking, BookingItem  # noqa: F401
from app.models.site_content import SiteContent  # noqa: F401
from app.models.banner import Banner  # noqa: F401
