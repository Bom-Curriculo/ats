# syntax=docker/dockerfile:1

# =============================================================================
# Development, servidor de dev do Vite com HMR
# =============================================================================
FROM node:22-alpine AS development

WORKDIR /app

# Mais tolerância a rede instável (retries/timeout)
ENV npm_config_fetch_retries=5 \
    npm_config_fetch_retry_mintimeout=20000 \
    npm_config_fetch_retry_maxtimeout=120000 \
    npm_config_fetch_timeout=600000

COPY package*.json ./
# Cache de download do npm entre builds (BuildKit): re-tentativas reaproveitam
RUN --mount=type=cache,target=/root/.npm npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# =============================================================================
# Build, gera os assets estáticos de produção
# =============================================================================
FROM node:22-alpine AS build

WORKDIR /app

# URL da API embutida no bundle em tempo de build
ARG VITE_API_URL_CONNECT=http://127.0.0.1:8080/api
ENV VITE_API_URL_CONNECT=${VITE_API_URL_CONNECT}

# Mais tolerância a rede instável (retries/timeout)
ENV npm_config_fetch_retries=5 \
    npm_config_fetch_retry_mintimeout=20000 \
    npm_config_fetch_retry_maxtimeout=120000 \
    npm_config_fetch_timeout=600000

COPY package*.json ./
# Cache de download do npm entre builds (BuildKit): retentativas reaproveitam
RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .
RUN npm run build

# =============================================================================
# Production, serve os assets estáticos via nginx
# =============================================================================
FROM nginx:1.28-alpine AS production

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
