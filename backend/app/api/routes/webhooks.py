from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.agent.transcription import transcribe_audio_from_url
from app.agent import runner as agent_runner
from app.services import payment_service
from app.schemas.payment import PaymentCreate

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
    
    # Extraer campos estándar del payload de Zavu / WhatsApp API
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

    # Disparar la lógica autónoma del agente de IA
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

@router.get("/mock-pay")
async def mock_payment_webhook(booking_id: int, monto: float, db: AsyncSession = Depends(get_async_db)):
    """
    Webhook / Link de simulación de pago.
    Al acceder a este enlace o ser invocado por la pasarela de pago,
    impacta la base de datos, cambia la habitación a 'ocupada' (Rojo)
    y notifica inmediatamente por WebSocket al PMS en tiempo real.
    """
    payment_in = PaymentCreate(
        booking_id=booking_id,
        monto=monto,
        proveedor="mock_gateway",
        referencia_externa=f"ref_pay_{booking_id}"
    )
    payment = await payment_service.record_payment(db, payment_in, is_confirmed=True)

    return {
        "status": "success",
        "message": "¡Pago confirmado! La reserva ha sido confirmada y la habitación cambió a OCUPADA (Rojo) en el PMS.",
        "payment": payment
    }
