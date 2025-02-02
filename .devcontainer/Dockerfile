FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=/usr/local/cuda-11.8/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN nvcc --version && \
    ldconfig && \
    echo "CUDA and cuDNN installed successfully"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcublas-11-8 \
    libcublas-dev-11-8 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu118

RUN python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('cuDNN version:', torch.backends.cudnn.version()); print('CUDA version:', torch.version.cuda)"

WORKDIR /app

CMD ["/bin/bash"]

