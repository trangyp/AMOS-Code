# AMOS 5-Repository Integration Architecture

## Executive Summary

This document defines the unified integration protocol for 5 AMOS repositories to communicate through **one shared protocol** instead of ad hoc imports.

## Repository Roles

| Repository | Role | Package Name | Public Endpoint |
|------------|------|--------------|-----------------|
| **AMOS-Code** | Core brain/package layer | `amos-brain` | None (library only) |
| **AMOS-Consulting** | Backend + orchestrator + API gateway | `amos-platform` | `api.amos.io` |
| **AMOS-Claws** | Agent/chat/operator frontend | `amos-claws` | `claws.amos.io` |
| **Mailinhconect** | Product/public frontend | `mailinh-web` | `app.amos.io` |
| **AMOS-Invest** | Investor/analytics frontend | `amos-invest` | `invest.amos.io` |

## Integration Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                      AMOS-Consulting                              │
│                    (Central Hub)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  REST API   │  │  WebSocket  │  │     Event Bus           │  │
│  │  /v1/*      │  │  /ws/*      │  │  Redis Streams/NATS     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │              │                    │
           ▼              ▼                    ▼
    ┌──────────┐   ┌──────────┐          ┌──────────┐
    │AMOS-Claws│   │Mailinh-  │          │AMOS-     │
    │(Operator)│   │connect   │          │Invest    │
    └──────────┘   └──────────┘          └──────────┘
           │                                    │
           └────────────┬───────────────────────┘
                        ▼
               ┌─────────────────┐
               │   AMOS-Code     │
               │  (amos-brain)   │
               │  Core Library   │
               └─────────────────┘
```

## Communication Lanes

### Lane 1: Synchronous (Request/Response)

**Purpose**: Immediate request/response operations

**Protocols**:
- **HTTP REST API** for stateless operations
- **WebSocket** for live updates and streaming

**Implementation**:
- `AMOS-Consulting` exposes FastAPI-based API gateway
- All frontends (Claws, Mailinhconect, Invest) connect to this hub
- `AMOS-Code` is NOT directly called by frontends

### Lane 2: Asynchronous (Cross-Repo Events)

**Purpose**: Background processing, decoupled workflows, notifications

**Protocol**: Redis Streams or NATS

**Benefits**:
- Fire-and-forget event publishing
- Decoupled service communication
- Reliable message delivery
- Horizontal scalability

## Package Name Resolution

### The Collision Problem

Currently both `AMOS-Code` and `AMOS-Consulting` may publish as `amos-brain`.

### The Solution

| Repository | Old Name | New Name | Import Path |
|------------|----------|----------|-------------|
| AMOS-Code | `amos-brain` | `amos-brain` | `import amos_brain` |
| AMOS-Consulting | `amos-brain` | `amos-platform` | `import amos_platform` |
| AMOS-Claws | `amos` | `amos-claws` | `import amos_claws` |

### Migration Steps

1. **AMOS-Consulting**: Rename package in `pyproject.toml`:
   ```toml
   [project]
   name = "amos-platform"
   ```

2. **Update all imports** in AMOS-Consulting from `amos_brain` to `amos_platform`

3. **AMOS-Claws**: Update to import from hub API instead of direct brain imports

## API Contract Specification

### Base URLs

```yaml
Development:
  API: http://localhost:8000
  WebSocket: ws://localhost:8000/ws
  
Staging:
  API: https://api-staging.amos.io
  WebSocket: wss://api-staging.amos.io/ws
  
Production:
  API: https://api.amos.io
  WebSocket: wss://api.amos.io/ws
```

### Authentication

All endpoints require Bearer token authentication:

```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
X-Workspace-ID: <workspace_id>
```

### REST Endpoints

#### Core Operations

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/v1/chat` | Send chat message, get response | Required |
| POST | `/v1/agent/run` | Execute agent task | Required |
| GET | `/v1/agent/status/{task_id}` | Check agent task status | Required |
| POST | `/v1/agent/cancel/{task_id}` | Cancel running agent | Required |

#### Repository Operations

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/v1/repo/scan` | Scan repository for issues | Required |
| POST | `/v1/repo/fix` | Apply fixes to repository | Required |
| GET | `/v1/repo/status/{scan_id}` | Get scan/fix status | Required |
| GET | `/v1/repo/reports/{scan_id}` | Download scan report | Required |

#### Workflow Operations

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/v1/workflow/run` | Execute workflow | Required |
| GET | `/v1/workflow/status/{workflow_id}` | Check workflow status | Required |
| POST | `/v1/workflow/cancel/{workflow_id}` | Cancel workflow | Required |

#### Model/LLM Operations

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/v1/models` | List available models | Required |
| GET | `/v1/models/{model_id}/status` | Check model status | Required |
| POST | `/v1/models/{model_id}/load` | Load model into memory | Admin |
| POST | `/v1/models/{model_id}/unload` | Unload model | Admin |

#### Task Management

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/v1/tasks` | List user tasks | Required |
| GET | `/v1/tasks/{task_id}` | Get task details | Required |
| DELETE | `/v1/tasks/{task_id}` | Delete task | Required |

#### System Operations

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/v1/health` | System health check | None |
| GET | `/v1/status` | Detailed system status | Required |
| GET | `/v1/metrics` | Prometheus metrics | Service |

### WebSocket Channels

#### Connection

```javascript
const ws = new WebSocket('wss://api.amos.io/ws/v1/stream');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: '<jwt_token>'
  }));
};
```

#### Incoming Events (Server → Client)

| Event Type | Payload | Description |
|------------|---------|-------------|
| `task.started` | `{task_id, type, timestamp}` | Task execution began |
| `task.progress` | `{task_id, percent, message}` | Progress update |
| `task.completed` | `{task_id, result, duration}` | Task finished successfully |
| `task.failed` | `{task_id, error, details}` | Task failed |
| `repo.scan.completed` | `{scan_id, findings_count}` | Repository scan done |
| `repo.fix.applied` | `{fix_id, files_changed}` | Fix applied successfully |
| `model.status_changed` | `{model_id, status}` | Model loaded/unloaded |
| `notification` | `{level, message, metadata}` | General notification |

#### Outgoing Events (Client → Server)

| Event Type | Payload | Description |
|------------|---------|-------------|
| `subscribe` | `{channel: 'tasks'}` | Subscribe to channel |
| `unsubscribe` | `{channel: 'tasks'}` | Unsubscribe from channel |
| `ping` | `{}` | Keep connection alive |

## Event Bus Topics

### Domain Events

| Topic | Publisher | Subscribers | Payload |
|-------|-----------|-------------|---------|
| `mailinh.lead.created` | Mailinhconect | AMOS-Consulting, AMOS-Invest | `{lead_id, source, timestamp}` |
| `mailinh.contact.submitted` | Mailinhconect | AMOS-Consulting | `{contact_id, form_data}` |
| `claws.session.started` | AMOS-Claws | AMOS-Consulting, AMOS-Invest | `{session_id, user_id, timestamp}` |
| `claws.agent.requested` | AMOS-Claws | AMOS-Consulting | `{agent_type, params, priority}` |
| `invest.report.requested` | AMOS-Invest | AMOS-Consulting | `{report_type, date_range}` |
| `invest.signal.generated` | AMOS-Consulting | AMOS-Invest | `{signal_type, confidence, data}` |

### System Events

| Topic | Publisher | Subscribers | Payload |
|-------|-----------|-------------|---------|
| `repo.scan.completed` | AMOS-Consulting | AMOS-Claws, AMOS-Invest | `{scan_id, repo_url, summary}` |
| `repo.fix.completed` | AMOS-Consulting | AMOS-Claws | `{fix_id, pr_url, files_changed}` |
| `model.run.completed` | AMOS-Consulting | AMOS-Claws, Invest | `{run_id, model_id, metrics}` |
| `system.alert` | AMOS-Consulting | All | `{severity, component, message}` |

### Event Payload Schema

```json
{
  "event_id": "uuid",
  "event_type": "mailinh.lead.created",
  "timestamp": "2026-01-19T10:30:00Z",
  "source": "mailinhconect",
  "payload": {
    // Event-specific data
  },
  "metadata": {
    "version": "1.0",
    "trace_id": "uuid"
  }
}
```

## Shared Contract Layer

### OpenAPI Specification

Location: `AMOS-Consulting/openapi/v1.yaml`

Generated clients:
- TypeScript client: `sdk/typescript/`
- Python client: `sdk/python/`

### Core Data Models

#### ChatRequest
```typescript
interface ChatRequest {
  message: string;
  context?: Message[];
  model?: string;
  temperature?: number;
  max_tokens?: number;
  workspace_id: string;
}
```

#### ChatResponse
```typescript
interface ChatResponse {
  id: string;
  message: string;
  model: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  timestamp: string;
}
```

#### AgentRunRequest
```typescript
interface AgentRunRequest {
  agent_type: 'code_review' | 'repo_scan' | 'fix_generator' | 'custom';
  target_repo?: string;
  parameters: Record<string, any>;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  callback_url?: string;
}
```

#### AgentRunResult
```typescript
interface AgentRunResult {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  agent_type: string;
  result?: any;
  error?: string;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
}
```

#### RepoScanRequest
```typescript
interface RepoScanRequest {
  repo_url: string;
  branch?: string;
  scan_types: ('security' | 'performance' | 'style' | 'architecture')[];
  depth: 'quick' | 'standard' | 'deep';
}
```

#### RepoScanResult
```typescript
interface RepoScanResult {
  scan_id: string;
  repo_url: string;
  status: string;
  findings: Finding[];
  summary: {
    total_files: number;
    issues_found: number;
    critical: number;
    warning: number;
    info: number;
  };
  report_url: string;
}
```

#### ModelInfo
```typescript
interface ModelInfo {
  id: string;
  name: string;
  provider: 'ollama' | 'lmstudio' | 'openai' | 'anthropic' | 'vllm';
  status: 'available' | 'loading' | 'loaded' | 'unavailable';
  capabilities: string[];
  context_window: number;
  loaded_at?: string;
}
```

#### TaskStatus
```typescript
interface TaskStatus {
  id: string;
  type: string;
  status: string;
  progress?: number;
  message?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  error?: string;
}
```

#### ApiError
```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    request_id: string;
    timestamp: string;
  };
}
```

## Local/Offline LLM Architecture

### Centralized LLM Access

**Only** `AMOS-Consulting` connects directly to:
- Ollama
- LM Studio
- llama.cpp server
- vLLM
- SGLang
- LiteLLM

### LLM Proxy Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /v1/models` | List all available models |
| `POST /v1/chat/completions` | OpenAI-compatible chat endpoint |
| `POST /v1/completions` | OpenAI-compatible completion endpoint |
| `POST /v1/embeddings` | Text embeddings |

### Model Routing

```yaml
Model Routing Rules:
  - pattern: "llama*"
    backend: ollama
    endpoint: http://localhost:11434
    
  - pattern: "qwen*"
    backend: vllm
    endpoint: http://localhost:8000
    
  - pattern: "gpt*"
    backend: openai
    endpoint: https://api.openai.com/v1
```

## Deployment Layout

### Subdomain Routing

| Subdomain | Target Repository | Purpose |
|-----------|-------------------|---------|
| `api.amos.io` | AMOS-Consulting | API Gateway |
| `claws.amos.io` | AMOS-Claws | Operator Interface |
| `app.amos.io` | Mailinhconect | Product Frontend |
| `invest.amos.io` | AMOS-Invest | Investor Dashboard |
| `docs.amos.io` | AMOS-Consulting | API Documentation |

### Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CDN (CloudFront)                    │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ claws.amos  │    │ app.amos.io │    │invest.amos  │
   │  (Static)   │    │  (Static)   │    │  (Static)   │
   └─────────────┘    └─────────────┘    └─────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  api.amos.io        │
                    │  (AMOS-Consulting)  │
                    │  - Load Balancer    │
                    │  - FastAPI Cluster  │
                    └─────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   Redis     │    │ PostgreSQL  │    │   Ollama    │
   │  (Events)   │    │  (Data)     │    │   (LLM)     │
   └─────────────┘    └─────────────┘    └─────────────┘
```

## Implementation Phases

### Phase 1: Package Rename (Week 1)

- [ ] Rename AMOS-Consulting package to `amos-platform`
- [ ] Update all internal imports
- [ ] Test package installation
- [ ] Update CI/CD pipelines

### Phase 2: Core API (Week 2-3)

- [ ] Implement REST API endpoints
- [ ] Add authentication/authorization
- [ ] Create shared OpenAPI spec
- [ ] Generate TypeScript client SDK

### Phase 3: WebSocket Layer (Week 3-4)

- [ ] Implement WebSocket server
- [ ] Add channel subscription management
- [ ] Create event broadcasting system
- [ ] Test with Claws frontend

### Phase 4: Event Bus (Week 4-5)

- [ ] Set up Redis Streams
- [ ] Implement event publishers
- [ ] Create event consumers
- [ ] Add retry and dead letter handling

### Phase 5: LLM Integration (Week 5-6)

- [ ] Centralize LLM access in AMOS-Consulting
- [ ] Implement model routing
- [ ] Add health checks for LLM backends
- [ ] Test with all frontends

### Phase 6: Frontend Migration (Week 6-8)

- [ ] Update AMOS-Claws to use API
- [ ] Update Mailinhconect to use API
- [ ] Update AMOS-Invest to use API
- [ ] Remove direct brain imports
- [ ] Add client-side caching

### Phase 7: Production Deploy (Week 8-10)

- [ ] Set up staging environment
- [ ] Configure monitoring
- [ ] Load testing
- [ ] Production deployment
- [ ] Documentation

## Anti-Patterns to Avoid

❌ **Do NOT**:
- Have all 5 repos import each other directly
- Let each repo manage its own model backend
- Keep both Python repos named `amos-brain`
- Make HTML repos hold backend logic
- Use synchronous HTTP for long-running tasks
- Share database connections across repos

✅ **DO**:
- Use the API gateway for all cross-repo communication
- Centralize LLM access in one place
- Use event bus for async workflows
- Maintain clear separation of concerns
- Use generated clients from OpenAPI spec
- Cache aggressively at the edge

## Success Metrics

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 200ms |
| WebSocket Latency | < 50ms |
| Event Delivery Time | < 100ms |
| Cross-repo Import Count | 0 |
| Package Name Conflicts | 0 |
| Frontend Bundle Size | < 500KB |
| System Availability | 99.9% |

## Conclusion

This architecture provides:
- **Single source of truth**: AMOS-Consulting is the only backend
- **Clean separation**: Each repo has one clear responsibility
- **Scalable communication**: Sync + async lanes for different needs
- **Type safety**: Generated clients from shared OpenAPI spec
- **Operational simplicity**: One deployment target for backend

The result is **one real system** instead of 5 disconnected repos.
