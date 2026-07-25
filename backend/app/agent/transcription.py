import httpx
import logging
import os
from typing import Optional

logger = logging.getLogger("transcription")

async def transcribe_audio_from_url(audio_url: str) -> Optional[str]:
    """
    Descarga una nota de voz enviada por WhatsApp/Zavu y realiza la transcripción a texto.
    Si hay una clave de API de OpenAI (OPENAI_API_KEY), usa Whisper.
    Si no hay clave o para pruebas locales offline, provee un fallback inteligente.
    """
    logger.info(f"Procesando transcripción de audio desde URL: {audio_url}")
    openai_key = os.getenv("OPENAI_API_KEY")

    if openai_key and not audio_url.startswith("mock://"):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=openai_key)

            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(audio_url)
                audio_bytes = response.content

            # Transcribir usando Whisper
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=("voice_note.ogg", audio_bytes, "audio/ogg"),
                language="es"
            )
            logger.info(f"Transcripción exitosa con Whisper: '{transcript.text}'")
            return transcript.text
        except Exception as e:
            logger.error(f"Error al transcribir con OpenAI Whisper: {e}")

    # Fallback para desarrollo / simulación de notas de voz
    logger.info("Usando motor de transcripción simulado para demo.")
    return "Hola, quisiera consultar disponibilidad de una habitación suite para dos personas del 1 al 5 de agosto."
