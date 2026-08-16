import math

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def get_pagination(row_count: int = 0, current_page_no: int = 1, default_page_size: int = 10) -> list[int]:
    current_page_no = current_page_no if current_page_no >= 1 else 1

    if row_count == 0:
        return [0, 0, default_page_size]

    total_pages = math.ceil(row_count / default_page_size)

    if current_page_no > total_pages:
        current_page_no = total_pages

    limit = current_page_no * default_page_size
    offset = limit - default_page_size

    if limit > row_count:
        limit = offset + (row_count % default_page_size)

    limit = limit - offset

    if offset < 0:
        offset = 0

    return [total_pages, offset, limit]


def paginate_query(db: Session, stmt: Select, page: int = 1, page_size: int = 10) -> dict:
    """Apply get_pagination() to a SQLAlchemy 2.0 select() and return items + paging metadata.

    Not safe to use on a statement with a joinedload() of a collection relationship
    (e.g. Booking.items) — counting via a subquery would count joined rows, not parent rows.
    """
    total_rows = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    total_pages, offset, limit = get_pagination(total_rows, page, page_size)

    items = db.scalars(stmt.offset(offset).limit(limit)).all()
    current_page = 1 if total_pages == 0 else min(max(page, 1), total_pages)

    return {
        "items": items,
        "total_pages": total_pages,
        "current_page": current_page,
        "page_size": page_size,
        "total_rows": total_rows,
    }
