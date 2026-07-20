#!/bin/sh
set -e

echo "🚀 Iniciando aplicação Laravel..."

# Aguarda o banco ficar disponível (opcional)
echo "⏳ Aguardando banco de dados..."

sleep 5

echo "📦 Rodando migrations..."
php artisan migrate --force

echo "📄 Gerando documentação da API (Swagger)..."
php artisan l5-swagger:generate

echo "🧹 Limpando cache..."
php artisan optimize:clear

echo "⚡ Iniciando servidor Laravel..."

exec "$@"