from fastapi import APIRouter
from app.api.routes import rooms, guests, bookings, payments, webhooks

api_router = APIRouter()

api_router.include_router(rooms.router)
api_router.include_router(guests.router)
api_router.include_router(bookings.router)
api_router.include_router(payments.router)
api_router.include_router(webhooks.router)
