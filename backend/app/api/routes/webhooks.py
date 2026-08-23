"""Webhooks de WhatsApp, simulador de demo y confirmación de pagos."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import runner as agent_runner
from app.agent.transcription import transcribe_audio_from_url
from app.agent.zavu_client import send_whatsapp_message
from app.core.config import settings
from app.db.session import get_async_db
from app.schemas.payment import PaymentCreate
from app.services import booking_service, payment_service
from app.services.payment_gateways.factory import PaymentGatewayFactory

router = APIRouter(prefix="/webhooks", tags=["Webhooks & Agente IA"])


class AgentSimRequest(BaseModel):
    """Cuerpo del simulador local (drawer del frontend)."""

    sender_contact: str = Field(default="+573001234567", example="+573001234567")
    message_text: Optional[str] = Field(
        default=None,
        example="Hola, ¿tienen habitaciones disponibles del 1 al 5 de agosto?",
    )
    audio_url: Optional[str] = Field(default=None, example="mock://audio_nota_de_voz.ogg")


@router.post("/whatsapp")
async def zavu_whatsapp_webhook(
    request: Request, db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Recibe mensajes de Zavu (texto o audio) y los pasa al agente."""
    payload = await request.json()

    sender_contact = payload.get("from") or payload.get("sender", {}).get("phone", "+573000000000")
    message_type = payload.get("type", "text")

    text_to_process = ""

    if message_type == "audio" or "audio" in payload:
        audio_url = payload.get("audio", {}).get("url") or payload.get("media_url", "mock://voice")
        transcription = await transcribe_audio_from_url(audio_url)
        text_to_process = transcription or "Solicitud por nota de voz no comprendida."
    else:
        text_to_process = payload.get("text", {}).get("body") or payload.get("message", {}).get("text", "")

    if not text_to_process:
        return {"status": "ignored", "reason": "No text content found"}

    agent_response = await agent_runner.process_incoming_message(sender_contact, text_to_process, db)
    return {
        "status": "success",
        "processed_text": text_to_process,
        "agent_response": agent_response,
    }


@router.post("/agent-sim")
async def simulate_whatsapp_message(
    payload: AgentSimRequest, db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Simula un mensaje de WhatsApp sin webhook externo (demo / tests locales)."""
    text_to_process = payload.message_text

    if payload.audio_url or not text_to_process:
        audio_url = payload.audio_url or "mock://audio_demo"
        text_to_process = await transcribe_audio_from_url(audio_url)

    agent_response = await agent_runner.process_incoming_message(
        payload.sender_contact, text_to_process, db
    )

    return {
        "status": "success",
        "sender": payload.sender_contact,
        "input_message": text_to_process,
        "agent_response": agent_response,
    }


@router.post("/payments/{provider}")
@router.get("/payments/{provider}")
async def unified_payment_webhook(
    provider: str,
    request: Request,
    booking_id: Optional[int] = None,
    monto: Optional[float] = None,
    db: AsyncSession = Depends(get_async_db),
) -> Dict[str, Any]:
    """Confirma un pago (Wallbit, MercadoPago, Stripe o mock) y actualiza el PMS.

    Flujo:
    1. Valida secreto (excepto provider ``mock``).
    2. Normaliza el payload con la factory de pasarelas.
    3. Registra el pago y sincroniza reserva + habitación.
    4. Envía comprobante por WhatsApp si hay huésped.
    """
    if settings.PAYMENT_WEBHOOK_SECRET and provider.lower() != "mock":
        provided_secret = (
            request.headers.get("x-webhook-secret")
            or request.headers.get("x-payment-webhook-secret")
            or request.headers.get("authorization", "").replace("Bearer ", "")
        )
        if provided_secret != settings.PAYMENT_WEBHOOK_SECRET:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Webhook no autorizado.")

    payload: Dict[str, Any] = {}
    if request.method == "POST":
        try:
            payload = await request.json()
        except Exception:
            payload = {}

    if booking_id:
        payload["booking_id"] = booking_id
    if monto:
        payload["monto"] = monto

    gateway = PaymentGatewayFactory.get_gateway(provider)
    parsed_data = gateway.parse_webhook_payload(payload)

    target_booking_id = parsed_data.get("booking_id")
    target_monto = parsed_data.get("monto")
    is_success = parsed_data.get("is_success", True)
    referencia = parsed_data.get("referencia", f"ref_{provider}_{target_booking_id}")

    if not target_booking_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falta el ID de reserva en el payload del webhook.",
        )

    payment_in = PaymentCreate(
        booking_id=target_booking_id,
        monto=target_monto or 100.0,
        proveedor=provider,
        referencia_externa=referencia,
    )
    payment = await payment_service.record_payment(db, payment_in, is_confirmed=is_success)

    booking = await booking_service.get_booking_by_id(db, target_booking_id)
    if is_success and booking and booking.guest:
        whatsapp_receipt = (
            f"🎉 *¡PAGO CONFIRMADO EXITOSAMENTE!* 🎉\n\n"
            f"Estimado/a *{booking.guest.nombre}*,\n"
            f"Hemos recibido tu pago de *${payment.monto} USD* a través de *{provider.upper()}*.\n\n"
            f"📌 *Detalles de tu Reserva #{booking.id}*:\n"
            f"• Habitación: *{booking.room.nombre}* ({booking.room.tipo.capitalize()})\n"
            f"• Check-in: *{booking.fecha_checkin}*\n"
            f"• Check-out: *{booking.fecha_checkout}*\n"
            f"• Referencia de Pago: `{referencia}`\n\n"
            f"Tu habitación se encuentra lista. ¡Te esperamos en nuestro hotel! 🏨✨"
        )
        await send_whatsapp_message(booking.guest.contacto, whatsapp_receipt)

    return {
        "status": "success",
        "provider": provider,
        "is_confirmed": is_success,
        "message": f"Pago procesado por {provider.upper()}. Habitación marcada como OCUPADA (Rojo) en el PMS.",
        "payment_id": payment.id,
        "booking_id": target_booking_id,
    }


@router.get("/mock-pay")
async def mock_pay_alias(
    booking_id: Optional[int] = None,
    monto: Optional[float] = None,
    db: AsyncSession = Depends(get_async_db),
) -> Dict[str, Any]:
    """Atajo GET para confirmar la última reserva pendiente (enlaces de demo)."""
    if booking_id is None:
        latest_pending = await booking_service.get_latest_pending_booking(db)
        if not latest_pending:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay reservas pendientes para confirmar.",
            )
        booking_id = latest_pending.id
        monto = float(latest_pending.monto)

    request = Request(scope={"type": "http", "method": "GET"})
    return await unified_payment_webhook("mock", request, booking_id=booking_id, monto=monto, db=db)
