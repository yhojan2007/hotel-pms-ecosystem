'use client';

import { useState, useEffect, useCallback } from 'react';
import { Room, fetchRooms } from '@/lib/api';

export function useRealtimeRooms() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastUpdatedRoomId, setLastUpdatedRoomId] = useState<number | null>(null);

  // Carga inicial de habitaciones por REST
  const loadInitialRooms = useCallback(async () => {
    const data = await fetchRooms();
    setRooms(data);
  }, []);

  useEffect(() => {
    loadInitialRooms();

    // Establecer conexión WebSocket nativa con FastAPI
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL
      || `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/rooms`;
    let socket: WebSocket | null = null;
    let reconnectTimer: NodeJS.Timeout;

    const connectWebSocket = () => {
      try {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          console.log('[WebSocket] Conectado exitosamente al PMS');
          setIsConnected(true);
        };

        socket.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data);
            if (payload.event === 'room_status_updated' && payload.data) {
              const updatedRoom: Room = payload.data;
              console.log('[WebSocket] Evento recibido:', updatedRoom);

              setRooms((prevRooms) =>
                prevRooms.map((room) =>
                  room.id === updatedRoom.id
                    ? { ...room, estado: updatedRoom.estado, updated_at: updatedRoom.updated_at }
                    : room
                )
              );

              setLastUpdatedRoomId(updatedRoom.id);
              setTimeout(() => setLastUpdatedRoomId(null), 1500);
            }
          } catch (err) {
            console.error('[WebSocket] Error al procesar mensaje:', err);
          }
        };

        socket.onerror = (error) => {
          console.error('[WebSocket] Error de conexión:', error);
          setIsConnected(false);
        };

        socket.onclose = () => {
          console.warn('[WebSocket] Desconectado. Reintentando en 3s...');
          setIsConnected(false);
          reconnectTimer = setTimeout(connectWebSocket, 3000);
        };
      } catch (e) {
        console.error('[WebSocket] Fallo al iniciar WebSocket:', e);
        reconnectTimer = setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (socket) socket.close();
      clearTimeout(reconnectTimer);
    };
  }, [loadInitialRooms]);

  return {
    rooms,
    setRooms,
    isConnected,
    lastUpdatedRoomId,
    refreshRooms: loadInitialRooms,
  };
}
