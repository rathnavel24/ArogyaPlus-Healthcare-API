"""
WhatsApp notification service abstraction.

ArogyaPlus sends a WhatsApp message to the clinic's destination number whenever a
new booking is created. The concrete provider (Meta WhatsApp Cloud API, Twilio,
or any other vendor) is fully configured through environment variables, so it
can be swapped without touching booking logic.

To wire up a real provider:
  1. Implement a class with the same `send(to, message) -> bool` signature as
     `MetaCloudAPIProvider` below (e.g. `TwilioProvider`).
  2. Update `WhatsAppService._build_provider` to select it based on config.
  3. Set the relevant environment variables in `.env`.

If the provider is not configured, notifications are skipped (logged only) so
that a booking is never lost because of a messaging failure.
"""

import logging
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings
from app.models.booking import Booking

logger = logging.getLogger("arogyaplus.whatsapp")


class NotificationProvider(ABC):
    """Common interface every WhatsApp provider implementation must follow."""

    @abstractmethod
    def send(self, to: str, message: str) -> bool:
        raise NotImplementedError


class MetaCloudAPIProvider(NotificationProvider):
    """Sends messages via the Meta WhatsApp Cloud API."""

    def __init__(self, api_url: str, access_token: str, phone_number_id: str):
        self.api_url = api_url.rstrip("/")
        self.access_token = access_token
        self.phone_number_id = phone_number_id

    def send(self, to: str, message: str) -> bool:
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            return True
        except httpx.HTTPError as exc:
            logger.warning("WhatsApp notification failed: %s", exc)
            return False


class NullProvider(NotificationProvider):
    """Used when no WhatsApp provider is configured yet."""

    def send(self, to: str, message: str) -> bool:
        logger.info("WhatsApp not configured - skipped notification to %s: %s", to, message)
        return False


class WhatsAppService:
    def __init__(self):
        self.destination_number = settings.WHATSAPP_DESTINATION_NUMBER
        self.provider = self._build_provider()

    def _build_provider(self) -> NotificationProvider:
        if settings.WHATSAPP_API_URL and settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID:
            return MetaCloudAPIProvider(
                api_url=settings.WHATSAPP_API_URL,
                access_token=settings.WHATSAPP_ACCESS_TOKEN,
                phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
            )
        return NullProvider()

    def is_configured(self) -> bool:
        return not isinstance(self.provider, NullProvider) and bool(self.destination_number)

    def send_booking_notification(self, booking: Booking) -> bool:
        if not self.destination_number:
            logger.info("WHATSAPP_DESTINATION_NUMBER not set - skipped booking notification.")
            return False

        item_lines = "\n".join(f"- {item.item_name} (AED {item.price})" for item in booking.items)
        message = (
            f"New ArogyaPlus booking received!\n\n"
            f"Reference: {booking.booking_reference}\n"
            f"Customer: {booking.customer_name} ({booking.age}, {booking.gender})\n"
            f"Phone: {booking.phone}\n"
            f"Visit mode: {booking.visit_mode}\n"
            f"Date: {booking.preferred_date} at {booking.time_slot}\n"
            f"Total: AED {booking.total_amount}\n\n"
            f"Items:\n{item_lines}"
        )

        try:
            success = self.provider.send(self.destination_number, message)
        except Exception:
            logger.exception("Unexpected error sending WhatsApp notification.")
            return False

        if success:
            logger.info("WhatsApp notification sent for booking %s", booking.booking_reference)
        else:
            logger.warning("WhatsApp notification not sent for booking %s", booking.booking_reference)
        return success

    def send_test_message(self) -> bool:
        if not self.destination_number:
            return False
        return self.provider.send(self.destination_number, "This is a test message from ArogyaPlus Healthcare.")


whatsapp_service = WhatsAppService()
