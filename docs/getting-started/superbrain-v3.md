# AMOS SuperBrain v3.0 - Getting Started

**Production-grade AI Agent System at 75% Health**

---

## 🎯 What is SuperBrain v3.0?

AMOS SuperBrain v3.0 is a **complete 10-layer AI agent architecture** designed for production deployment. It provides a fully-functional AI system at 75% health (without API keys) with a clear path to 100% health when LLM API keys are configured.

### Architecture Highlights

```
Layer 10: Web API (FastAPI + WebSocket)
Layer 9:  CLI Interface (Typer + Rich)
Layer 8:  A2A Multi-Agent Protocol
Layer 7:  Tiered Memory (L1/L2/L3)
Layer 6:  Docker + CI/CD
Layer 5:  Comprehensive Testing
Layer 4:  Health Monitoring
Layer 3:  10 MCP Tools
Layer 2:  Math Framework (22 equations)
Layer 1:  Configuration Management
```

---

## 🚀 Quick Start (3 Options)

### Option 1: CLI Interface (Fastest)

```bash
# Check system status
python3 amos_superbrain_cli.py status

# List all tools
python3 amos_superbrain_cli.py tools --list

# Test a tool
python3 amos_superbrain_cli.py tools --test calculate

# Create A2A task
python3 amos_superbrain_cli.py task "Calculate 2+2" --capability calculate

# View A2A agents
python3 amos_superbrain_cli.py agents
```

### Option 2: Web API (REST + WebSocket)

```bash
# Start the API server
python3 amos_superbrain_api.py

# Access interactive docs
open http://localhost:8000/docs

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/status
curl http://localhost:8000/tools
```

### Option 3: Docker Deployment (Production)

```bash
# Deploy full stack
docker-compose up -d

# Check logs
docker-compose logs -f amos-superbrain

# Access API
curl http://localhost:8000/health
```

---

## 📊 System Health

### At 75% Health (Default)

The system is **fully functional** without any API keys:

| Component | Status | Details |
|-----------|--------|---------|
| Math Framework | ✅ Active | 22 equations, 4 invariants |
| MCP Tools | ✅ Active | 10 tools (built-in + extended) |
| A2A Protocol | ✅ Active | Multi-agent orchestration |
| Memory Architecture | ✅ Active | L1/L2/L3 tiers |
| Health Monitoring | ✅ Active | Production observability |
| CLI Interface | ✅ Active | Rich terminal UI |
| Web API | ✅ Active | FastAPI + WebSocket |
| Docker/CI/CD | ✅ Active | Production deployment |

### Reaching 100% Health

Configure LLM API keys to unlock full capabilities:

```bash
# Interactive configuration
./scripts/configure_api_keys.sh

# Or manually edit .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
KIMI_API_KEY=...

# Restart system
docker-compose restart
```

---

## 🛠️ Available Tools

### Built-in Tools (5)

| Tool | Description | Example |
|------|-------------|---------|
| `analyze_code_structure` | Analyze Python code | `amos task "Analyze amos_brain.py"` |
| `execute_shell_command` | Safe shell execution | `amos task "Run ls -la"` |
| `search_files` | File pattern search | `amos task "Find all .py files"` |
| `get_system_info` | System information | `amos task "Get CPU info"` |
| `validate_json` | JSON validation | `amos task "Validate config.json"` |

### Extended Tools (5)

| Tool | Description | API Endpoint |
|------|-------------|--------------|
| `calculate` | Safe math evaluation | `POST /tools/calculate/execute` |
| `file_read_write` | File I/O operations | `POST /tools/file_read_write/execute` |
| `database_query` | SQL queries | `POST /tools/database_query/execute` |
| `web_search` | DuckDuckGo search | `POST /tools/web_search/execute` |
| `git_operations` | Git status/log/diff | `POST /tools/git_operations/execute` |

---

## 🤖 A2A Multi-Agent System

### Overview

AMOS SuperBrain implements Google's **Agent2Agent (A2A) Protocol** for multi-agent orchestration:

- **Agent Discovery**: Automatic capability advertisement
- **Task Routing**: Intelligent agent selection
- **Message Passing**: Standardized communication
- **State Management**: Task lifecycle tracking

### Using A2A

```python
from amos_brain.a2a_orchestrator import get_a2a_orchestrator

# Get orchestrator
orchestrator = get_a2a_orchestrator()

# Discover agents
agents = orchestrator.discover_agents(capability="calculate")

# Route task
task = orchestrator.route_task(
    message="Calculate 2+2",
    capability="calculate"
)

print(f"Task {task.id} assigned to {task.assigned_agent}")
```

