# AMOS 6-Repository Platform Architecture
## Synthetic Monorepo with NATS + Temporal + ArgoCD + Renovate

> **Version**: 1.0.0  
> **Last Updated**: 2026-04-19  
> **Status**: Implementation Ready

---

## Executive Summary

This document defines the complete architecture for connecting 6 AMOS repositories into a unified platform that behaves as one coordinated system. The architecture uses:

- **Nx Synthetic Monorepo** - Cross-repo visibility without code merging
- **NATS** - Real-time pub/sub and request/reply messaging
- **Temporal** - Durable workflows for long-running operations
- **Argo CD** - GitOps continuous deployment
- **Renovate** - Automated dependency management

---

## Repository Roles & Boundaries

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTENDS / UI                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ AMOS-Claws      │ Mailinhconect   │ AMOS-Invest                 │
│ (Operator)      │ (Product)       │ (Investor)                  │
│ TypeScript/React│ TypeScript/React│ TypeScript/React            │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                         API GATEWAY                              │
│                    AMOS-Consulting (FastAPI)                     │
├─────────────────────────────────────────────────────────────────┤
│                     SHARED LIBRARIES                             │
├─────────────────────────┬───────────────────────────────────────┤
│ AMOS-Code               │ AMOS-UNIVERSE                         │
│ (Python Core Library)   │ (Schemas & Contracts)                 │
├─────────────────────────┴───────────────────────────────────────┤
│                    MESSAGING BACKBONE                            │
│                        NATS Server                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository 1: AMOS-Code

### Role
**Shared Core Library** - Python foundation used by all backend services

### Type
Library (pip-installable)

### Exposed Packages
- `amos_core` - Core utilities and base classes
- `amos_brain` - Cognitive reasoning engine
- `amos_equations` - Mathematical equation framework
- `amos_nats` - NATS messaging client

### API Boundaries

**Exports TO:**
- AMOS-Consulting (via pip install)
- AMOS-Claws backend (via pip install)

**Imports FROM:**
- AMOS-UNIVERSE (schemas, contracts)

**Communication:**
- Publishes: `amos.brain.>`, `amos.system.>`
- Subscribes: `amos.knowledge.>`, `amos.equations.>`

### Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
nats-py = "^2.6"
temporalio = "^1.4"
amos-universe = { path = "../AMOS-UNIVERSE" }
```

---

## Repository 2: AMOS-UNIVERSE

### Role
**Shared Schemas & Contracts** - Type definitions and protocol specifications

### Type
Library (pip-installable + npm for TypeScript)

### Exposed Packages
- `amos_schemas` - Pydantic/dataclass models
- `amos_ontology` - Knowledge graph definitions
- `amos_contracts` - Interface contracts

### API Boundaries

**Exports TO:**
- AMOS-Code (schemas for brain operations)
- AMOS-Consulting (API request/response models)
- AMOS-Claws (TypeScript types)
- Mailinhconect (TypeScript types)
- AMOS-Invest (TypeScript types)

**Imports FROM:**
- None (this is the foundation layer)

### Key Contracts

```python
# amos_contracts/nats_topics.py
class NATSTopics:
    BRAIN_THINK = "amos.brain.think"
    BRAIN_REASON = "amos.brain.reason"
    EQUATION_EXECUTE = "amos.equations.execute"
    SYSTEM_HEARTBEAT = "amos.system.heartbeat"

# amos_schemas/brain.py
class BrainThinkRequest(BaseModel):
    query: str
    context: dict[str, Any]
    priority: int = 5

class BrainThinkResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[str]
```

---

## Repository 3: AMOS-Consulting

### Role
**Backend Hub & API Gateway** - Central orchestrator and workflow hub

### Type
Application (FastAPI + Temporal worker)

### Responsibilities
1. REST API for all frontends
2. Temporal workflow orchestration
3. NATS message routing
4. Cross-repo coordination

### API Endpoints

```yaml
# Core API
GET  /api/v1/health           → Health check
POST /api/v1/brain/think      → Cognitive reasoning
POST /api/v1/equations/exec   → Execute equation
GET  /api/v1/repos/status     → All repo statuses

# Workflow API
POST /api/v1/workflows/scan    → Start repo scan workflow
POST /api/v1/workflows/fix     → Start fix workflow
POST /api/v1/workflows/release → Start release workflow

