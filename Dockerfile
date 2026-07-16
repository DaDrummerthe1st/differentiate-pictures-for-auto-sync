FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends openssl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout /app/key.pem -out /app/cert.pem -days 3650 \
    -subj "/CN=mamma-photo-viewer"

EXPOSE 8420
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8420", \
     "--ssl-keyfile", "/app/key.pem", "--ssl-certfile", "/app/cert.pem"]
