'use client';

/**
 * Cabecera del PMS: marca, estado del WebSocket y acciones de demo.
 */

import { Hotel, Radio, RefreshCw, Sparkles } from 'lucide-react';

export interface NavbarProps {
  /** True cuando el socket `/ws/rooms` está abierto. */
  isConnected: boolean;
  onOpenSimulator: () => void;
  onRefresh: () => void;
}

export function Navbar({ isConnected, onOpenSimulator, onRefresh }: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 glass-panel border-b border-gray-800 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-emerald-600 to-indigo-600 rounded-xl shadow-lg shadow-indigo-500/20">
            <Hotel className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              EcoPMS Cloud{' '}
              <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                Live Demo
              </span>
            </h1>
            <p className="text-xs text-gray-400">PMS en Tiempo Real + Agente Autónomo WhatsApp</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              isConnected
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
            }`}
          >
            <Radio
              className={`w-3.5 h-3.5 ${isConnected ? 'animate-pulse text-emerald-400' : 'text-rose-400'}`}
            />
            <span>{isConnected ? 'WebSocket Conectado' : 'Conectando WebSocket...'}</span>
          </div>

          <button
            type="button"
            onClick={onRefresh}
            className="p-2 text-gray-400 hover:text-white bg-gray-800/60 hover:bg-gray-800 rounded-lg transition-colors border border-gray-700/50"
            title="Refrescar habitaciones"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={onOpenSimulator}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-medium text-sm rounded-xl shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Sparkles className="w-4 h-4 text-emerald-100" />
            <span>Simulador WhatsApp & Pagos</span>
          </button>
        </div>
      </div>
    </header>
  );
}
