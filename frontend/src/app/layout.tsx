/**
 * Layout raíz de Next.js App Router.
 * Aplica metadata SEO, idioma y el fondo global del PMS.
 */

import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import './globals.css';

export const metadata: Metadata = {
  title: 'Hotel PMS Ecosystem - Cloud Dashboard',
  description: 'Dashboard en tiempo real con agente de WhatsApp e integraciones',
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="es">
      <body className="antialiased bg-[#090d16] text-gray-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
