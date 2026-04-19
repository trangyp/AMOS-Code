# AMOS Platform API Gateway

Central API gateway for the AMOS 6-repository ecosystem.

## Overview

This is the **AMOS-Consulting** repository implementation - renamed to `amos-platform` to avoid package name collision with `amos-brain`.

It provides:
- REST API for all AMOS operations
- WebSocket for real-time events
- Centralized LLM routing (only component connecting to Ollama/LM Studio)
- Redis-based event bus for cross-repo communication

## Installation

```bash
pip install -e .
# Or with dev dependencies
pip install -e ".[dev]"
```

## Running

```bash
# Start the API server
python -m amos_platform.api.gateway

# Or use the CLI
amos-api
```

## API Endpoints

- `GET /` - API info
- `GET /v1/health` - Health check
- `GET /v1/status` - System status
- `POST /v1/chat` - Chat completion
- `GET /v1/models` - List available LLMs
- `POST /v1/models/run` - Run model inference
- `POST /v1/repo/scan` - Scan repository
- `POST /v1/repo/fix` - Apply fixes
- `POST /v1/workflow/run` - Run workflow
- `POST /v1/brain/run` - Execute brain cycle
- `WS /v1/ws/stream` - WebSocket event stream

## Architecture

The 6-repo integration:
- **AMOS-UNIVERSE** (`amos-universe`): Contracts, schemas, ontology
- **AMOS-Code** (`amos-brain`): Core brain library
- **AMOS-Platform** (`amos-platform`): This API gateway
- **AMOS-Claws**, **Mailinhconect**, **AMOS-Invest**: Frontend repos connect here

## Environment Variables

```bash
PORT=8000
HOST=0.0.0.0
REDIS_URL=redis://localhost:6379
DEBUG=false
```
