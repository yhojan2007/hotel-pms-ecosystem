# 🏨 Ecosistema Hotelero Cloud — PMS Visual + Agente Autónomo de WhatsApp

Demo de un sistema integral para hoteles boutique que combina un **dashboard de administración (PMS)** con un **agente de IA en WhatsApp** capaz de gestionar reservas y pagos en tiempo real, sin intervención humana.

## 📋 Descripción

El sistema resuelve la fricción operativa de un hotel independiente conectando dos capas sincronizadas:

- Un **agente conversacional en WhatsApp** que entiende lenguaje natural (texto o audio), consulta disponibilidad, cierra reservas y procesa pagos.
- Un **dashboard web** que refleja en tiempo real el estado de cada habitación según lo que ocurre en la conversación del huésped.

Cada acción del agente —confirmar una reserva, generar un link de pago, recibir la confirmación de pago— se propaga instantáneamente al panel visual mediante WebSockets.

## 🎯 Objetivo de la demo

Mostrar en vivo la transaccionalidad autónoma de punta a punta:

1. Un huésped envía una nota de voz por WhatsApp pidiendo una habitación.
2. El agente transcribe el audio, consulta la base de datos y responde con disponibilidad y precio.
3. El huésped confirma → el agente genera un link de pago → la habitación pasa de **Verde** (disponible) a **Amarillo** (pago pendiente) en el dashboard.
4. Al confirmarse el pago, un webhook actualiza el estado a **Rojo** (confirmada/pagada) y el huésped recibe la confirmación por WhatsApp.

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL + SQLAlchemy + Alembic |
| Frontend | Next.js + TailwindCSS |
| Tiempo real | WebSockets |
| Mensajería / WhatsApp | Zavu |
| Agente / LLM | Anthropic Claude (function calling) |
| Transcripción de audio | Wispr Flow |
| Pagos | Wallbit / pasarela de pago |
| Infraestructura | Docker + docker-compose |
| Control de versiones | Git + GitHub |

## 📁 Estructura del proyecto

```
hotel-pms-ecosystem/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/       # rooms, bookings, guests, webhooks
│   │   ├── api/ws.py         # canal de tiempo real
│   │   ├── agent/            # tools, runner, transcripción
│   │   ├── models/
│   │   ├── schemas/
│   │   └── db/
│   └── alembic/               # migraciones
├── frontend/
│   └── src/
│       ├── components/       # RoomGrid, BookingCard, GuestTable
│       └── hooks/             # useRealtimeRooms
└── docs/
    └── PRD.md
```

## 🗄️ Modelo de datos

- **rooms**: habitaciones, tipo, precio base, estado
- **guests**: huéspedes y su historial
- **bookings**: reservas (habitación, huésped, fechas, estado, monto)
- **payments**: pagos asociados a cada reserva

## 🚀 Cómo levantar el proyecto

```bash
git clone <url-del-repo>
cd hotel-pms-ecosystem
cp .env.example .env    # completar variables (DB, Zavu, Anthropic, pasarela de pago)
docker-compose up --build
```

- Backend disponible en `http://localhost:8000`
- Frontend disponible en `http://localhost:3000`

## 🎬 Guion de la demo

1. Pantalla dividida: PMS a la izquierda (habitación "Suite Océano" en Verde), WhatsApp a la derecha.
2. Nota de voz: *"Necesito una suite para este fin de semana para dos personas"*.
3. El agente responde con disponibilidad y precio.
4. Confirmación → cambio automático a Amarillo en el PMS.
5. Pago simulado → webhook → cambio a Rojo + factura enviada por WhatsApp.

## ✅ Estado del proyecto

Demo realizada. *(Completar aquí con los resultados: qué funcionó, qué se ajustó sobre la marcha, feedback recibido y capturas de pantalla si las hay.)*

## 🔜 Próximos pasos

- [ ] Confirmar/definir la pasarela de pago definitiva.
- [ ] Agregar autenticación al dashboard.
- [ ] Cobertura de tests en backend.
- [ ] Documentar variables de entorno completas en `.env.example`.

## 👥 Autoría

Proyecto desarrollado como práctica de arquitectura cloud, Docker y agentes de IA — Ingeniería en Sistemas.