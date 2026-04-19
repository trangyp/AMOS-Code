# AMOS Connection Architecture Decision

**Status:** ✅ Implemented  
**Date:** 2024-01-15  
**Owner:** Trang  

## Context

The AMOS ecosystem has multiple entry points (dashboards, APIs, WebSocket servers) that were experiencing "Connecting to server" issues due to:

1. **Port mismatches** - Dashboards pointing to wrong ports
2. **Blocking initialization** - Server startup waiting for 50MB+ knowledge base load
3. **No health probes** - Clients couldn't distinguish between "starting" and "failed"
4. **Port conflicts** - Multiple services trying to use port 8765

## Decision

Implement a **Kubernetes-inspired health probe pattern** with proper service orchestration.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AMOS Ecosystem                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: API Gateway (Flask)                               │
│  ├── Port: 5000                                            │
│  ├── /health  → Liveness probe (always returns 200)          │
│  ├── /ready   → Readiness probe (503 during init)            │
│  └── Background thread for AMOS initialization              │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: WebSocket Server                                   │
│  ├── Port: 8766 (changed from 8765)                        │
│  └── Real-time streaming for think/decide operations        │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Dashboards                                         │
│  ├── amos_dashboard.html  → Port 5000 API                 │
│  ├── dashboard/index.html → Port 5000 API                 │
│  └── Organism dashboard   → Port 8765 (separate)          │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Orchestration                                      │
│  └── start_amos_servers.py → Unified startup script       │
└─────────────────────────────────────────────────────────────┘
```

## Health Check Strategy

Following Kubernetes best practices, we implement two distinct probes:

### 1. Liveness Probe (`/health`)
- **Purpose:** Is the server running?
- **Returns:** Always 200 if server is up
- **Use:** Kubernetes restart decisions
- **Implementation:** Immediate response, no dependency checks

### 2. Readiness Probe (`/ready`)
- **Purpose:** Is the server ready to serve requests?
- **Returns:** 503 during initialization, 200 when ready
- **Use:** Load balancer routing decisions
- **Implementation:** Checks AMOS initialization state

## Connection Flow

```
Dashboard Load
     ↓
Show "Connecting to API..."
     ↓
Call /health (should return 200 immediately)
     ↓
Call /ready
     ├─ If 503: Show "AMOS Initializing..." → Retry in 3s
     └─ If 200: Show "Connected to AMOS API"
```

## Port Allocation

| Service | Old Port | New Port | Status |
|---------|----------|----------|--------|
| API Server | - | 5000 | ✅ Primary |
| Organism API | 8765 | 8765 | ✅ Separate |
| WebSocket | 8765 | 8766 | ✅ Fixed conflict |
| Dashboard WS | 8765 | 8766 | ✅ Fixed |

## Implementation Details

### API Server (`amos_api_enhanced.py`)

```python
# Background initialization
def _init_amos_background():
    """Initialize AMOS in background thread."""
    # ... initialization code

# Fast liveness check
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})  # Always immediate

# Readiness check with state
@app.route("/ready", methods=["GET"])
def readiness_check():
    if amos_system is None:
        return jsonify({"status": "not_ready"}), 503
    if not getattr(amos_system, '_initialized', False):
        return jsonify({"status": "initializing"}), 503
    return jsonify({"status": "ready"})
```

### Dashboard (`amos_dashboard.html`)

```javascript
async function checkConnection() {
    // 1. Check server is alive
    const health = await fetch(`${API_BASE}/health`);
    if (!health.ok) {
        showError("Server not responding");
        return;
    }
    
    // 2. Check if ready to serve
    const ready = await fetch(`${API_BASE}/ready`);
    if (ready.status === 503) {
        showMessage("AMOS Initializing... Please wait");
        setTimeout(checkConnection, 3000);  // Retry
        return;
    }
    
    // 3. Connected!
    showSuccess("Connected to AMOS API");
}
```

## Unified Startup Script

Created `start_amos_servers.py` that:
- Starts API server and WebSocket server concurrently
- Performs health checks on startup
- Shows real-time status
- Gracefully shuts down all services on Ctrl+C

## Testing

```bash
# Start unified servers
python start_amos_servers.py

# Or start individually
python amos_api_enhanced.py        # Port 5000
python websocket_server.py         # Port 8766

# Test endpoints
curl http://localhost:5000/health  # Should return immediately
curl http://localhost:5000/ready   # 503 until initialized, then 200
```

## Consequences

### Positive
- ✅ Server starts immediately (no blocking)
- ✅ Clear visibility into initialization state
- ✅ Proper separation of concerns (liveness vs readiness)
- ✅ No port conflicts
- ✅ Unified startup orchestration

### Negative
- ⚠️ Slightly more complex health check logic
- ⚠️ Dashboard needs to handle 503 responses

## References

- [Kubernetes Health Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Flask CORS Best Practices](https://flask-cors.readthedocs.io/)
- [WebSocket Server Port Conflicts](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
