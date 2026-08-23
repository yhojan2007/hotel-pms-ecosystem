'use client';

/**
 * Drawer de demo: dispara el agente (`/webhooks/agent-sim`) y el pago mock
 * para ver el grid cambiar de color sin WhatsApp ni pasarela reales.
 */

import { useState } from 'react';
import { CheckCircle, CreditCard, MessageSquare, Mic, Send, Sparkles, X } from 'lucide-react';

import { simulateMockPayment, simulateWhatsAppAgent } from '@/lib/api';

export interface SimulatorDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SimulatorDrawer({ isOpen, onClose }: SimulatorDrawerProps) {
  const [senderContact, setSenderContact] = useState<string>('+573001234567');
  const [messageText, setMessageText] = useState<string>('');
  const [isAudio, setIsAudio] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [responseLog, setResponseLog] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSendSimulatedMessage = async (textToSend?: string): Promise<void> => {
    setLoading(true);
    setResponseLog(null);
    try {
      const finalMsg = textToSend || messageText;
      const res = await simulateWhatsAppAgent(
        senderContact,
        isAudio ? '' : finalMsg,
        isAudio ? 'mock://audio_nota_de_voz.ogg' : undefined
      );
      setResponseLog(res.agent_response || 'Mensaje procesado correctamente.');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error desconocido';
      setResponseLog(`Error: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulatePayment = async (): Promise<void> => {
    setLoading(true);
    setResponseLog(null);
    try {
      const res = await simulateMockPayment();
      setResponseLog(res.message || 'Pago confirmado exitosamente.');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error desconocido';
      setResponseLog(`Error: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-md glass-panel border-l border-gray-800 h-full p-6 flex flex-col justify-between shadow-2xl overflow-y-auto">
        <div>
          <div className="flex items-center justify-between pb-4 mb-6 border-b border-gray-800">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Simulador de WhatsApp & Pagos</h2>
                <p className="text-xs text-gray-400">Prueba en vivo frente al público</p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                Número del Huésped (WhatsApp)
              </label>
              <input
                type="text"
                value={senderContact}
                onChange={(e) => setSenderContact(e.target.value)}
                className="w-full px-3 py-2 bg-gray-900/80 border border-gray-700/80 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Acciones Rápidas de Demo:
              </label>
              <div className="grid grid-cols-1 gap-2">
                <button
                  type="button"
                  onClick={() =>
                    handleSendSimulatedMessage(
                      'Hola, ¿tienen habitaciones disponibles del 1 al 5 de agosto?'
                    )
                  }
                  disabled={loading}
                  className="flex items-center justify-between p-3 bg-gray-800/60 hover:bg-gray-800 border border-gray-700/60 rounded-xl text-xs text-left text-gray-200 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-indigo-400" />
                    1. Consultar Disponibilidad
                  </span>
                  <span className="text-[10px] text-gray-400">Texto</span>
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleSendSimulatedMessage(
                      'Me gustaría reservar la Habitación 101 a nombre de Carlos Mendoza del 1 al 5 de agosto'
                    )
                  }
                  disabled={loading}
                  className="flex items-center justify-between p-3 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-xl text-xs text-left text-amber-300 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    2. Simular Pre-Reserva (Cambia a Amarillo)
                  </span>
                  <span className="text-[10px] text-amber-400">WebSocket</span>
                </button>

                <button
                  type="button"
                  onClick={handleSimulatePayment}
                  disabled={loading}
                  className="flex items-center justify-between p-3 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 rounded-xl text-xs text-left text-rose-300 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    <CreditCard className="w-4 h-4 text-rose-400" />
                    3. Simular Confirmación de Pago (Cambia a Rojo)
                  </span>
                  <span className="text-[10px] text-rose-400">Webhook</span>
                </button>
              </div>
            </div>

            <div className="pt-2">
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Mensaje Personalizado
                </label>
                <button
                  type="button"
                  onClick={() => setIsAudio(!isAudio)}
                  className={`text-xs px-2 py-0.5 rounded-md flex items-center gap-1 ${
                    isAudio ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  <Mic className="w-3 h-3" />
                  {isAudio ? 'Modo Nota de Voz' : 'Texto'}
                </button>
              </div>

              <textarea
                rows={3}
                disabled={isAudio}
                value={isAudio ? '🎤 [Simulación de Nota de Voz enviada por WhatsApp]' : messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Escribe lo que diría el huésped por WhatsApp..."
                className="w-full px-3 py-2 bg-gray-900/80 border border-gray-700/80 rounded-xl text-sm text-white focus:outline-none focus:border-emerald-500 disabled:opacity-60"
              />

              <button
                type="button"
                onClick={() => handleSendSimulatedMessage()}
                disabled={loading}
                className="w-full mt-2 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20"
              >
                {loading ? (
                  'Procesando con Agente IA...'
                ) : (
                  <>
                    <Send className="w-4 h-4" /> Enviar Mensaje al Agente
                  </>
                )}
              </button>
            </div>
          </div>

          {responseLog && (
            <div className="mt-6 p-4 bg-gray-900/90 border border-gray-700/80 rounded-xl space-y-2">
              <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" /> Respuesta del Agente de WhatsApp:
              </div>
              <p className="text-xs text-gray-300 whitespace-pre-line leading-relaxed font-mono">
                {responseLog}
              </p>
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-gray-800 text-center">
          <p className="text-[11px] text-gray-500">
            Al ejecutar cualquier acción, el WebSocket enviará el evento en tiempo real y el PMS
            cambiará de color instantáneamente.
          </p>
        </div>
      </div>
    </div>
  );
}
