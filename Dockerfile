# AMOS Brain + ClawSpring Docker Image
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY setup.py .
COPY README.MD .
COPY amos_brain/ ./amos_brain/
COPY _AMOS_BRAIN/ ./_AMOS_BRAIN/

# Install Python dependencies
RUN pip install --no-cache-dir --user -e .

# Stage 2: Production
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH=/root/.local/bin:$PATH \
    AMOS_BRAIN_PATH=/app/_AMOS_BRAIN

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY amos_brain/ ./amos_brain/
COPY clawspring/ ./clawspring/
COPY _AMOS_BRAIN/ ./_AMOS_BRAIN/
COPY tests/ ./tests/

# Copy entry points
COPY amos.py .
COPY amos_clawspring.py .
COPY amos_mcp_server.py .
COPY demo_amos_brain.py .
COPY amos_api_server.py .
COPY websocket_server.py .
COPY requirements-deploy.txt .
COPY amos .

# Create directories for persistence
RUN mkdir -p /app/data /app/logs /app/memory

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from amos_brain import get_amos_integration; a = get_amos_integration(); print('OK' if a.get_status()['initialized'] else 'FAIL')" || exit 1

# Default command (API server mode for neurosyncai.tech)
ENV PORT=5000
EXPOSE 5000 8765
CMD ["python3", "amos_api_server.py"]
