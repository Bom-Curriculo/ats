#!/usr/bin/env bash
# Entrypoint de DESENVOLVIMENTO.
# O código é montado via bind-mount, então preparamos o ambiente em runtime.
set -euo pipefail

cd /var/www/html

echo "[entrypoint:dev] preparando ambiente..."

# .env
if [ ! -f .env ] && [ -f .env.example ]; then
    echo "[entrypoint:dev] criando .env a partir do .env.example"
    cp .env.example .env
fi

# Dependências (o vendor não vem na imagem em dev)
if [ ! -d vendor ] || [ ! -f vendor/autoload.php ]; then
    echo "[entrypoint:dev] instalando dependências do composer..."
    composer install --prefer-dist --no-progress
fi

# APP_KEY
if ! grep -qE '^APP_KEY=.+' .env; then
    echo "[entrypoint:dev] gerando APP_KEY..."
    php artisan key:generate --force || true
fi

# Banco sqlite (padrão do projeto)
if grep -qE '^DB_CONNECTION=sqlite' .env && [ ! -f database/database.sqlite ]; then
    echo "[entrypoint:dev] criando database/database.sqlite"
    mkdir -p database
    touch database/database.sqlite
fi

# Permissões de runtime (inclui database/ para o SQLite gravar journal/WAL)
mkdir -p storage/framework/{cache,sessions,views} storage/logs bootstrap/cache
chown -R www-data:www-data storage bootstrap/cache database || true
chmod -R 775 storage bootstrap/cache database || true

# Migrations (graceful, não derruba o container se o banco não estiver pronto)
echo "[entrypoint:dev] rodando migrations..."
php artisan migrate --force || echo "[entrypoint:dev] migrations falharam (seguindo mesmo assim)"

echo "[entrypoint:dev] pronto. iniciando: $*"
exec "$@"
