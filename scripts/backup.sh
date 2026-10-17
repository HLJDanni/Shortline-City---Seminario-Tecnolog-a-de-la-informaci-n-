#!/usr/bin/env bash
# Respaldo de la base de datos (RF-061, RNF-011).
#
# Uso:
#   ./scripts/backup.sh
#     - Si DATABASE_URL está definida (p. ej. Supabase), respalda esa base
#       con el pg_dump instalado en el equipo (versión >= a la del servidor).
#     - Si no, respalda el contenedor "db" de docker compose.
set -euo pipefail

STAMP=$(date +%Y%m%d_%H%M%S)
DEST="scripts/backup"
mkdir -p "$DEST"
ARCHIVO="${DEST}/shoreline_${STAMP}.dump"

if [[ -n "${DATABASE_URL:-}" ]]; then
  # pg_dump no entiende el prefijo de SQLAlchemy "postgresql+psycopg://".
  URL="${DATABASE_URL/postgresql+psycopg:\/\//postgresql://}"
  pg_dump "$URL" -n public -F c --no-owner --no-privileges -f "$ARCHIVO"
else
  DB="${POSTGRES_DB:-shoreline_city}"
  USER="${POSTGRES_USER:-shoreline}"
  docker compose exec -T db pg_dump -U "$USER" -d "$DB" -F c > "$ARCHIVO"
fi

echo "Backup creado: ${ARCHIVO}"

# Retención: conservar los últimos 14 respaldos.
ls -1t "${DEST}"/shoreline_*.dump 2>/dev/null | tail -n +15 | xargs -r rm --
