# AMOS SuperBrain v3.0 - Production Docker Image
# Multi-stage build with security hardening
# Supports 75% health (no API keys in image) - inject via environment
# Python 3.11+ | Pydantic v2 | FastAPI | Health Monitoring | MCP Tools

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# =============================================================================
# Stage 2: Production
# =============================================================================
FROM python:3.11-slim

LABEL maintainer="AMOS Team" \
      version="3.0" \
      description="AMOS SuperBrain - AI Agent System" \
      health="75% - Ready for API key injection"

# Security: Create non-root user
RUN groupadd -r amos && useradd -r -g amos amos

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    git \
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
    APP_HOME=/app \
    PYTHONPATH=/app

WORKDIR $APP_HOME

# Copy installed packages from builder
COPY --from=builder /root/.local /home/amos/.local

# Copy AMOS SuperBrain modules
COPY --chown=amos:amos amos_brain/ $APP_HOME/amos_brain/
COPY --chown=amos:amos clawspring/ $APP_HOME/clawspring/
COPY --chown=amos:amos amos_observability/ $APP_HOME/amos_observability/

# Copy core files
COPY --chown=amos:amos \
    .env.example \
    requirements.txt \
    pyproject.toml \
    $APP_HOME/

# Copy scripts
COPY --chown=amos:amos scripts/ $APP_HOME/scripts/

# Create directories for persistence
RUN mkdir -p $APP_HOME/data $APP_HOME/logs $APP_HOME/exports \
    $APP_HOME/feature_flags $APP_HOME/memory $APP_HOME/amos_logs \
    && chown -R amos:amos $APP_HOME

# Switch to non-root user
USER amos

# Health check - validates 75% health level
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "
import sys
sys.path.insert(0, '/app')
from amos_brain import get_super_brain
brain = get_super_brain()
state = brain.get_state()
exit(0 if state.health_score >= 0.75 else 1)
" || exit 1

# Expose port
EXPOSE 8000

# Default: Run configuration validation then start
CMD ["sh", "-c", "
echo 'Validating AMOS SuperBrain configuration...'
python3 -c \"
import sys
sys.path.insert(0, '/app')
from amos_brain.config_validation import validate_configuration
validate_configuration()
\" && echo '✅ Configuration valid - starting AMOS SuperBrain at 75% health' && \
echo 'To reach 100% health, inject API keys via environment variables:' && \
echo '  OPENAI_API_KEY, ANTHROPIC_API_KEY, KIMI_API_KEY' && \
python3 -m amos_brain
"]
