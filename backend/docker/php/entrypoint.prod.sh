#!/usr/bin/env bash
# Entrypoint de PRODUÇÃO.
# Código e dependências já vêm embutidos na imagem.
set -euo pipefail

cd /var/www/html

echo "[entrypoint:prod] inicializando..."

# APP_KEY é obrigatório em produção
if ! grep -qE '^APP_KEY=.+' .env 2>/dev/null && [ -z "${APP_KEY:-}" ]; then
    echo "[entrypoint:prod] ERRO: APP_KEY não definido (.env ou variável de ambiente)." >&2
    exit 1
fi

# Banco sqlite: garante o arquivo e a escrita pelo www-data (php-fpm).
# O SQLite precisa gravar tanto o arquivo quanto o diretório (journal/WAL).
if [ "${DB_CONNECTION:-}" = "sqlite" ]; then
    [ -f database/database.sqlite ] || touch database/database.sqlite
    chown -R www-data:www-data database
    chmod -R 775 database
fi

# Migrations
echo "[entrypoint:prod] rodando migrations..."
php artisan migrate --force

# Caches de produção (não-fatais: uma falha de cache não deve impedir o boot).
# OBS: route:cache é omitido de propósito, o projeto tem rota com closure
# (routes/web.php), o que faz o route:cache falhar. Reative quando as rotas
# usarem apenas controllers.
echo "[entrypoint:prod] otimizando (config/view cache)..."
php artisan config:cache || echo "[entrypoint:prod] aviso: config:cache falhou"
php artisan view:cache   || echo "[entrypoint:prod] aviso: view:cache falhou"

echo "[entrypoint:prod] pronto. iniciando: $*"
exec "$@"
