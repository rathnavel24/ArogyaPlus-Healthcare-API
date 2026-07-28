from fastapi import APIRouter, Depends

from app.core.security import get_current_admin
from app.models.admin import Admin
from app.services.whatsapp_service import whatsapp_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/whatsapp/test")
def send_test_whatsapp_message(current_admin: Admin = Depends(get_current_admin)):
    sent = whatsapp_service.send_test_message()
    return {
        "sent": sent,
        "configured": whatsapp_service.is_configured(),
        "message": "Test message sent." if sent else "WhatsApp provider is not configured or the message failed.",
    }
