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

if [ ! -f public/build/manifest.json ]; then
  echo "❌ Vite manifest não encontrado em public/build/manifest.json"
  exit 1
fi

echo "🧹 Limpando cache..."
php artisan optimize:clear

echo "⏳ Aguardando PostgreSQL..."

until php -r '
$host = getenv("DB_HOST") ?: "postgres";
$port = getenv("DB_PORT") ?: "5432";
$database = getenv("DB_DATABASE");
$user = getenv("DB_USERNAME");
$password = getenv("DB_PASSWORD");

try {
    new PDO(
        "pgsql:host=$host;port=$port;dbname=$database",
        $user,
        $password
    );
    exit(0);
} catch (Throwable $e) {
    exit(1);
}
'; do
  echo "PostgreSQL ainda não está disponível..."
  sleep 2
done

echo "✅ PostgreSQL disponível."

echo "📦 Rodando migrations e seeds..."
php artisan migrate --seed --force

echo "🔗 Criando link do storage..."
php artisan storage:link || true

echo "⚡ Iniciando servidor Laravel..."

exec "$@"
