FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt

COPY . .

VOLUME ["/app/configs", "/app/logs", "/app/storage", "/app/plugins"]

CMD ["python", "main.py"]
