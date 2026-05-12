# Используем образ с поддержкой CUDA от NVIDIA
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Устанавливаем Python и необходимые системные утилиты
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Настраиваем переменные окружения для сборки llama-cpp с поддержкой CUDA
ENV LLAMA_CUBLAS=1
ENV CMAKE_ARGS="-DLLAMA_CUBLAS=on"
ENV FORCE_CMAKE=1

WORKDIR /app

COPY requirements.txt .

# Устанавливаем зависимости (здесь llama-cpp пересоберется с поддержкой GPU)
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "app.py"]

