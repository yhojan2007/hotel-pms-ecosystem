#!/bin/bash
set -e

echo "[Production Entrypoint] Esperando a que PostgreSQL esté listo..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_SERVER" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "[Production Entrypoint] Base de datos no disponible aún, esperando 2 segundos..."
  sleep 2
done

echo "[Production Entrypoint] Base de datos conectada. Ejecutando migraciones con Alembic..."
alembic upgrade head

echo "[Production Entrypoint] Ejecutando seed de datos iniciales si aplica..."
python -m app.db.seed

echo "[Production Entrypoint] Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${WEB_CONCURRENCY:-1}"
