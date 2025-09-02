# app/backend/Dockerfile  (build context: repo root ".")
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Dependências
COPY app/backend/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y build-essential \
 && pip install --no-cache-dir -r /app/requirements.txt

# 2) Copia o repositório inteiro (para que o pacote "app" exista)
COPY . /app

# 3) Expõe porta e inicia Uvicorn usando o caminho do pacote
EXPOSE 8000
CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
