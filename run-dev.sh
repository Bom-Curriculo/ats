#!/usr/bin/env bash
# =============================================================================
# Sobe o ambiente de DESENVOLVIMENTO (hot reload, portas expostas).
#
#   ./run-dev.sh                 # sobe tudo (build + foreground)
#   ./run-dev.sh -d              # em background
#   ./run-dev.sh logs -f backend # qualquer subcomando do compose
#   ./run-dev.sh down            # derruba o ambiente
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")"

COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.dev.yml)

if [ "$#" -eq 0 ]; then
  echo ">> Subindo ambiente de desenvolvimento..."
  exec "${COMPOSE[@]}" up --build
fi

# Se o primeiro argumento for uma flag (ex: -d), assume "up"
case "$1" in
  -*) exec "${COMPOSE[@]}" up --build "$@" ;;
  *)  exec "${COMPOSE[@]}" "$@" ;;
esac
