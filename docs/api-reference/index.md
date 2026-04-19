# API Reference

Complete reference for AMOS APIs and SDKs.

## Overview

AMOS provides multiple interfaces for integration:

- **REST API**: HTTP endpoints for all AMOS capabilities
- **WebSocket**: Real-time communication with agents
- **Python SDK**: Native Python client library
- **CLI**: Command-line interface for quick tasks

## Authentication

Most API endpoints require authentication via JWT token.

```bash
# Get a token
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use the token
curl http://localhost:8080/api/v1/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Sections

### REST API

- [REST API Endpoints](rest-api.md) - Complete HTTP API reference
- [Authentication](rest-api.md#authentication) - Login and token management
- [Agents](rest-api.md#agents) - Spawn and manage agents
- [Orchestration](rest-api.md#orchestration) - Execute multi-agent tasks
- [Memory](rest-api.md#memory) - Access and manage memory
- [Laws](rest-api.md#laws) - Validate actions against laws

### WebSocket

- [WebSocket API](websocket.md) - Real-time agent communication
- [Connection](websocket.md#connection) - Establishing WebSocket connections
- [Messages](websocket.md#messages) - Message formats and protocols
- [Streaming](websocket.md#streaming) - Real-time response streaming

### Python SDK

- [Python SDK](python-sdk.md) - Native Python client
- [Installation](python-sdk.md#installation) - Installing the SDK
- [Quick Start](python-sdk.md#quick-start) - Basic SDK usage
- [Advanced Usage](python-sdk.md#advanced-usage) - Complex scenarios

## OpenAPI Specification

AMOS provides an OpenAPI 3.0 specification for automatic client generation:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI JSON**: `http://localhost:8080/openapi.json`

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Errors use standard HTTP status codes with detailed messages:

```json
{
  "success": false,
  "error": "Agent not found",
  "code": "AGENT_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Rate Limiting

API requests are rate-limited per IP address:

- **Default**: 100 requests per minute
- **Authenticated**: 1000 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

---

!!! tip "Interactive Documentation"
    Visit `http://localhost:8080/docs` when AMOS is running to explore the API interactively with Swagger UI.
