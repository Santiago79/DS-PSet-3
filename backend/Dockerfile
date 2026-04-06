FROM python:3.11-slim

# El código importa `from backend.xxx`; la raíz del paquete debe ser /app/backend
WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# /app para `backend.*`; /app/backend para imports planos (`domain`, `infrastructure`, …)
ENV PYTHONPATH=/app:/app/backend

COPY requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . ./backend/

EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
