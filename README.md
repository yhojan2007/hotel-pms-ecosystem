# Ecosistema Hotelero Cloud — PMS Visual + Agente Autónomo de WhatsApp

Demo de un sistema integral para hoteles boutique que combina un **dashboard de administración (PMS)** con un **agente de IA en WhatsApp** capaz de gestionar reservas y pagos en tiempo real, sin intervención humana.

## Descripción

El sistema resuelve la fricción operativa de un hotel independiente conectando dos capas sincronizadas:

- Un **agente conversacional en WhatsApp** que entiende lenguaje natural (texto o audio), consulta disponibilidad, cierra reservas y procesa pagos.
- Un **dashboard web** que refleja en tiempo real el estado de cada habitación según lo que ocurre en la conversación del huésped.

Cada acción del agente —confirmar una reserva, generar un link de pago, recibir la confirmación de pago— se propaga instantáneamente al panel visual mediante WebSockets.

## Objetivo de la demo

Mostrar en vivo la transaccionalidad autónoma de punta a punta:

1. Un huésped envía una nota de voz por WhatsApp pidiendo una habitación.
2. El agente transcribe el audio, consulta la base de datos y responde con disponibilidad y precio.
3. El huésped confirma → el agente genera un link de pago → la habitación pasa de **Verde** (disponible) a **Amarillo** (pago pendiente) en el dashboard.
4. Al confirmarse el pago, un webhook actualiza el estado a **Rojo** (confirmada/pagada) y el huésped recibe la confirmación por WhatsApp.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL + SQLAlchemy + Alembic |
| Frontend | Next.js + TailwindCSS |
| Tiempo real | WebSockets |
| Mensajería / WhatsApp | Zavu |
| Agente / LLM | Anthropic Claude (function calling) |
| Transcripción de audio | OpenAI Whisper (opcional) / fallback de demo |
| Pagos | Mock, Wallbit, MercadoPago, Stripe |
| Infraestructura | Docker + docker-compose |
| Control de versiones | Git + GitHub |

## Estructura del proyecto

```
hotel-pms-ecosystem/
├── docker-compose.yml
├── docker-compose.override.yml   # DEBUG=true en backend (solo local)
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/           # rooms, bookings, guests, payments, webhooks
│   │   ├── api/ws.py             # canal de tiempo real
│   │   ├── agent/                # tools, runner, transcripción, Zavu
│   │   ├── models/
│   │   ├── schemas/
│   │   └── db/
│   └── alembic/                  # migraciones
├── frontend/
│   └── src/
│       ├── components/           # RoomGrid, SimulatorDrawer, Navbar
│       └── hooks/                # useRealtimeRooms
└── docs/
    └── PRD.md
```

## Modelo de datos

- **rooms**: habitaciones, tipo, precio base, estado (`disponible` / `pendiente` / `ocupada`)
- **guests**: huéspedes y su historial de gasto
- **bookings**: reservas (habitación, huésped, fechas, estado, monto)
- **payments**: pagos asociados a cada reserva

El seed inicial crea 8 habitaciones (101–104, 201–202, 301–302) solo si la tabla está vacía.

---

## Cómo levantar el proyecto con Docker

Esta es la forma recomendada. Compose arranca PostgreSQL, aplica migraciones Alembic, corre el seed y levanta FastAPI + Next.js.

### Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y **en ejecución**
- Puertos libres: **3000** (frontend), **8000** (API), **5432** (Postgres)
- Git

No hace falta instalar Python ni Node en el host.

### 1. Clonar y crear el `.env`

```bash
git clone <url-del-repo>
cd hotel-pms-ecosystem
```

En Windows (PowerShell):

```powershell
copy .env.example .env
```

En macOS / Linux:

```bash
cp .env.example .env
```

Para **solo dashboard + simulador** no hace falta completar las claves de Anthropic, Zavu ni pagos. El agente usa un motor simulado cuando `ANTHROPIC_API_KEY` está vacío o es el placeholder `your_anthropic_api_key_here`. WhatsApp se escribe en los logs del backend (modo mock).

Si quieres el flujo real, edita `.env`:

