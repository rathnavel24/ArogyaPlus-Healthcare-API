from fastapi import APIRouter

from app.api.endpoints import auth, banners, bookings, notifications, packages, site_content, tests, uploads

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(packages.public_router)
api_router.include_router(packages.admin_router)
api_router.include_router(tests.public_router)
api_router.include_router(tests.admin_router)
api_router.include_router(bookings.public_router)
api_router.include_router(bookings.admin_router)
api_router.include_router(bookings.dashboard_router)
api_router.include_router(notifications.router)
api_router.include_router(site_content.public_router)
api_router.include_router(site_content.admin_router)
api_router.include_router(banners.public_router)
api_router.include_router(banners.admin_router)
api_router.include_router(uploads.router)