# Admin API
GET  /admin/temporal/status    → Temporal cluster status
GET  /admin/nats/stats         → NATS connection stats
```

### NATS Integration

```python
# Publisher
await nats_client.publish(
    "amos.brain.think",
    {"query": "optimize revenue", "context": {...}}
)

# Subscriber
await nats_client.subscribe(
    "amos.workflow.completed",
    handle_workflow_completion
)
```

### Temporal Workflows Hosted
- `MultiRepoScanWorkflow` - Scan all 6 repos
- `MultiRepoFixWorkflow` - Apply fixes with approval gates
- `CrossRepoReleaseWorkflow` - Coordinate releases
- `KnowledgeSyncWorkflow` - Sync schemas to all repos

### Dependencies
- AMOS-Code (core library)
- AMOS-UNIVERSE (schemas)
- PostgreSQL (state storage)
- Redis (caching)
- NATS (messaging)
- Temporal (workflow engine)

---

## Repository 4: AMOS-Claws

### Role
**Operator Interface** - Agent control panel and system management UI

### Type
Application (Next.js + FastAPI backend)

### Structure
```
amos-claws/
├── frontend/          # Next.js React app
│   ├── app/
│   ├── components/
│   └── lib/api.ts     # API client
├── backend/           # FastAPI Python API
│   ├── api/
│   └── workers/       # Temporal workers
└── package.json
```

### API Boundaries

**Frontend → Backend:**
- REST calls to local FastAPI
- WebSocket for real-time updates

**Backend → AMOS-Consulting:**
- REST API calls
- NATS pub/sub for events

**Backend Workflows:**
- `AgentDeploymentWorkflow`
- `SystemMaintenanceWorkflow`

### Key Features
- Agent pool management
- Workflow monitoring dashboard
- System health visualization
- Real-time log streaming

---

## Repository 5: Mailinhconect

### Role
**Product Frontend** - Customer-facing product interface

### Type
Application (React + Vite)

### API Boundaries

**Frontend → AMOS-Consulting:**
- REST API for all backend operations
- WebSocket for real-time features

**No Local Backend** - Pure frontend application

### Key Features
- Customer dashboards
- Analytics visualization
- Report generation
- Notification center

---

## Repository 6: AMOS-Invest

### Role
**Investor Frontend** - Investor relations and reporting interface

### Type
Application (React + Vite)

### API Boundaries

**Frontend → AMOS-Consulting:**
- REST API for investor data
- WebSocket for live metrics

**No Local Backend** - Pure frontend application

### Key Features
- Investment portfolio view
- Performance metrics
- Financial reports
- Document vault

---

## Communication Patterns

### 1. Sync Lane (Request/Reply)

**Use Case:** Direct API calls requiring immediate response

```python
# Frontend → Consulting → Brain
response = await api.post("/brain/think", {
    "query": "Optimize Q3 revenue"
})

# Consulting internally uses NATS
result = await nats_client.request(
    "amos.brain.think",
    {"query": "..."},
    timeout=30
)
```

### 2. Async Lane (Pub/Sub)

**Use Case:** Events, notifications, background processing

```python
# Repo scan completed - notify all
await nats_client.publish(
    "amos.repo.scanned",
    {"repo": "AMOS-Code", "issues_found": 5}
)

# All subscribers receive:
# - Consulting (update dashboard)
# - Claws (notify operators)
# - Mailinhconect (update status)
```

### 3. Contract Lane (Shared Packages)

**Use Case:** Type-safe contracts across repos

```python
# In AMOS-UNIVERSE
class RepoScanResult(BaseModel):
    repo_name: str
    status: Literal["success", "failed"]
    issues: list[Issue]

# Used in all repos:
# - Consulting returns this from API
# - Claws displays this in UI
# - Temporal workflows pass this between steps
```

---

## Three Lanes Summary

| Lane | Pattern | Use For | Examples |
|------|---------|---------|----------|
| **Sync** | HTTP/gRPC + NATS req/reply | Direct queries | Brain think, Health check |
| **Async** | NATS pub/sub | Events & notifications | Repo changed, Workflow started |
| **Contract** | Shared packages | Type definitions | Schemas, API contracts |

---

## Deployment Architecture

### Kubernetes Namespaces

```yaml
# argocd/amos-applications.yaml
namespaces:
  - amos-consulting    # Backend hub
  - amos-claws        # Operator interface
  - mailinhconect     # Product frontend
  - amos-invest       # Investor frontend
  - amos-shared       # NATS, Temporal, Redis
