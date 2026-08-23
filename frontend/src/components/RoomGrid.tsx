'use client';

/**
 * Grid filtrable de habitaciones con métricas por color de estado.
 */

import { useMemo, useState } from 'react';
import { CheckCircle2, Clock, LayoutGrid, UserCheck } from 'lucide-react';

import { type Room, type RoomStatus } from '@/lib/api';

import { RoomCard } from './RoomCard';

export type RoomFilter = 'todos' | RoomStatus;

export interface RoomGridProps {
  rooms: Room[];
  lastUpdatedRoomId: number | null;
  onStatusChange: (roomId: number, estado: RoomStatus) => void;
}

export function RoomGrid({ rooms, lastUpdatedRoomId, onStatusChange }: RoomGridProps) {
  const [filter, setFilter] = useState<RoomFilter>('todos');

  const disponibles = rooms.filter((r) => r.estado === 'disponible').length;
  const pendientes = rooms.filter((r) => r.estado === 'pendiente').length;
  const ocupadas = rooms.filter((r) => r.estado === 'ocupada').length;

  const filteredRooms = useMemo(
    () => (filter === 'todos' ? rooms : rooms.filter((r) => r.estado === filter)),
    [filter, rooms]
  );

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="grid grid-cols-4 gap-3 w-full md:w-auto">
          <button
            type="button"
            onClick={() => setFilter('todos')}
            className={`px-4 py-2.5 rounded-xl border text-left transition-all ${
              filter === 'todos'
                ? 'bg-indigo-600/20 border-indigo-500/40 text-white shadow-md'
                : 'bg-gray-800/40 border-gray-700/50 text-gray-400 hover:text-white'
            }`}
          >
            <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-400">Total</div>
            <div className="text-xl font-bold text-white">{rooms.length}</div>
          </button>

          <button
            type="button"
            onClick={() => setFilter('disponible')}
            className={`px-4 py-2.5 rounded-xl border text-left transition-all ${
              filter === 'disponible'
                ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300 shadow-md'
                : 'bg-gray-800/40 border-gray-700/50 text-gray-400 hover:text-emerald-400'
            }`}
          >
            <div className="text-[11px] font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Verde
            </div>
            <div className="text-xl font-bold text-emerald-400">{disponibles}</div>
          </button>

          <button
            type="button"
            onClick={() => setFilter('pendiente')}
            className={`px-4 py-2.5 rounded-xl border text-left transition-all ${
              filter === 'pendiente'
                ? 'bg-amber-500/20 border-amber-500/40 text-amber-300 shadow-md'
                : 'bg-gray-800/40 border-gray-700/50 text-gray-400 hover:text-amber-400'
            }`}
          >
            <div className="text-[11px] font-semibold uppercase tracking-wider text-amber-400 flex items-center gap-1">
              <Clock className="w-3 h-3" /> Amarillo
            </div>
            <div className="text-xl font-bold text-amber-400">{pendientes}</div>
          </button>

          <button
            type="button"
            onClick={() => setFilter('ocupada')}
            className={`px-4 py-2.5 rounded-xl border text-left transition-all ${
              filter === 'ocupada'
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-300 shadow-md'
                : 'bg-gray-800/40 border-gray-700/50 text-gray-400 hover:text-rose-400'
            }`}
          >
            <div className="text-[11px] font-semibold uppercase tracking-wider text-rose-400 flex items-center gap-1">
              <UserCheck className="w-3 h-3" /> Rojo
            </div>
            <div className="text-xl font-bold text-rose-400">{ocupadas}</div>
          </button>
        </div>

        <div className="flex items-center space-x-2 text-sm text-gray-400 font-medium">
          <LayoutGrid className="w-4 h-4 text-indigo-400" />
          <span>Vista Kanban Grid ({filteredRooms.length} habitaciones)</span>
        </div>
      </div>

      {filteredRooms.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center text-gray-400">
          No hay habitaciones en este estado actualmente.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {filteredRooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              isJustUpdated={lastUpdatedRoomId === room.id}
              onStatusChange={onStatusChange}
            />
          ))}
        </div>
      )}
    </div>
  );
}
