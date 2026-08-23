"""Gestor de conexiones WebSocket y emisión de eventos al dashboard PMS."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import WebSocket

logger = logging.getLogger("ws_manager")


class ConnectionManager:
    """Registro en memoria de clientes WebSocket activos (proceso único)."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Acepta el handshake y registra el cliente."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"Nuevo cliente WebSocket conectado. Total activos: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Quita el cliente de la lista si sigue registrado."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"Cliente WebSocket desconectado. Total activos: {len(self.active_connections)}"
            )

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Envía un mensaje JSON a todos los clientes; limpia sockets rotos."""
        disconnected_clients: List[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error al enviar mensaje por WebSocket: {e}")
                disconnected_clients.append(connection)

        for client in disconnected_clients:
            self.disconnect(client)


manager = ConnectionManager()


async def notify_room_status_change(room_data: Dict[str, Any]) -> None:
    """Emite ``room_status_updated`` con el payload de la habitación."""
    payload: Dict[str, Any] = {
        "event": "room_status_updated",
        "data": room_data,
    }
    await manager.broadcast(payload)
