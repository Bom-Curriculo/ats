#!/usr/bin/env bash
# =============================================================================
# Sobe o ambiente de PRODUÇÃO (imagens auto-contidas).
#
#   ./run-prod.sh                # build + up -d
#   ./run-prod.sh logs -f        # qualquer subcomando do compose
#   ./run-prod.sh down           # derruba o ambiente
#
# Variáveis opcionais (podem vir do .env na raiz):
#   FRONTEND_PORT (5173)  BACKEND_PORT (8080)  BOT_PORT (8000)
#   VITE_API_URL_CONNECT
# =============================================================================
set -euo pipefail

cd "$(dirname "$0")"

COMPOSE=(docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml)

if [ "$#" -eq 0 ]; then
  echo ">> Subindo ambiente de produção..."
  exec "${COMPOSE[@]}" up -d --build
fi

case "$1" in
  -*) exec "${COMPOSE[@]}" up -d --build "$@" ;;
  *)  exec "${COMPOSE[@]}" "$@" ;;
esac
