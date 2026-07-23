# syntax=docker/dockerfile:1
# nginx de PRODUÇÃO para o backend: embute os assets estáticos de public/
# e a configuração. O contexto de build é a raiz do repositório.
FROM nginx:1.28-alpine

COPY docker/backend.conf /etc/nginx/conf.d/default.conf
COPY backend/public /var/www/html/public
