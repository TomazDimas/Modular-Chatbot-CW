FROM python:3.11-slim

WORKDIR /app

COPY app/backend/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
  && pip install --no-cache-dir -r /app/requirements.txt \
  && apt-get purge -y --auto-remove build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY app /app/app

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
