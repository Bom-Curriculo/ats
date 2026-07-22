#!/bin/sh
set -eu

echo "🚀 Iniciando aplicação Laravel..."

APP_KEY_FILE="/var/www/html/storage/app/docker/app_key"

mkdir -p \
  storage/app/docker \
  storage/app/public \
  storage/framework/cache/data \
  storage/framework/sessions \
  storage/framework/views \
  storage/logs \
  bootstrap/cache

chmod -R ug+rwX storage bootstrap/cache

if [ -z "${APP_KEY:-}" ]; then
  if [ -s "$APP_KEY_FILE" ]; then
    echo "🔑 Carregando APP_KEY persistida..."
    APP_KEY="$(cat "$APP_KEY_FILE")"
  else
    echo "🔑 Gerando APP_KEY..."
    APP_KEY="$(php artisan key:generate --show --no-ansi)"

    printf '%s' "$APP_KEY" > "$APP_KEY_FILE"
    chmod 600 "$APP_KEY_FILE"
  fi

  export APP_KEY
fi

echo "🧹 Limpando cache..."
php artisan optimize:clear

echo "📦 Rodando migrations..."
php artisan migrate --force

echo "🔗 Criando link do storage..."
php artisan storage:link || true

echo "⚡ Iniciando servidor Laravel..."

exec "$@"
