'use client';

import React from 'react';
import { Room } from '@/lib/api';
import { Bed, UserCheck, Clock, CheckCircle2, DollarSign } from 'lucide-react';

interface RoomCardProps {
  room: Room;
  isJustUpdated: boolean;
  onStatusChange: (roomId: number, estado: 'disponible' | 'pendiente' | 'ocupada') => void;
}

export const RoomCard: React.FC<RoomCardProps> = ({ room, isJustUpdated, onStatusChange }) => {
  const getStatusStyles = (estado: Room['estado']) => {
    switch (estado) {
      case 'disponible':
        return {
          badgeBg: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
          dotBg: 'bg-emerald-500',
          cardGlow: 'hover:shadow-glow-green border-emerald-500/20',
          label: 'Disponible',
          icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        };
      case 'pendiente':
        return {
          badgeBg: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
          dotBg: 'bg-amber-500',
          cardGlow: 'hover:shadow-glow-yellow border-amber-500/30',
          label: 'Pago Pendiente',
          icon: <Clock className="w-4 h-4 text-amber-400 animate-pulse" />
        };
      case 'ocupada':
        return {
          badgeBg: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
          dotBg: 'bg-rose-500',
          cardGlow: 'hover:shadow-glow-red border-rose-500/30',
          label: 'Ocupada / Pagada',
          icon: <UserCheck className="w-4 h-4 text-rose-400" />
        };
      default:
        return {
          badgeBg: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
          dotBg: 'bg-gray-500',
          cardGlow: 'border-gray-700',
          label: estado,
          icon: null
        };
    }
  };

  const statusInfo = getStatusStyles(room.estado);

  return (
    <div
      className={`glass-card rounded-2xl p-5 relative overflow-hidden flex flex-col justify-between transition-all duration-500 ${
        statusInfo.cardGlow
      } ${isJustUpdated ? 'animate-status-update ring-2 ring-indigo-500 shadow-2xl' : ''}`}
    >
      {/* Fondo sutil de color según estado */}
      <div className={`absolute -top-12 -right-12 w-28 h-28 rounded-full blur-3xl opacity-20 pointer-events-none ${statusInfo.dotBg}`} />

      <div>
        {/* Cabecera de Tarjeta: Tipo y Estado */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs uppercase tracking-wider font-semibold text-gray-400 flex items-center gap-1.5">
            <Bed className="w-3.5 h-3.5 text-indigo-400" />
            {room.tipo}
          </span>

          <div className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${statusInfo.badgeBg}`}>
            {statusInfo.icon}
            <span>{statusInfo.label}</span>
          </div>
        </div>

        {/* Nombre de Habitación */}
        <h3 className="text-xl font-bold text-white mb-2 tracking-tight">
          {room.nombre}
        </h3>

        {/* Precio */}
        <div className="flex items-baseline space-x-1 text-gray-300 mb-4">
          <span className="text-2xl font-bold text-white">${room.precio_base}</span>
          <span className="text-xs text-gray-400">USD / noche</span>
        </div>
      </div>

      {/* Acciones Rápidas para Cambio Manual de Estado */}
      <div className="pt-3 border-t border-gray-800/80 flex items-center justify-between gap-1 text-xs">
        <span className="text-gray-500 text-[10px] font-medium">CAMBIAR:</span>
        <div className="flex space-x-1">
          <button
            onClick={() => onStatusChange(room.id, 'disponible')}
            className={`px-2 py-1 rounded-md text-[11px] font-medium transition-all ${
              room.estado === 'disponible'
                ? 'bg-emerald-500 text-white shadow-sm'
                : 'bg-gray-800 text-gray-400 hover:text-emerald-400 hover:bg-gray-700'
            }`}
          >
            Verde
          </button>
          <button
            onClick={() => onStatusChange(room.id, 'pendiente')}
            className={`px-2 py-1 rounded-md text-[11px] font-medium transition-all ${
              room.estado === 'pendiente'
                ? 'bg-amber-500 text-white shadow-sm'
                : 'bg-gray-800 text-gray-400 hover:text-amber-400 hover:bg-gray-700'
            }`}
          >
            Amarillo
          </button>
          <button
            onClick={() => onStatusChange(room.id, 'ocupada')}
            className={`px-2 py-1 rounded-md text-[11px] font-medium transition-all ${
              room.estado === 'ocupada'
                ? 'bg-rose-500 text-white shadow-sm'
                : 'bg-gray-800 text-gray-400 hover:text-rose-400 hover:bg-gray-700'
            }`}
          >
            Rojo
          </button>
        </div>
      </div>
    </div>
  );
};
