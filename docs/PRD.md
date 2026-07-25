# PRD - Ecosistema Hotelero Cloud (PMS + Agente de WhatsApp)

## Visión General
Ecosistema hotelero en tiempo real compuesto por un Dashboard PMS web y un Agente de WhatsApp autónomo integrado con IA (Anthropic Claude + Zavu) y pasarela de pago.

## Arquitectura y Componentes
1. **Backend (FastAPI)**: REST API + WebSockets para actualización instantánea.
2. **Database (PostgreSQL + SQLAlchemy)**: Almacena Habitaciones, Huéspedes, Reservas y Pagos.
3. **Agente WhatsApp (Zavu + Claude)**: Procesa notas de voz y texto, gestiona reservas con tool calling.
4. **Frontend (Next.js)**: Dashboard PMS interactivo en grid/kanban con estados de color en tiempo real.
5. **Webhooks Pagos**: Impacta backend -> actualiza DB -> emite por WebSocket al frontend -> notifica por WhatsApp.
