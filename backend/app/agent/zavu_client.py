"""Cliente de envío de WhatsApp vía Zavu (o log mock si no hay API key)."""

import logging
from uuid import uuid4

from app.core.config import settings

logger = logging.getLogger("zavu_client")


async def send_whatsapp_message(to_phone: str, message_text: str) -> bool:
    """Envía texto por WhatsApp.

    Sin ``ZAVU_API_KEY`` / ``ZAVUDEV_API_KEY`` (o con el placeholder del
    ``.env.example``) solo escribe el mensaje en logs y retorna ``True``.
    """
    api_key = settings.ZAVUDEV_API_KEY or settings.ZAVU_API_KEY

    if not api_key or api_key == "your_zavu_api_key_here":
        logger.info("==========================================================")
        logger.info(f"[MOCK ZAVU WHATSAPP SENDER] Para: {to_phone}")
        logger.info(f"Mensaje: {message_text}")
        logger.info("==========================================================")
        return True

    try:
        from zavudev import AsyncZavudev

        async with AsyncZavudev(api_key=api_key, timeout=20.0, max_retries=2) as client:
            send_params: dict[str, str] = {
                "to": to_phone,
                "text": message_text,
                "channel": "whatsapp",
                "idempotency_key": f"hotel-pms-{uuid4()}",
            }
            if settings.ZAVU_PHONE_NUMBER_ID:
                send_params["zavu_sender"] = settings.ZAVU_PHONE_NUMBER_ID

            response = await client.messages.send(**send_params)
            logger.info(f"Mensaje enviado exitosamente vía Zavu a {to_phone}: {response.message.id}")
            return True
    except Exception as e:
        logger.error(f"Excepción al conectar con la API de Zavu: {e}")
        return False
