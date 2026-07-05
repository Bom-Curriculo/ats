FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (cached while pyproject.toml/uv.lock are unchanged).
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY . .

EXPOSE 8000

# HTTP API (Quart/ASGI). Run the RabbitMQ worker separately with:
#   uv run python -m app.workers.rabbitmq_worker
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000"]
