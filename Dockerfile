# Lecture Mind - Multi-stage Dockerfile
# IMPLEMENTS: v0.3.0 G4 - Docker image
#
# Build: docker build -t lecture-mind .
# Run:   docker run -p 7860:7860 lecture-mind
#
# Target: <3GB image size

# ==============================================================================
# Stage 1: Builder - Install dependencies and build wheel
# ==============================================================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies first (better caching)
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package with all extras except dev
RUN pip install --upgrade pip && \
    pip install ".[ml,audio,ui]"

# ==============================================================================
# Stage 2: Runtime - Minimal production image
# ==============================================================================
FROM python:3.11-slim as runtime

# Labels
LABEL org.opencontainers.image.title="Lecture Mind" \
      org.opencontainers.image.description="AI-powered lecture summarizer with visual and transcript search" \
      org.opencontainers.image.version="0.3.0" \
      org.opencontainers.image.authors="Matteo Panzeri" \
      org.opencontainers.image.source="https://github.com/matte1782/lecture-mind" \
      org.opencontainers.image.licenses="MIT"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    # Gradio settings
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    # Disable telemetry
    GRADIO_ANALYTICS_ENABLED=false \
    # Model cache directory
    HF_HOME=/app/cache/huggingface \
    TORCH_HOME=/app/cache/torch

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # FFmpeg for audio extraction
    ffmpeg \
    # OpenCV dependencies (libgl1 replaces libgl1-mesa-glx in newer Debian)
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --create-home appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create cache directories with correct permissions
RUN mkdir -p /app/cache/huggingface /app/cache/torch && \
    chown -R appuser:appgroup /app

# Copy application code
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup pyproject.toml README.md ./

# Switch to non-root user
USER appuser

# Expose Gradio port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/')" || exit 1

# Default command: Launch Gradio UI
CMD ["python", "-m", "vl_jepa.ui.app", "--port", "7860"]
