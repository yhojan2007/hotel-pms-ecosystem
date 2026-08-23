"""Agregador de routers REST de la API v1."""

from fastapi import APIRouter

from app.api.routes import bookings, guests, payments, rooms, webhooks

api_router = APIRouter()

api_router.include_router(rooms.router)
api_router.include_router(guests.router)
api_router.include_router(bookings.router)
api_router.include_router(payments.router)
api_router.include_router(webhooks.router)
