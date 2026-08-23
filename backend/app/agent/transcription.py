"""Transcripción de notas de voz (Whisper o texto fijo de demo)."""

import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("transcription")


async def transcribe_audio_from_url(audio_url: str) -> Optional[str]:
    """Convierte audio de WhatsApp/Zavu a texto.

    Con ``OPENAI_API_KEY`` y URL real usa Whisper. URLs ``mock://`` o fallos
    devuelven una frase de demo en español.
    """
    logger.info(f"Procesando transcripción de audio desde URL: {audio_url}")
    openai_key = settings.OPENAI_API_KEY

    if openai_key and not audio_url.startswith("mock://"):
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=openai_key)

            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(audio_url)
                audio_bytes = response.content

            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=("voice_note.ogg", audio_bytes, "audio/ogg"),
                language="es",
            )
            logger.info(f"Transcripción exitosa con Whisper: '{transcript.text}'")
            return transcript.text
        except Exception as e:
            logger.error(f"Error al transcribir con OpenAI Whisper: {e}")

    logger.info("Usando motor de transcripción simulado para demo.")
    return "Hola, quisiera consultar disponibilidad de una habitación suite para dos personas del 1 al 5 de agosto."
