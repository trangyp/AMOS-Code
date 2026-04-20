# AMOS Brain v14.0.0 - Production Docker Image
# Multi-stage build with security hardening
# Unified build: pip install from pyproject.toml (no source copy)
# Python 3.11+ | Pydantic v2 | FastAPI | Health Monitoring
#
# BUILD: docker build -t amos-brain:14.0.0 .
# RUN:   docker run -p 8000:8000 -e OPENAI_API_KEY=xxx amos-brain:14.0.0

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.14-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy package definition first for better caching
COPY pyproject.toml README.md ./

# Install the package and all extras (server, database, security, events, ml)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user ".[server,database,security,events,ml]"

# =============================================================================
# Stage 2: Production
# =============================================================================
FROM python:3.14-slim

LABEL maintainer="AMOS Team <trang@amos-project.dev>" \
      version="14.0.0" \
      description="AMOS Brain Cognitive OS - 14-layer deterministic cognitive architecture" \
      org.opencontainers.image.source="https://github.com/trangyp/AMOS-Code" \
      org.opencontainers.image.documentation="https://github.com/trangyp/AMOS-Code/blob/main/AMOS_BRAIN_GUIDE.md"

# Security: Create non-root user
RUN groupadd -r amos && useradd -r -g amos amos

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PATH=/home/amos/.local/bin:$PATH \
    APP_HOME=/app

WORKDIR $APP_HOME

# Copy installed packages from builder
COPY --from=builder /root/.local /home/amos/.local

# Copy only necessary config files (no source code - already installed)
COPY --chown=amos:amos .env.example $APP_HOME/

# Create directories for persistence
RUN mkdir -p $APP_HOME/data $APP_HOME/logs $APP_HOME/exports \
    && chown -R amos:amos $APP_HOME

# Switch to non-root user
USER amos

# Health check - uses installed package (no sys.path hacks)
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "from amos_brain import get_super_brain; b=get_super_brain(); exit(0 if b.get_state().health_score >= 0.75 else 1)" || exit 1

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/sh\necho "AMOS Brain v14.0.0 - Starting..."\npython3 -c "from amos_brain.config_validation import validate_configuration; validate_configuration()" && echo "✅ Configuration valid - starting at 75% health" && echo "To reach 100% health, inject API keys via environment:" && echo "  OPENAI_API_KEY, ANTHROPIC_API_KEY, KIMI_API_KEY" && exec amos-brain' > /home/amos/start.sh && chmod +x /home/amos/start.sh

# Default: Run startup script
CMD ["/home/amos/start.sh"]