| Variable | Para qué |
|---|---|
| `ANTHROPIC_API_KEY` | Agente Claude con tool calling |
| `OPENAI_API_KEY` | Transcripción Whisper de notas de voz reales |
| `ZAVU_API_KEY` / `ZAVU_PHONE_NUMBER_ID` | Envío real por WhatsApp |
| `PAYMENT_WEBHOOK_SECRET` | Autenticar webhooks de pago (excepto `mock`) |

**Importante:** dentro de Docker, `POSTGRES_SERVER` y las URLs de base de datos deben usar el host `db` (nombre del servicio), no `localhost`.

### 2. Construir y arrancar

Desde la raíz del repositorio:

```bash
docker compose up --build
```

La primera vez tarda (imagen Python + `npm run build` de Next). Deja la terminal abierta.

Cuando los contenedores estén healthy:

| Servicio | URL |
|---|---|
| Dashboard PMS | http://localhost:3000 |
| API + Swagger | http://localhost:8000/docs |
| Healthcheck | http://localhost:8000/health (`database: connected`) |
| WebSocket | `ws://localhost:8000/ws/rooms` |

En el dashboard deberías ver **8 habitaciones en verde** y el indicador de WebSocket conectado.

### 3. Verificar el flujo de demo (sin WhatsApp real)

1. Abre http://localhost:3000.
2. Abre el **Simulador** (drawer).
3. Envía un mensaje como *«¿tienen habitaciones disponibles?»* → el agente lista habitaciones (fechas de demo: 1–5 de agosto de 2026).
4. Envía *«quiero reservar»* → una habitación pasa a **amarillo**.
5. Simula el pago → pasa a **rojo**.

También puedes cambiar el estado a mano en cada tarjeta.

### 4. Parar y resetear

```bash
docker compose down       # detiene contenedores; conserva el volumen de Postgres
docker compose down -v    # además borra la DB (el seed se vuelve a ejecutar al subir)
```

Usa `-v` si el esquema quedó desfasado o quieres habitaciones “limpias”.

### Problemas frecuentes

| Síntoma | Qué revisar |
|---|---|
| `docker compose` falla al instante | Docker Desktop no está corriendo |
| Contenedor `db` no arranca | Puerto **5432** ocupado por un Postgres local. Cambia `POSTGRES_PORT` en `.env` o detén ese servicio |
| Frontend vacío / API 502 | Espera a que el backend termine migraciones + seed; revisa `docker compose logs backend` |
| Healthcheck sin DB | Las URLs deben apuntar a `db`, no a `localhost`, dentro de Compose |

---

## Desarrollo local (opcional, sin Docker para app)

Sigue necesitando PostgreSQL (puedes dejar solo el servicio `db` de Compose). Cambia en `.env` `POSTGRES_SERVER=localhost` y las URLs `...@localhost:5432/...`.

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Unix: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

Frontend (otra terminal):

```bash
cd frontend
npm install
# Windows PowerShell:
# $env:API_INTERNAL_URL="http://localhost:8000"
# $env:NEXT_PUBLIC_API_URL="/api/v1"
# $env:NEXT_PUBLIC_WS_URL="ws://localhost:8000/ws/rooms"
API_INTERNAL_URL=http://localhost:8000 NEXT_PUBLIC_API_URL=/api/v1 NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/rooms npm run dev
```

---

## Guion de la demo

1. Pantalla dividida: PMS a la izquierda (habitaciones en verde), simulador o WhatsApp a la derecha.
2. Nota de voz o texto: *«Necesito una suite para este fin de semana para dos personas»*.
3. El agente responde con disponibilidad y precio.
4. Confirmación / «reservar» → cambio automático a amarillo en el PMS.
5. Pago simulado → webhook → cambio a rojo + mensaje de confirmación (WhatsApp real o logs mock).

## Estado del proyecto

Demo realizada. *(Completar aquí con los resultados: qué funcionó, qué se ajustó sobre la marcha, feedback recibido y capturas de pantalla si las hay.)*

## Próximos pasos

- [ ] Confirmar/definir la pasarela de pago definitiva.
- [ ] Agregar autenticación al dashboard.
- [ ] Cobertura de tests en backend.

## Autoría

Proyecto desarrollado como práctica de arquitectura cloud, Docker y agentes de IA — Ingeniería en Sistemas.
