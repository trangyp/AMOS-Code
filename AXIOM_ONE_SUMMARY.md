# AXIOM ONE: Build Specification Summary

## Documents Created

| Document | Description |
|----------|-------------|
| `AXIOM_ONE_BUILD_SPECIFICATION.md` | Complete 50+ page build specification |
| `AXIOM_ONE_MVP_SCHEMA.sql` | PostgreSQL database schema |
| `AXIOM_ONE_MVP_BACKEND.py` | FastAPI backend implementation |

## MVP Timeline

- **Phase 1** (Months 1-2): Foundation - DB, API, Git integration
- **Phase 2** (Months 3-4): Repo Autopsy - Static analysis, autofix
- **Phase 3** (Months 5-6): AI Integration - Agent runtime, bounded AI
- **Phase 4** (Months 7-8): Runtime - Deploy, observe, govern

## Core Features Implemented

### 1. Repo Autopsy (The Wedge)
- Static analysis pipeline
- Autofix generation
- PR creation
- Tables: `repo_autopsy_jobs`, `repo_autopsy_issues`

### 2. Canonical Object Graph
- 30+ object types
- Unified graph with Neo4j
- Tables: `repositories`, `symbols`, `services`, `deployments`, `incidents`, `agents`

### 3. Event-Sourced Core
- Complete audit trail
- Tables: `events` with correlation/causation

### 4. Bounded AI Labor
- Agent runtime with receipts
- Tables: `agents`, `agent_executions`

### 5. Universal Commands
- `/inspect`, `/run`, `/patch`, `/explain`
- API: `POST /api/v1/commands/execute`

## API Endpoints

| Category | Endpoints |
|----------|-----------|
| Identity | tenants, people, teams |
| Code | repositories, symbols, tests |
| Services | services, endpoints |
| Runtime | environments, deployments |
| Operations | incidents, alerts |
| AI | agents, agent executions |
| Repo Autopsy | jobs, issues, fixes |
| Commands | universal command interface |

## Getting Started

```bash
# Database
psql axiom_one < AXIOM_ONE_MVP_SCHEMA.sql

# Backend
pip install fastapi uvicorn asyncpg redis pydantic
python AXIOM_ONE_MVP_BACKEND.py

# Test
curl http://localhost:8000/health
```

## Architecture

```
Studio (IDE) → API Gateway → Services → PostgreSQL/Neo4j/Redis
```

## Key Differentiators

1. **Repo Autopsy** - Fixes repos automatically
2. **Object Graph** - Everything linked and typed
3. **Event-Sourced** - Complete audit trail
4. **Bounded AI** - Agents with permissions and budgets
5. **Universal Commands** - Operator-grade interface

---

**Status**: MVP specification complete. Ready for Phase 1 implementation.
