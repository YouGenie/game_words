FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3-pip python3-dev git cmake build-essential \
    && rm -rf /var/lib/apt/lists/*

# Настройки для RTX 5060 Ti
ENV LLAMA_CUDA=on
ENV FORCE_CMAKE=1
ENV CMAKE_ARGS="-DLLAMA_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=89"

WORKDIR /app

# Обновляем pip и ставим инструменты сборки
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir setuptools scikit-build cmake

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python3", "app.py"]







