#!/usr/bin/env bash
# Respaldo de la base de datos (RF-061, RNF-011).
# Uso: ./scripts/backup.sh   (ejecutar en el host con docker compose activo)
set -euo pipefail

STAMP=$(date +%Y%m%d_%H%M%S)
DEST="scripts/backup"
mkdir -p "$DEST"
DB="${POSTGRES_DB:-shoreline_city}"
USER="${POSTGRES_USER:-shoreline}"

docker compose exec -T db pg_dump -U "$USER" -d "$DB" -F c \
  > "${DEST}/shoreline_${STAMP}.dump"

echo "Backup creado: ${DEST}/shoreline_${STAMP}.dump"

# Retención: conservar los últimos 14 respaldos.
ls -1t "${DEST}"/shoreline_*.dump 2>/dev/null | tail -n +15 | xargs -r rm --
