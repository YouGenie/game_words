FROM python:3.10-slim

WORKDIR /app

# Устанавливаем минимальные утилиты, необходимые для развертывания
RUN apt-get update && apt-get install -y \
    gcc g++ cmake git \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN python3 -m pip install --upgrade pip

# Устанавливаем ГОТОВЫЙ бинарник (wheel) под CPU по правильной ссылке разработчика
RUN python3 -m pip install --no-cache-dir llama-cpp-python \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Копируем и устанавливаем остальные зависимости проекта
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .

# Оба сервиса будут запускаться через docker-compose, здесь просто открываем порты
EXPOSE 8000 8501




