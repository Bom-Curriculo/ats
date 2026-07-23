# syntax=docker/dockerfile:1

# =============================================================================
# Base — runtime Python + uv e dependências de produção
# =============================================================================
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Instala dependências primeiro (cacheado enquanto pyproject.toml/uv.lock não mudam)
# Cache de download do uv (BuildKit): re-tentativas reaproveitam.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev

# =============================================================================
# Development — inclui deps de dev; código vem via bind-mount
# =============================================================================
FROM base AS development

RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked

EXPOSE 8000
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000", "--reload"]

# =============================================================================
# Production — código embutido na imagem
# =============================================================================
FROM base AS production

COPY . .

EXPOSE 8000

# API HTTP (Quart/ASGI)
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000"]
