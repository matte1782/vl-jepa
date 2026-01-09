# Docker Guide

> **Version**: v0.3.0
> **Image Size Target**: <3GB

!!! note "Port Information"
    The Docker image runs the **Gradio UI** on port **7860**.
    For the **FastAPI backend** (documented in [API Reference](guide/api.md)), run locally with `uvicorn` on port **8000**.
    See [Local Setup](local-setup.md) for FastAPI instructions.

---

## Quick Start

```bash
# Build the image
docker build -t lecture-mind .

# Run the container
docker run -p 7860:7860 lecture-mind

# Open in browser
open http://localhost:7860
```

---

## Using Docker Compose (Recommended)

```bash
# Start the application
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GRADIO_SERVER_NAME` | `0.0.0.0` | Server host binding |
| `GRADIO_SERVER_PORT` | `7860` | Server port |
| `GRADIO_ANALYTICS_ENABLED` | `false` | Disable telemetry |
| `HF_HOME` | `/app/cache/huggingface` | HuggingFace cache |
| `TORCH_HOME` | `/app/cache/torch` | PyTorch cache |

### Command Line Arguments

```bash
# Custom port
docker run -p 8080:8080 lecture-mind python -m vl_jepa.ui.app --port 8080

# Use real encoders (requires models)
docker run -p 7860:7860 lecture-mind python -m vl_jepa.ui.app --no-placeholders

# Create public share link
docker run -p 7860:7860 lecture-mind python -m vl_jepa.ui.app --share
```

---

## Volume Mounts

### Persist Model Cache

Models are downloaded on first use. Persist them to avoid re-downloading:

```bash
docker run -p 7860:7860 \
  -v lecture-mind-cache:/app/cache \
  lecture-mind
```

### Mount Local Videos

Process videos from your local machine:

```bash
docker run -p 7860:7860 \
  -v /path/to/videos:/app/videos:ro \
  lecture-mind
```

---

## Resource Requirements

### Minimum

- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 5GB (image + models)

### Recommended

- **CPU**: 4+ cores
- **RAM**: 8GB
- **Disk**: 10GB

### Memory Limits

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
    reservations:
      memory: 4G
```

---

## Building the Image

### Standard Build

```bash
docker build -t lecture-mind .
```

### Build with Custom Tag

```bash
docker build -t lecture-mind:v0.3.0 .
```

### Build with Build Arguments

```bash
# Use specific Python version
docker build --build-arg PYTHON_VERSION=3.11 -t lecture-mind .
```

### Multi-Platform Build

```bash
# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t lecture-mind .
```

---

## Health Check

The container includes a health check that verifies the Gradio server is responding:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' lecture-mind
```

Health check configuration:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 60 seconds (allow time for model loading)
- **Retries**: 3

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs lecture-mind

# Run interactively
docker run -it --rm lecture-mind /bin/bash
```

### Out of Memory

```bash
# Increase memory limit
docker run -p 7860:7860 --memory=8g lecture-mind
```

### Port Already in Use

```bash
# Use a different port
docker run -p 8080:7860 lecture-mind
```

### Permission Denied

The container runs as non-root user `appuser` (UID 1000). If mounting volumes:

```bash
# Ensure correct permissions
chmod -R 755 /path/to/mount
```

---

## Security

- Runs as non-root user (`appuser:appgroup`)
- No unnecessary packages installed
- Telemetry disabled by default
- Health check for container orchestration

---

## Image Layers

The Dockerfile uses multi-stage builds:

1. **Builder Stage**: Installs dependencies, creates wheel
2. **Runtime Stage**: Minimal image with only runtime deps

This reduces the final image size significantly.

---

## Updating

```bash
# Pull latest code
git pull

# Rebuild image
docker build -t lecture-mind .

# Restart container
docker-compose down && docker-compose up -d
```

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build Docker image
  run: docker build -t lecture-mind .

- name: Test Docker image
  run: |
    docker run -d -p 7860:7860 --name test lecture-mind
    sleep 30
    curl -f http://localhost:7860/ || exit 1
    docker stop test
```

### Docker Hub Publishing

```bash
# Tag for Docker Hub
docker tag lecture-mind username/lecture-mind:v0.3.0

# Push
docker push username/lecture-mind:v0.3.0
```

---

*For more information, see the [Home](index.md) page or [Local Setup Guide](local-setup.md).*
