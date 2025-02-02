
## VSCode or Cursor setup with GPU support on remote server with nvidia cards (and )

## 1. Required Extensions
Install these VS Code extensions locally:
- **Remote Development** extension pack (includes Remote-SSH and Dev Containers)
- **Docker** extension

## 2. SSH Configuration
Add this to your `~/.ssh/config`:
```config
Host gpu-server
    HostName your.server.ip
    User your-username
    IdentityFile ~/.ssh/your-private-key
    ForwardAgent yes
```

To build and run this Docker container:

1. change into container directory.
    ```bash
    cd container
    ```
2. Build the image:
   ```bash
   docker build -t cuda11.8-cublas-cudnn .
   ```
3. Run the container with GPU support:
   ```bash
   docker run --gpus all -it cuda11.8-cublas-cudnn
   ```
4. To check CUDA and cuDNN installation:
   ```bash
   python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('cuDNN version:', torch.backends.cudnn.version()); print('CUDA version:', torch.version.cuda)"
   ```

Make sure the user on the remote server has access to docker.

```bash
sudo usermod -aG docker $USER
```