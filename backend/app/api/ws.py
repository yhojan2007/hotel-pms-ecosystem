from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger("ws_manager")

class ConnectionManager:
    def __init__(self):
        # Lista de clientes WebSocket activos
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nuevo cliente WebSocket conectado. Total activos: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Cliente WebSocket desconectado. Total activos: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Envía un mensaje JSON a todos los clientes WebSocket conectados en tiempo real."""
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error al enviar mensaje por WebSocket: {e}")
                disconnected_clients.append(connection)

        # Limpiar conexiones cerradas inesperadamente
        for client in disconnected_clients:
            self.disconnect(client)

manager = ConnectionManager()

async def notify_room_status_change(room_data: Dict[str, Any]):
    """Helper global para emitir evento de actualización de habitación a todo el frontend."""
    payload = {
        "event": "room_status_updated",
        "data": room_data
    }
    await manager.broadcast(payload)
