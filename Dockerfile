# Билд стадия
FROM python:3.12-alpine AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем системные зависимости для компиляции
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальная стадия
FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем только runtime зависимости
RUN apk add --no-cache \
    libffi \
    libssl3

WORKDIR /aio-s-parser

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /root/.local

# Добавляем путь к локальным пакетам
ENV PATH="/root/.local/bin:${PATH}"

# Копируем код
COPY . .

CMD ["python", "main.py"]