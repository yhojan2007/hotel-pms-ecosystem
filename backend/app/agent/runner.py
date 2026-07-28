import logging
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.agent.tools import AGENT_TOOLS, execute_tool_call
from app.agent.zavu_client import send_whatsapp_message

logger = logging.getLogger("agent_runner")

SYSTEM_PROMPT = """
Eres el asistente virtual autónomo del Hotel Ecosistema PMS en WhatsApp.
Tu objetivo es ayudar a los huéspedes a consultar disponibilidad de habitaciones, realizar reservas y enviarles enlaces de pago.

Instrucciones:
1. Sé muy amable, profesional, atento y directo.
2. Cuando el usuario pregunte por disponibilidad o precios, DEBES llamar a la herramienta `check_room_availability` con las fechas de llegada (check-in) y salida (check-out).
3. Si el usuario confirma que desea reservar una habitación específica y te da su nombre, DEBES llamar a `create_prebooking` para registrar la pre-reserva.
4. Inmediatamente después de crear la pre-reserva, DEBES llamar a `generate_payment_link` y proporcionarle el enlace de pago al cliente.
5. Recuerda que la fecha actual de referencia es el año 2026. Si el cliente no especifica el año, asume 2026.
"""

async def process_incoming_message(
    sender_contact: str,
    message_text: str,
    db: AsyncSession
) -> str:
    """
    Procesa un mensaje recibido (texto o nota de voz transcribida),
    interactúa con Anthropic Claude usando Function/Tool Calling,
    ejecuta las herramientas necesarias y envía la respuesta al huésped por WhatsApp.
    """
    logger.info(f"Procesando mensaje de [{sender_contact}]: '{message_text}'")

    anthropic_key = settings.ANTHROPIC_API_KEY
    if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=anthropic_key)

            messages = [
                {"role": "user", "content": message_text}
            ]

            # 1. Primera llamada a Claude con herramientas
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                tools=AGENT_TOOLS,
                messages=messages
            )

            # 2. Bucle de ejecución de herramientas
            while response.stop_reason == "tool_use":
                tool_results = []
                messages.append({"role": "assistant", "content": response.content})

                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id

                        logger.info(f"Ejecutando herramienta: {tool_name} con parámetros: {tool_input}")
                        
                        # Inyectar contacto si no viene en el input
                        if tool_name == "create_prebooking" and "guest_contact" not in tool_input:
                            tool_input["guest_contact"] = sender_contact

                        result = await execute_tool_call(tool_name, tool_input, db)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })

                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Obtener la siguiente respuesta de Claude tras entregar los resultados de las herramientas
                response = await client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    system=SYSTEM_PROMPT,
                    tools=AGENT_TOOLS,
                    messages=messages
                )

            # Extraer el texto final
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response += block.text

            await send_whatsapp_message(sender_contact, final_response)
            return final_response

        except Exception as e:
            logger.error(f"Error en la llamada a Anthropic API: {e}")

    # Fallback / Simulador Inteligente sin API Key para demo inmediata
    logger.info("Ejecutando motor conversacional simulado de demostración con Tool Calling automático...")
    
    msg_lower = message_text.lower()

    if "reservar" in msg_lower or "reserva" in msg_lower or "confirmar" in msg_lower:
        availability = await execute_tool_call("check_room_availability", {
            "fecha_checkin": "2026-08-01",
            "fecha_checkout": "2026-08-05"
        }, db)
        available_rooms = availability.get("habitaciones_disponibles", [])
        if not available_rooms:
            resp_text = "Lo siento, ya no hay habitaciones disponibles para esas fechas de demo."
            await send_whatsapp_message(sender_contact, resp_text)
            return resp_text

        selected_room = available_rooms[0]

        # Simula llamada a create_prebooking y generate_payment_link
        tool_res = await execute_tool_call("create_prebooking", {
            "guest_name": "Huésped Demo",
            "guest_contact": sender_contact,
            "room_id": selected_room["id"],
            "fecha_checkin": "2026-08-01",
            "fecha_checkout": "2026-08-05"
        }, db)

        if "error" in tool_res:
            resp_text = f"Lo sentimos, ocurrió un problema: {tool_res['error']}"
        else:
            pay_res = await execute_tool_call("generate_payment_link", {
                "booking_id": tool_res["booking_id"],
                "monto": tool_res["monto_total"]
            }, db)
            resp_text = (
                f"¡Excelente noticia! He creado tu pre-reserva para la **{tool_res['habitacion']}** "
                f"a nombre de **{tool_res['huesped']}** por un total de **${tool_res['monto_total']} USD**.\n\n"
                f"La habitación se ha marcado como PENDIENTE (Amarillo) en el sistema.\n\n"
                f"Por favor completa tu pago en el siguiente enlace para confirmar la reserva:\n"
                f"👉 {pay_res['payment_link']}"
            )
    else:
        # Simula llamada a check_room_availability
        avail_res = await execute_tool_call("check_room_availability", {
            "fecha_checkin": "2026-08-01",
            "fecha_checkout": "2026-08-05"
        }, db)

        rooms_list = avail_res.get("habitaciones_disponibles", [])
        if rooms_list:
            rooms_formatted = "\n".join([
                f"• *{r['nombre']}* ({r['tipo'].capitalize()}): ${r['precio_por_noche']} USD/noche - Total: ${r['precio_total']} USD"
                for r in rooms_list[:3]
            ])
            resp_text = (
                f"¡Hola! Gracias por comunicarte con nuestro hotel. 🏨\n\n"
                f"Para las fechas del 1 al 5 de agosto de 2026, tenemos las siguientes habitaciones disponibles:\n\n"
                f"{rooms_formatted}\n\n"
                f"¿Cuál de ellas te gustaría reservar?"
            )
        else:
            resp_text = "Hola, actualmente no tenemos habitaciones disponibles para esas fechas."

    await send_whatsapp_message(sender_contact, resp_text)
    return resp_text
