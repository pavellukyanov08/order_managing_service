#!/bin/sh
set -e

host="$1"

if [ -z "$host" ]; then
  echo "❌ POSTGRES_HOST is not set!"
  exit 1
fi

echo "⏳ Waiting for PostgreSQL (${host}:5432)..."

until nc -z "$host" 5432; do
  sleep 1
  echo "⏳ Waiting for PostgreSQL (${host}:5432)..."
done

echo "✅ PostgreSQL is up!"