### CLI Usage

```bash
# List agents
amos agents

# Create task
amos task "Analyze code structure" --capability code_analysis
```

---

## 🧠 Memory Architecture

### Tiered Storage

| Tier | Technology | Speed | Use Case |
|------|------------|-------|----------|
| **L1** | In-Memory Cache | Fastest | Active conversations |
| **L2** | SQLite | Fast | Persistent sessions |
| **L3** | File System | Slower | Long-term archival |

### API Usage

```python
from amos_brain.memory_architecture import get_memory_manager

# Store memory
manager = get_memory_manager()

from datetime import datetime, timezone
from amos_brain.memory_architecture import MemoryEntry

entry = MemoryEntry(
    id="conv-001",
    content="User asked about Python",
    timestamp=datetime.now(timezone.utc),
    session_id="session-001",
    memory_type="conversation",
    priority=8
)

manager.store(entry)

# Search memory
results = manager.search(
    session_id="session-001",
    memory_type="conversation",
    limit=10
)
```

---

## 📡 API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/status` | GET | System status |
| `/tools` | GET | List tools |
| `/tools/{name}/execute` | POST | Execute tool |
| `/agents` | GET | List agents |
| `/agents/task` | POST | Create task |
| `/memory` | GET | Memory stats |
| `/memory/search` | POST | Search memory |
| `/config` | GET | Config status |

### WebSocket

Connect to `ws://localhost:8000/ws` for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Health:', data.health_score);
};

// Send ping
ws.send(JSON.stringify({type: 'ping'}));
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Application
APP_NAME=AMOS SuperBrain
DEBUG=false
ENVIRONMENT=production

# LLM Providers (for 100% health)
OPENAI_API_KEY=sk-...          # Optional
ANTHROPIC_API_KEY=sk-ant-...   # Optional
KIMI_API_KEY=...               # Optional
OLLAMA_BASE_URL=http://localhost:11434

# Security
SECRET_KEY=your-secret-key

# Observability
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL=60
```

### Validation

```bash
# Validate configuration
python3 -c "
from amos_brain.config_validation import ConfigValidator
validator = ConfigValidator()
validator.print_report()
"
```

---

## 📈 Monitoring

### Health Checks

```bash
# Via CLI
amos status

# Via API
curl http://localhost:8000/health

# Via WebSocket
# Connect to ws://localhost:8000/ws
```

### Metrics

The system exposes:

- Health score (0-100%)
- Tool execution counts
- Memory usage (L1/L2/L3)
- A2A agent statistics
- API response times

---

## 🚀 Production Deployment

### Docker Compose

```yaml
# docker-compose.superbrain.yml
version: '3.8'
services:
  amos-superbrain:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
    volumes:
      - ./data:/app/data
      - ./memory:/app/memory
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/amos-superbrain-deployment.yaml
kubectl apply -f k8s/amos-superbrain-service.yaml
```

---

## 🆘 Troubleshooting

### Common Issues

**Health score is 0%**
```bash
# Initialize system
python3 -c "from amos_brain import initialize_super_brain; initialize_super_brain()"
```

**API not responding**
```bash
# Check if API is running
curl http://localhost:8000/health

# Check logs
python3 amos_superbrain_api.py  # Run in foreground
```

**Tools not working**
```bash
# Test specific tool
amos tools --test calculate
```

### Getting Help

- **Documentation**: https://amos-ai.readthedocs.io
- **GitHub Issues**: https://github.com/trangyp/AMOS-Code/issues
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🎓 Next Steps

1. **Configure API Keys** for 100% health
2. **Explore A2A Protocol** for multi-agent workflows
3. **Build Custom Tools** using MCP framework
4. **Deploy to Production** with Docker/Kubernetes
5. **Integrate with Your Stack** via REST API

---

## 📊 System Capabilities Summary

```
✅ Math Framework: 22 equations, 4 invariants
✅ Tools: 10 MCP-compliant (5 built-in + 5 extended)
✅ Memory: L1/L2/L3 tiered architecture
✅ A2A: Multi-agent orchestration
✅ API: FastAPI with WebSocket
✅ CLI: Rich terminal interface
✅ Docker: Production deployment
✅ CI/CD: GitHub Actions
✅ Testing: Comprehensive pytest suite
✅ Health: 75% (100% with API keys)
```

---

**Ready to build with AMOS SuperBrain v3.0!** 🚀
