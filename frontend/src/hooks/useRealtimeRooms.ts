'use client';

/**
 * Hook de estado del PMS: carga REST inicial + suscripción WebSocket.
 *
 * El backend emite `{ event: "room_status_updated", data: Room }` en `/ws/rooms`.
 * Si se pierde la conexión, reintenta cada 3 segundos.
 */

import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from 'react';

import { fetchRooms, type Room } from '@/lib/api';

export interface UseRealtimeRoomsResult {
  rooms: Room[];
  setRooms: Dispatch<SetStateAction<Room[]>>;
  isConnected: boolean;
  lastUpdatedRoomId: number | null;
  refreshRooms: () => Promise<void>;
}

/** Evento de habitación que emite FastAPI por WebSocket. */
interface RoomStatusPayload {
  event?: string;
  data?: Room;
}

export function useRealtimeRooms(): UseRealtimeRoomsResult {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastUpdatedRoomId, setLastUpdatedRoomId] = useState<number | null>(null);

  const loadInitialRooms = useCallback(async (): Promise<void> => {
    const data = await fetchRooms();
    setRooms(data);
  }, []);

  useEffect(() => {
    void loadInitialRooms();

    const wsUrl: string =
      process.env.NEXT_PUBLIC_WS_URL ||
      `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/rooms`;

    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout>;

    const connectWebSocket = (): void => {
      try {
        socket = new WebSocket(wsUrl);

        socket.onopen = (): void => {
          console.log('[WebSocket] Conectado exitosamente al PMS');
          setIsConnected(true);
        };

        socket.onmessage = (event: MessageEvent<string>): void => {
          try {
            const payload = JSON.parse(event.data) as RoomStatusPayload;
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

        socket.onerror = (error: Event): void => {
          console.error('[WebSocket] Error de conexión:', error);
          setIsConnected(false);
        };

        socket.onclose = (): void => {
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

    return (): void => {
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
