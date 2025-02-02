FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

# Install prerequisites for adding repositories
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Add Python 3.10 repository (PPA)
RUN add-apt-repository -y ppa:deadsnakes/ppa

# Install Python 3.10 and system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.10 \
    python3.10-distutils \
    python3.10-dev \
    && rm -rf /var/lib/apt/lists/*

# Create proper symbolic links
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

# Set Python 3.10 as default
RUN update-alternatives --set python3 /usr/bin/python3.10

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio

# Install Whisper and its dependencies
RUN pip3 install git+https://github.com/openai/whisper.git
RUN pip3 install faster-whisper

# Set the working directory
WORKDIR /workspace


