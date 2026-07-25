'use client';

import React, { useState } from 'react';
import { Room } from '@/lib/api';
import { RoomCard } from './RoomCard';
import { LayoutGrid, Filter, CheckCircle2, Clock, UserCheck } from 'lucide-react';

interface RoomGridProps {
  rooms: Room[];
  lastUpdatedRoomId: number | null;
  onStatusChange: (roomId: number, estado: 'disponible' | 'pendiente' | 'ocupada') => void;
}

export const RoomGrid: React.FC<RoomGridProps> = ({ rooms, lastUpdatedRoomId, onStatusChange }) => {
  const [filter, setFilter] = useState<'todos' | 'disponible' | 'pendiente' | 'ocupada'>('todos');

  // Métricas
  const total = rooms.length;
  const disponibles = rooms.filter(r => r.estado === 'disponible').length;
  const pendientes = rooms.filter(r => r.estado === 'pendiente').length;
  const ocupadas = rooms.filter(r => r.estado === 'ocupada').length;

  const filteredRooms = filter === 'todos' 
    ? rooms 
    : rooms.filter(r => r.estado === filter);

  return (
    <div className="space-y-6">
      
      {/* Barra de Filtros & Métricas de Estado */}
      <div className="glass-panel rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Tarjetas de Resumen de Métricas */}
        <div className="grid grid-cols-4 gap-3 w-full md:w-auto">
          
          <button
            onClick={() => setFilter('todos')}
            className={`px-4 py-2.5 rounded-xl border text-left transition-all ${
              filter === 'todos'
                ? 'bg-indigo-600/20 border-indigo-500/40 text-white shadow-md'
                : 'bg-gray-800/40 border-gray-700/50 text-gray-400 hover:text-white'
            }`}
          >
            <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-400">Total</div>
            <div className="text-xl font-bold text-white">{total}</div>
          </button>

          <button
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

        {/* Título de Vista Grid */}
        <div className="flex items-center space-x-2 text-sm text-gray-400 font-medium">
          <LayoutGrid className="w-4 h-4 text-indigo-400" />
          <span>Vista Kanban Grid ({filteredRooms.length} habitaciones)</span>
        </div>
      </div>

      {/* Grid de Tarjetas de Habitaciones */}
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
};
