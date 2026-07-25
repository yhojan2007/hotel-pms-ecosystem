import httpx
import logging
from app.core.config import settings

logger = logging.getLogger("zavu_client")

async def send_whatsapp_message(to_phone: str, message_text: str) -> bool:
    """
    Envía un mensaje de texto por WhatsApp a un número de destino utilizando la API de Zavu.
    Si ZAVU_API_KEY no está configurada, opera en modo MOCK imprimiendo el mensaje en logs para la demo.
    """
    if not settings.ZAVU_API_KEY or settings.ZAVU_API_KEY == "your_zavu_api_key_here":
        logger.info("==========================================================")
        logger.info(f"[MOCK ZAVU WHATSAPP SENDER] Para: {to_phone}")
        logger.info(f"Mensaje: {message_text}")
        logger.info("==========================================================")
        return True

    url = "https://api.zavu.embot.ai/v1/messages"  # URL base de la API de Zavu
    headers = {
        "Authorization": f"Bearer {settings.ZAVU_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to_phone,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if response.status_code in [200, 201, 202]:
                logger.info(f"Mensaje enviado exitosamente vía Zavu a {to_phone}")
                return True
            else:
                logger.error(f"Error de Zavu API ({response.status_code}): {response.text}")
                return False
    except Exception as e:
        logger.error(f"Excepción al conectar con la API de Zavu: {e}")
        return False
