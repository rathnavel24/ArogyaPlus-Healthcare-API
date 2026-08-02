import logging
import random
import string
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingItem
from app.models.package import Package
from app.models.test import Test
from app.schemas.booking import BookingCreate
from app.services.whatsapp_service import whatsapp_service

logger = logging.getLogger("arogyaplus.booking")


def _generate_booking_reference() -> str:
    stamp = datetime.utcnow().strftime("%y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"AP-{stamp}-{suffix}"


def create_booking(db: Session, booking_in: BookingCreate) -> Booking:
    booking_items: list[BookingItem] = []
    total_amount = 0

    for entry in booking_in.items:
        if entry.item_type == "package":
            record = db.get(Package, entry.item_id)
        else:
            record = db.get(Test, entry.item_id)

        if record is None or not record.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Selected {entry.item_type} is no longer available.",
            )

        price = record.home_price if booking_in.visit_mode == "home" else record.lab_price
        total_amount += price

        booking_items.append(
            BookingItem(
                item_type=entry.item_type,
                item_id=record.id,
                item_name=record.name,
                price=price,
                quantity=1,
            )
        )

    booking = Booking(
        booking_reference=_generate_booking_reference(),
        customer_name=booking_in.customer_name,
        age=booking_in.age,
        gender=booking_in.gender,
        phone=booking_in.phone,
        email=booking_in.email,
        address=booking_in.address,
        preferred_date=booking_in.preferred_date,
        time_slot=booking_in.time_slot,
        visit_mode=booking_in.visit_mode,
        total_amount=total_amount,
        status="New",
        items=booking_items,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    try:
        whatsapp_service.send_booking_notification(booking)
    except Exception:
        logger.exception("WhatsApp notification failed for booking %s", booking.booking_reference)

    return booking
