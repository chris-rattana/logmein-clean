FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN useradd -m -u 10001 appuser \
    && mkdir -p /tmp/gunicorn \
    && chown -R appuser:appuser /app /tmp/gunicorn

USER appuser

ENV DB_HOST=db
ENV DB_NAME=logs_db
ENV DB_USER=logs_user
ENV DB_PASSWORD=logs_password
ENV DB_PORT=5432
ENV BACKEND_PORT=5000

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-tmp-dir", "/tmp/gunicorn", "app:app"]
