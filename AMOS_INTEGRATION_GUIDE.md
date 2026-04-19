# AMOS 5-Repository Integration Guide

## Quick Start

### 1. Package Names (Fix Collision First)

| Repository | Package Name | Import Path |
|------------|--------------|-------------|
| AMOS-Code | `amos-brain` | `import amos_brain` |
| AMOS-Consulting | `amos-platform` | `import amos_platform` |
| AMOS-Claws | `amos-claws` | Uses API, not direct import |
| Mailinhconect | `mailinh-web` | Uses API, not direct import |
| AMOS-Invest | `amos-invest` | Uses API, not direct import |

### 2. Repository Roles

```
AMOS-Code          → Core brain library (no public endpoint)
AMOS-Consulting    → Platform hub (api.amos.io)
AMOS-Claws         → Operator UI (claws.amos.io)
Mailinhconect      → Product UI (app.amos.io)
AMOS-Invest        → Investor UI (invest.amos.io)
```

### 3. Communication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Claws   │────→│ Platform │←────│  Invest  │
└──────────┘     │   API    │     └──────────┘
     │           └────┬─────┘           │
     │                │                  │
     └────────────────┼──────────────────┘
                      │
                      ▼
               ┌─────────────┐
               │ AMOS-Code   │
               │ (amos-brain)│
               └─────────────┘
```

## Installation

### Python Client

```bash
pip install amos-platform-client
```

### TypeScript/JavaScript Client

```bash
npm install @amos/platform-client
```

## Usage Examples

### Python SDK

```python
import asyncio
from amos_integration_client import AMOSClient

async def main():
    # Initialize client
    client = AMOSClient(
        base_url="https://api.amos.io",
        api_key="your-api-key",
    )
    
    # Check health
    health = await client.health()
    print(f"API Status: {health['status']}")
    
    # Chat with AI
    response = await client.chat.send_message(
        message="Analyze this code for security issues",
        workspace_id="ws-123",
        model="llama3.1",
    )
    print(f"AI: {response.message}")
    
    # Run repository scan
    task = await client.agents.run(
        agent_type="repo_scan",
        target_repo="https://github.com/user/repo",
        priority="high",
    )
    print(f"Task ID: {task.task_id}")
    
    # Check status
    status = await client.agents.get_status(task.task_id)
    print(f"Status: {status.status}")
    
    # Cleanup
    await client.close()

asyncio.run(main())
```

### TypeScript SDK

```typescript
import { AMOSClient } from '@amos/platform-client';

const client = new AMOSClient({
  baseUrl: 'https://api.amos.io',
  apiKey: 'your-api-key',
});

// Chat with AI
const response = await client.chat({
  message: 'Analyze this code',
  workspace_id: 'ws-123',
  model: 'llama3.1',
});
console.log(`AI: ${response.message}`);

// Run agent
const task = await client.runAgent({
  agent_type: 'repo_scan',
  target_repo: 'https://github.com/user/repo',
  priority: 'high',
});
console.log(`Task ID: ${task.task_id}`);

// WebSocket for real-time updates
const ws = client.connectWebSocket();
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};
```

### cURL Examples

```bash
# Health check (no auth)
curl https://api.amos.io/v1/health

# Chat (requires auth)
curl -X POST https://api.amos.io/v1/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, AMOS!",
    "workspace_id": "ws-123"
  }'

# Run agent
curl -X POST https://api.amos.io/v1/agent/run \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "repo_scan",
    "target_repo": "https://github.com/user/repo",
    "priority": "high"
  }'

# Check task status
curl https://api.amos.io/v1/agent/status/$TASK_ID \
  -H "Authorization: Bearer $JWT_TOKEN"
```

## WebSocket Events

### Connect

```javascript
const ws = new WebSocket('wss://api.amos.io/v1/ws/stream');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: '<jwt_token>'
  }));
  
  // Subscribe to channels
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'tasks'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'task.started':
      console.log('Task started:', data.task_id);
      break;
    case 'task.progress':
      console.log('Progress:', data.percent, '%');
      break;
    case 'task.completed':
      console.log('Task completed:', data.task_id);
      break;
    case 'repo.scan.completed':
      console.log('Scan completed:', data.scan_id);
      break;
  }
};
```

### Event Types

| Event | Description | Payload |
|-------|-------------|---------|
| `task.started` | Task execution began | `{task_id, type, timestamp}` |
| `task.progress` | Progress update | `{task_id, percent, message}` |
| `task.completed` | Task finished | `{task_id, result, duration}` |
| `task.failed` | Task failed | `{task_id, error, details}` |
| `repo.scan.completed` | Scan done | `{scan_id, findings_count}` |
| `repo.fix.applied` | Fix applied | `{fix_id, files_changed}` |
| `model.status_changed` | Model status | `{model_id, status}` |
| `notification` | General notification | `{level, message, metadata}` |

## Event Bus Topics

### Publishing Events

```python
from amos_event_bus import EventBus

