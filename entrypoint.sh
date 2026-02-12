#!/bin/sh
set -e

echo "⏳ Checking PostgreSQL availability..."
wait_for_pg.sh "$POSTGRES_HOST"

echo "🔄 Running Alembic migrations..."
alembic upgrade head

echo "👤 Running startup script..."
python3 -m app.startup.startup

echo "🚀 Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 80
