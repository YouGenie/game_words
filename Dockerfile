# Используем образ с предустановленным Python
FROM python:3.10-slim

# Устанавливаем системные зависимости для сборки llama-cpp
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Открываем порт, на котором работает FastAPI (обычно 8000)
EXPOSE 8000

# Команда для запуска сервера
CMD ["python", "app.py"]
