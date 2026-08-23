"""Rutas REST de huéspedes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.schemas.guest import GuestCreate, GuestResponse
from app.services import guest_service

router = APIRouter(prefix="/guests", tags=["Huéspedes"])


@router.get("", response_model=List[GuestResponse])
async def list_guests(db: AsyncSession = Depends(get_async_db)) -> List[GuestResponse]:
    """Lista todos los huéspedes registrados."""
    return await guest_service.get_all_guests(db)


@router.get("/by-contact/{contacto}", response_model=GuestResponse)
async def get_guest_by_contact(contacto: str, db: AsyncSession = Depends(get_async_db)) -> GuestResponse:
    """Busca un huésped por teléfono / WhatsApp."""
    guest = await guest_service.get_guest_by_contacto(db, contacto)
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Huésped no registrado")
    return guest


@router.get("/{guest_id}", response_model=GuestResponse)
async def get_guest(guest_id: int, db: AsyncSession = Depends(get_async_db)) -> GuestResponse:
    """Devuelve un huésped por ID o 404."""
    guest = await guest_service.get_guest_by_id(db, guest_id)
    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Huésped no encontrado")
    return guest


@router.post("", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
async def create_guest(guest_in: GuestCreate, db: AsyncSession = Depends(get_async_db)) -> GuestResponse:
    """Crea el huésped o reutiliza el existente con el mismo contacto."""
    return await guest_service.create_guest(db, guest_in)
