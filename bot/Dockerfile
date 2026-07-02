FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# API FastAPI (o consumer do RabbitMQ será adicionado quando o fluxo for implementado)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
