# Use the latest CUDA devel image for Ubuntu 22.04 with cuDNN
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04


# Install software-properties-common (to add PPAs), add deadsnakes for Python3.10,
# and install Python 3.10 plus required packages.
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip \
        curl \
        git \
        ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcudnn8 libcudnn8-dev

ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Upgrade pip to the latest version
RUN python3 -m pip install --upgrade pip

# Install your Python dependencies (here combined into one layer to reduce image size)
RUN python3 -m pip install \
    torch torchvision torchaudio requests \
    feedparser python-dotenv sqlalchemy pyyaml \
    git+https://github.com/m-bain/whisperx.git \
    faster-whisper

# Set the working directory
WORKDIR /workspace
