import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Hotel PMS Ecosystem - Cloud Dashboard',
  description: 'Dashboard en tiempo real con agente de WhatsApp e integraciones',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="antialiased bg-[#090d16] text-gray-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
