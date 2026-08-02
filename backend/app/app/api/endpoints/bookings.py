from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.models.booking import Booking
from app.models.package import Package
from app.models.test import Test
from app.schemas.booking import BookingCreate, BookingCreatedOut, BookingOut, BookingStatusUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.booking_service import create_booking
from app.utils import get_pagination

public_router = APIRouter(prefix="/api/bookings", tags=["bookings"])
admin_router = APIRouter(prefix="/api/admin/bookings", tags=["admin-bookings"])
dashboard_router = APIRouter(prefix="/api/admin/dashboard", tags=["admin-dashboard"])


@public_router.post("", response_model=BookingCreatedOut, status_code=status.HTTP_201_CREATED)
def submit_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    try:
        booking = create_booking(db, payload)
    except HTTPException:
        raise
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return BookingCreatedOut(
        booking_reference=booking.booking_reference,
        total_amount=booking.total_amount,
        status=booking.status,
    )


@admin_router.get("", response_model=PaginatedResponse[BookingOut])
def admin_list_bookings(
    status_filter: Literal["New", "Contacted", "Done"] | None = None,
    booking_date: date | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    query = db.query(Booking)

    if status_filter:
        query = query.filter(Booking.status == status_filter)
    if booking_date:
        query = query.filter(Booking.preferred_date == booking_date)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Booking.customer_name.ilike(like))
            | (Booking.phone.ilike(like))
            | (Booking.email.ilike(like))
            | (Booking.booking_reference.ilike(like))
        )

    query = query.order_by(Booking.created_at.desc())

    # Counted before the joinedload is added — Booking.items is a collection, and
    # counting a joined collection would count booking+item combinations, not bookings.
    total_rows = query.count()
    total_pages, offset, limit = get_pagination(total_rows, page, page_size)

    items = query.options(joinedload(Booking.items)).offset(offset).limit(limit).all()
    current_page = 1 if total_pages == 0 else min(max(page, 1), total_pages)

    return {
        "items": items,
        "total_pages": total_pages,
        "current_page": current_page,
        "page_size": page_size,
        "total_rows": total_rows,
    }


@admin_router.get("/{booking_id}", response_model=BookingOut)
def admin_get_booking(
    booking_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return booking


@admin_router.patch("/{booking_id}/status", response_model=BookingOut)
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    booking.status = payload.status
    db.commit()
    db.refresh(booking)
    return booking


@dashboard_router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    total_packages = db.query(Package).count()
    total_tests = db.query(Test).count()
    total_bookings = db.query(Booking).count()
    new_bookings = db.query(Booking).filter(Booking.status == "New").count()
    contacted_bookings = db.query(Booking).filter(Booking.status == "Contacted").count()
    done_bookings = db.query(Booking).filter(Booking.status == "Done").count()

    recent_bookings = (
        db.query(Booking).options(joinedload(Booking.items)).order_by(Booking.created_at.desc()).limit(5).all()
    )

    return {
        "total_packages": total_packages,
        "total_tests": total_tests,
        "total_bookings": total_bookings,
        "new_bookings": new_bookings,
        "status_summary": {
            "New": new_bookings,
            "Contacted": contacted_bookings,
            "Done": done_bookings,
        },
        "recent_bookings": [BookingOut.model_validate(b) for b in recent_bookings],
    }
