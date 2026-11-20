# ==============================================================================
# Almost Real AI - Backend Dockerfile
# Python 3.11 + uv + FFmpeg + All video pipeline dependencies
# ==============================================================================
FROM python:3.11-slim

# Install system dependencies: FFmpeg (video encoding), curl (health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Install Python dependencies from pinned requirements file
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy backend source code
COPY . /app/backend

# Create runtime directories
RUN mkdir -p /app/storage/videos /app/storage/audio /app/storage/images /app/storage/temp /app/data /app/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