bus = EventBus()
await bus.connect("redis://localhost:6379")

# Publish event
await bus.publish("mailinh.lead.created", {
    "lead_id": "lead-123",
    "source": "website",
    "email": "user@example.com"
})
```

### Subscribing to Events

```python
async def on_lead_created(event):
    print(f"New lead: {event['payload']['lead_id']}")

bus.subscribe("mailinh.lead.created", on_lead_created)
```

### Topic Reference

| Topic | Publisher | Subscribers |
|-------|-----------|-------------|
| `mailinh.lead.created` | Mailinhconect | AMOS-Consulting, Invest |
| `mailinh.contact.submitted` | Mailinhconect | AMOS-Consulting |
| `claws.session.started` | AMOS-Claws | AMOS-Consulting, Invest |
| `claws.agent.requested` | AMOS-Claws | AMOS-Consulting |
| `invest.report.requested` | AMOS-Invest | AMOS-Consulting |
| `invest.signal.generated` | AMOS-Consulting | AMOS-Invest |
| `repo.scan.completed` | AMOS-Consulting | Claws, Invest |
| `repo.fix.completed` | AMOS-Consulting | Claws |
| `model.run.completed` | AMOS-Consulting | Claws, Invest |
| `system.alert` | AMOS-Consulting | All |

## Migration Guide

### From Direct Imports to API Calls

**Before (ad hoc imports):**
```python
# In AMOS-Claws (wrong way)
from amos_brain import get_cognitive_runtime

brain = get_cognitive_runtime()
result = await brain.process(...)
```

**After (API calls):**
```python
# In AMOS-Claws (correct way)
from amos_integration_client import AMOSClient

client = AMOSClient(base_url="https://api.amos.io")
result = await client.chat.send_message(...)
```

### Renaming AMOS-Consulting Package

**Step 1: Update pyproject.toml**
```toml
[project]
name = "amos-platform"  # Changed from "amos-brain"
```

**Step 2: Update imports**
```python
# Old (in AMOS-Consulting)
from amos_brain import get_cognitive_runtime

# New
from amos_platform.core import get_cognitive_runtime
```

**Step 3: Update deployment**
```bash
# Update package in environment
pip uninstall amos-brain
pip install amos-platform
```

## Deployment

### Subdomains

| Subdomain | Target | Use Case |
|-----------|--------|----------|
| `api.amos.io` | AMOS-Consulting | API requests |
| `claws.amos.io` | AMOS-Claws | Operator interface |
| `app.amos.io` | Mailinhconect | Product interface |
| `invest.amos.io` | AMOS-Invest | Investor dashboard |

### Environment Variables

```bash
# AMOS-Consulting (Platform)
AMOS_API_HOST=0.0.0.0
AMOS_API_PORT=8000
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret
API_KEY_SALT=your-salt

# Client Applications
AMOS_API_URL=https://api.amos.io
AMOS_API_KEY=your-api-key
AMOS_WS_URL=wss://api.amos.io
```

## Testing

```python
import pytest
from amos_integration_client import AMOSClient

@pytest.mark.asyncio
async def test_chat():
    client = AMOSClient(base_url="http://localhost:8000")
    
    response = await client.chat.send_message(
        message="Hello",
        workspace_id="test-ws",
    )
    
    assert response.message is not None
    assert response.id is not None
    
    await client.close()
```

## Troubleshooting

### Connection Issues

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Authentication Errors

1. Check JWT token is not expired
2. Verify API key is valid
3. Ensure `Authorization` header format: `Bearer <token>`

### WebSocket Disconnections

```javascript
// Add reconnection logic
let ws;
function connect() {
  ws = new WebSocket('wss://api.amos.io/v1/ws/stream');
  ws.onclose = () => setTimeout(connect, 1000);
}
connect();
```

## Support

- API Documentation: https://docs.amos.io/api
- OpenAPI Spec: https://api.amos.io/openapi.json
- SDK Issues: https://github.com/amos-project/platform-client/issues
- Slack: #amos-platform
