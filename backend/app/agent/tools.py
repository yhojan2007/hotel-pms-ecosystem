from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room, RoomStatus, RoomType
from app.schemas.guest import GuestCreate
from app.schemas.booking import BookingCreate
from app.services import room_service, guest_service, booking_service

# Definición de herramientas para Anthropic Claude (Tool Calling Schema)
AGENT_TOOLS = [
    {
        "name": "check_room_availability",
        "description": "Consulta la disponibilidad real de habitaciones en el hotel entre una fecha de check-in y check-out.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fecha_checkin": {
                    "type": "string",
                    "description": "Fecha de llegada en formato YYYY-MM-DD"
                },
                "fecha_checkout": {
                    "type": "string",
                    "description": "Fecha de salida en formato YYYY-MM-DD"
                },
                "tipo_habitacion": {
                    "type": "string",
                    "enum": ["individual", "doble", "suite", "deluxe"],
                    "description": "Tipo opcional de habitación deseada (individual, doble, suite, deluxe)"
                }
            },
            "required": ["fecha_checkin", "fecha_checkout"]
        }
    },
    {
        "name": "create_prebooking",
        "description": "Crea una pre-reserva para el huésped. Cambia automáticamente el estado de la habitación a 'pendiente' (Amarillo en el PMS) y notifica por WebSocket.",
        "input_schema": {
            "type": "object",
            "properties": {
                "guest_name": {
                    "type": "string",
                    "description": "Nombre completo del huésped"
                },
                "guest_contact": {
                    "type": "string",
                    "description": "Número de WhatsApp o teléfono del huésped con código de país"
                },
                "room_id": {
                    "type": "integer",
                    "description": "ID numérico de la habitación a reservar"
                },
                "fecha_checkin": {
                    "type": "string",
                    "description": "Fecha de entrada en formato YYYY-MM-DD"
                },
                "fecha_checkout": {
                    "type": "string",
                    "description": "Fecha de salida en formato YYYY-MM-DD"
                }
            },
            "required": ["guest_name", "guest_contact", "room_id", "fecha_checkin", "fecha_checkout"]
        }
    },
    {
        "name": "generate_payment_link",
        "description": "Genera un enlace de pago seguro para que el huésped confirme su reserva.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {
                    "type": "integer",
                    "description": "ID de la reserva creada"
                },
                "monto": {
                    "type": "number",
                    "description": "Monto total a pagar"
                }
            },
            "required": ["booking_id", "monto"]
        }
    }
]

async def execute_tool_call(tool_name: str, tool_input: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """Ejecuta la función del backend asociada al Tool Call invocado por Claude."""
    
    if tool_name == "check_room_availability":
        try:
            checkin = date.fromisoformat(tool_input["fecha_checkin"])
            checkout = date.fromisoformat(tool_input["fecha_checkout"])
        except ValueError:
            return {"error": "Formato de fecha inválido. Utiliza YYYY-MM-DD."}

        all_rooms = await room_service.get_all_rooms(db)
        available_rooms = []

        for room in all_rooms:
            # Filtrar por tipo si se especifica
            if tool_input.get("tipo_habitacion") and room.tipo.value != tool_input["tipo_habitacion"]:
                continue

            # Verificar si la habitación no está ocupada y no tiene reservas solapadas
            is_avail = await booking_service.check_room_availability(db, room.id, checkin, checkout)
            if is_avail and room.estado == RoomStatus.DISPONIBLE:
                nights = (checkout - checkin).days
                total_price = float(room.precio_base) * max(nights, 1)
                available_rooms.append({
                    "id": room.id,
                    "nombre": room.nombre,
                    "tipo": room.tipo.value,
                    "precio_por_noche": float(room.precio_base),
                    "noches": nights,
                    "precio_total": total_price,
                    "estado": room.estado.value
                })

        return {
            "habitaciones_disponibles": available_rooms,
            "total_encontradas": len(available_rooms)
        }

    elif tool_name == "create_prebooking":
        try:
            checkin = date.fromisoformat(tool_input["fecha_checkin"])
            checkout = date.fromisoformat(tool_input["fecha_checkout"])
        except ValueError:
            return {"error": "Formato de fecha inválido."}

        room = await room_service.get_room_by_id(db, tool_input["room_id"])
        if not room:
            return {"error": f"La habitación con ID {tool_input['room_id']} no existe."}

        # 1. Crear o recuperar el huésped
        guest = await guest_service.create_guest(
            db, GuestCreate(nombre=tool_input["guest_name"], contacto=tool_input["guest_contact"])
        )

        nights = (checkout - checkin).days
        total_monto = float(room.precio_base) * max(nights, 1)

        # 2. Crear reserva
        try:
            booking = await booking_service.create_booking(
                db,
                BookingCreate(
                    room_id=room.id,
                    guest_id=guest.id,
                    fecha_checkin=checkin,
                    fecha_checkout=checkout,
                    monto=total_monto
                )
            )
        except ValueError as e:
            return {"error": str(e)}

        return {
            "status": "success",
            "booking_id": booking.id,
            "habitacion": room.nombre,
            "huesped": guest.nombre,
            "monto_total": total_monto,
            "estado_reserva": booking.estado.value,
            "mensaje": "Pre-reserva creada. La habitación cambió a PENDIENTE (Amarillo) en el PMS."
        }

    elif tool_name == "generate_payment_link":
        booking_id = tool_input["booking_id"]
        monto = tool_input["monto"]
        provider = tool_input.get("proveedor", "mock")

        from app.services.payment_gateways.factory import PaymentGatewayFactory
        gateway = PaymentGatewayFactory.get_gateway(provider)
        payment_info = gateway.create_payment_link(
            booking_id=booking_id,
            monto=monto,
            descripcion=f"Reserva Hotel PMS #{booking_id}"
        )

        return {
            "booking_id": booking_id,
            "monto": monto,
            "payment_link": payment_info["payment_url"],
            "proveedor": provider,
            "instrucciones": "Envía este enlace de pago al cliente por WhatsApp."
        }

    return {"error": f"Herramienta '{tool_name}' no implementada."}
