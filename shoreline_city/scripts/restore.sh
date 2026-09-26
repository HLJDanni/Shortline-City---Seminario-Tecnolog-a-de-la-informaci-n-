#!/usr/bin/env bash
# Restauración desde un respaldo (RF-062).
# Uso: ./scripts/restore.sh scripts/backup/shoreline_XXXX.dump
set -euo pipefail

FILE="${1:?Indique el archivo .dump a restaurar}"
DB="${POSTGRES_DB:-shoreline_city}"
USER="${POSTGRES_USER:-shoreline}"

cat "$FILE" | docker compose exec -T db pg_restore -U "$USER" -d "$DB" --clean --if-exists
echo "Restauración completada desde: $FILE"