```

### Service Mesh

```
Ingress (Traefik/Nginx)
    ↓
amos-consulting:8000 (REST API)
    ↓
NATS:4222 (messaging)
    ↓
Temporal:7233 (workflows)
```

---

## Workflow Examples

### Example 1: Cross-Repo Fix Workflow

```
1. Operator clicks "Fix All Repos" in Claws UI
   ↓
2. Claws backend calls Consulting API
   POST /workflows/fix
   ↓
3. Consulting starts Temporal workflow
   MultiRepoFixWorkflow
   ↓
4. Workflow scans all 6 repos (parallel)
   via RepoScanWorkflow children
   ↓
5. Issues aggregated, presented for approval
   ↓
6. Approved fixes applied via PRs
   ↓
7. Results published to NATS
   amos.workflow.completed
   ↓
8. All UIs update via WebSocket
```

### Example 2: Knowledge Sync

```
1. Schema updated in AMOS-UNIVERSE
   ↓
2. GitHub webhook → Consulting
   ↓
3. Consulting starts KnowledgeSyncWorkflow
   ↓
4. Workflow syncs to all repos in parallel
   - AMOS-Code
   - AMOS-Consulting
   - AMOS-Claws (TypeScript types)
   ↓
5. Renovate creates update PRs
   ↓
6. Tests run via CI/CD
   ↓
7. Argo CD deploys updates
```

---

## Setup Instructions

### 1. Infrastructure

```bash
# Deploy shared services
kubectl apply -f k8s/nats/
kubectl apply -f k8s/temporal/
kubectl apply -f k8s/redis/

# Deploy Argo CD
kubectl apply -f argocd/amos-applications.yaml
```

### 2. Repository Setup

```bash
# AMOS-Code (shared library)
cd AMOS-Code
pip install -e .
nats-server -c nats.conf &

# AMOS-Consulting (backend)
cd AMOS-Consulting
pip install -e ../AMOS-Code
pip install -e ../AMOS-UNIVERSE
python -m temporal_worker &
uvicorn main:app &

# AMOS-Claws (full stack)
cd AMOS-Claws
npm install
pip install -e ../AMOS-Code  # for backend
npm run dev
```

### 3. Renovate Setup

```bash
# Install Renovate GitHub App for all 6 repos
# Configuration in renovate.json at repo root
```

---

## Development Workflow

### Day-to-Day Development

1. **Feature in AMOS-Code**
   - Code → Test → PR → Merge
   - Automatically publishes to PyPI

2. **Downstream Update**
   - Renovate creates PR in AMOS-Consulting
   - CI runs integration tests
   - Argo CD deploys on merge

3. **Cross-Repo Coordination**
   - Use Temporal workflows for multi-repo operations
   - Monitor in Claws dashboard

---

## Monitoring & Observability

### Health Checks

| Component | Endpoint | Check |
|-----------|----------|-------|
| Consulting | GET /health | API + DB + NATS |
| NATS | nats://:4222 | Connection |
| Temporal | :7233 | gRPC health |
| Argo CD | /api/v1/health | GitOps status |

### Dashboards

- **Claws**: System-wide operator view
- **Consulting**: API metrics, workflow stats
- **Argo CD**: Deployment status

---

## Migration from Direct Imports

### Before (Problem)
```python
# AMOS-Consulting trying to import from AMOS-Code
from AMOS_Code.amos_brain import Brain  # ❌ Circular deps
```

### After (Solution)
```python
# AMOS-Consulting
from amos_core.brain import Brain  # ✅ pip install amos-code

# Or via NATS for async operations
await nats_client.request("amos.brain.think", {...})
```

---

## Summary

This architecture enables:
- ✅ **Independent repo development** - No circular dependencies
- ✅ **Coordinated changes** - Nx + Temporal for cross-repo ops
- ✅ **Real-time communication** - NATS pub/sub and req/reply
- ✅ **Always-on deployments** - Argo CD GitOps
- ✅ **Automated maintenance** - Renovate for dependencies

**Next Steps:**
1. Set up shared infrastructure (NATS, Temporal)
2. Configure Argo CD applications
3. Install Renovate GitHub App
4. Begin gradual migration to new patterns
