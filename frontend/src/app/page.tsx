'use client';

/**
 * Página principal del dashboard PMS.
 *
 * Combina el grid de habitaciones, el indicador WebSocket y el simulador
 * de WhatsApp/pagos. Los cambios de estado manuales son optimistas:
 * la UI se actualiza al instante y luego se confirma con el PATCH del API.
 */

import { useState } from 'react';
import { Sparkles } from 'lucide-react';

import { Navbar } from '@/components/Navbar';
import { RoomGrid } from '@/components/RoomGrid';
import { SimulatorDrawer } from '@/components/SimulatorDrawer';
import { useRealtimeRooms } from '@/hooks/useRealtimeRooms';
import { updateRoomStatus, type RoomStatus } from '@/lib/api';

export default function PMSDashboardPage() {
  const { rooms, setRooms, isConnected, lastUpdatedRoomId, refreshRooms } = useRealtimeRooms();
  const [isSimulatorOpen, setIsSimulatorOpen] = useState<boolean>(false);

  const handleManualStatusChange = async (roomId: number, estado: RoomStatus): Promise<void> => {
    setRooms((prev) => prev.map((r) => (r.id === roomId ? { ...r, estado } : r)));
    await updateRoomStatus(roomId, estado);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16] text-gray-100 selection:bg-indigo-500 selection:text-white">
      <Navbar
        isConnected={isConnected}
        onOpenSimulator={() => setIsSimulatorOpen(true)}
        onRefresh={refreshRooms}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border border-indigo-500/20">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20 mt-1 md:mt-0">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Panel de Control de Habitaciones (Property Management System)
              </h2>
              <p className="text-sm text-gray-400 max-w-2xl mt-0.5">
                Las habitaciones cambian de estado en{' '}
                <strong className="text-emerald-400 font-semibold">tiempo real</strong> cuando el
                agente de WhatsApp atiende clientes por nota de voz o cuando el webhook recibe un
                pago.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Verde = Disponible</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>Amarillo = Pendiente</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <span className="w-2 h-2 rounded-full bg-rose-400" />
              <span>Rojo = Ocupada</span>
            </div>
          </div>
        </div>

        <RoomGrid
          rooms={rooms}
          lastUpdatedRoomId={lastUpdatedRoomId}
          onStatusChange={handleManualStatusChange}
        />
      </main>

      <SimulatorDrawer isOpen={isSimulatorOpen} onClose={() => setIsSimulatorOpen(false)} />

      <footer className="border-t border-gray-800/80 py-6 text-center text-xs text-gray-500">
        <p>
          Ecosistema Hotelero Cloud © 2026 — FastAPI + Next.js + Anthropic Claude + Zavu WhatsApp
          API
        </p>
      </footer>
    </div>
  );
}
