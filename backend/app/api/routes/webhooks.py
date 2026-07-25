from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.agent.transcription import transcribe_audio_from_url
from app.agent import runner as agent_runner
from app.agent.zavu_client import send_whatsapp_message
from app.services import payment_service, booking_service
from app.schemas.payment import PaymentCreate
from app.services.payment_gateways.factory import PaymentGatewayFactory

router = APIRouter(prefix="/webhooks", tags=["Webhooks & Agente IA"])

class AgentSimRequest(BaseModel):
    sender_contact: str = Field(default="+573001234567", example="+573001234567")
    message_text: Optional[str] = Field(default=None, example="Hola, ¿tienen habitaciones disponibles del 1 al 5 de agosto?")
    audio_url: Optional[str] = Field(default=None, example="mock://audio_nota_de_voz.ogg")

@router.post("/whatsapp")
async def zavu_whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_async_db)):
    """
    Webhook oficial para recibir mensajes entrantes de WhatsApp desde Zavu.
    Procesa mensajes de texto y notas de voz automáticamente.
    """
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
        "agent_response": agent_response
    }

@router.post("/agent-sim")
async def simulate_whatsapp_message(payload: AgentSimRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Endpoint de simulación para pruebas locales y demostración en vivo.
    Permite enviar un mensaje de texto o una URL de audio sin necesidad de webhook externo.
    """
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
        "agent_response": agent_response
    }

@router.post("/payments/{provider}")
@router.get("/payments/{provider}")
async def unified_payment_webhook(
    provider: str,
    request: Request,
    booking_id: Optional[int] = None,
    monto: Optional[float] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Webhook unificado de confirmación de pago modular (Wallbit, MercadoPago, Stripe, Mock).
    
    Flujo automático:
    1. Procesa el payload según el proveedor.
    2. Registra el pago en estado CONFIRMADO.
    3. Cambia la reserva a CONFIRMADA y la habitación a OCUPADA (Rojo) en el PMS.
    4. Emite evento por WebSocket en tiempo real al frontend.
    5. Envía comprobante de reserva confirmado por WhatsApp al huésped a través de Zavu.
    """
    payload = {}
    if request.method == "POST":
        try:
            payload = await request.json()
        except Exception:
            payload = {}

    if booking_id:
        payload["booking_id"] = booking_id
    if monto:
        payload["monto"] = monto

    # Instanciar el gateway correspondiente según el proveedor usando Factory
    gateway = PaymentGatewayFactory.get_gateway(provider)
    parsed_data = gateway.parse_webhook_payload(payload)

    target_booking_id = parsed_data.get("booking_id")
    target_monto = parsed_data.get("monto")
    is_success = parsed_data.get("is_success", True)
    referencia = parsed_data.get("referencia", f"ref_{provider}_{target_booking_id}")

    if not target_booking_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falta el ID de reserva en el payload del webhook.")

    # 1. Registrar pago y actualizar estados de Reserva y Habitación
    payment_in = PaymentCreate(
        booking_id=target_booking_id,
        monto=target_monto or 100.0,
        proveedor=provider,
        referencia_externa=referencia
    )
    payment = await payment_service.record_payment(db, payment_in, is_confirmed=is_success)

    # 2. Enviar recibo de confirmación por WhatsApp si fue exitoso
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
        "booking_id": target_booking_id
    }

@router.get("/mock-pay")
async def mock_pay_alias(booking_id: int, monto: float, db: AsyncSession = Depends(get_async_db)):
    """Alias rápido de webhook para enlaces de prueba."""
    request = Request(scope={"type": "http", "method": "GET"})
    return await unified_payment_webhook("mock", request, booking_id=booking_id, monto=monto, db=db)
