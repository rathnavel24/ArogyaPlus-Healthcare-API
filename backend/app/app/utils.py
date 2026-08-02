import math

from sqlalchemy.orm import Query


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


def paginate_query(query: Query, page: int = 1, page_size: int = 10) -> dict:
    """Apply get_pagination() to a SQLAlchemy query and return items + paging metadata.

    Not safe to use on a query with a joinedload() of a collection relationship
    (e.g. Booking.items) — count() would count joined rows, not parent rows.
    """
    total_rows = query.count()
    total_pages, offset, limit = get_pagination(total_rows, page, page_size)

    items = query.offset(offset).limit(limit).all()
    current_page = 1 if total_pages == 0 else min(max(page, 1), total_pages)

    return {
        "items": items,
        "total_pages": total_pages,
        "current_page": current_page,
        "page_size": page_size,
        "total_rows": total_rows,
    }
