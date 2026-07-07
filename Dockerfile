FROM python:3.11-slim

# Настройка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установка системных зависимостей для сборки, если они понадобятся
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода проекта
COPY . .

# Запуск бота
CMD ["python", "main.py"]
