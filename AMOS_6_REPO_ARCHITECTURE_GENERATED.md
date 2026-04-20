# AMOS 6-Repository Architecture

## Repository Overview

| Repository | Role | Package | Endpoint | Layer |
|------------|------|---------|----------|-------|
| **AMOS-Code** | Core brain library | `amos-brain` | N/A | Layer 01 (Brain) |
| **AMOS-Consulting** | Backend API hub | `amos-platform` | api.amos.io | Layer 00 (Root) |
| **AMOS-Claws** | Operator frontend | `amos-claws` | claws.amos.io | Layer 09 (Social) |
| **Mailinhconect** | Product frontend | `mailinh-web` | app.amos.io | Layer 14 (Interfaces) |
| **AMOS-Invest** | Investor frontend | `amos-invest` | invest.amos.io | Layer 14 (Interfaces) |
| **AMOS-UNIVERSE** | Canonical knowledge layer | `amos-universe` | universe.amos.io | Layer 11 (Canon) |

## Dependency Graph

```
AMOS-UNIVERSE (Canonical Layer)
       │
       ├──► AMOS-Code (Core Library)
       │
       ├──► AMOS-Consulting (API Hub) ◄──┬─── AMOS-Claws
       │                                   ├─── Mailinhconect
       │                                   └─── AMOS-Invest
       │
       └──► All Frontends (via generated SDKs)
```

## Event Topics

- `claws.session.started`: AMOS-Claws → AMOS-Consulting
- `claws.session.ended`: AMOS-Claws → AMOS-Consulting
- `claws.agent.requested`: AMOS-Claws → AMOS-Consulting
- `claws.agent.completed`: AMOS-Consulting → AMOS-Claws, AMOS-Invest
- `claws.tool.invoked`: AMOS-Claws → AMOS-Consulting
- `mailinh.lead.created`: Mailinhconect → AMOS-Consulting, AMOS-Invest
- `mailinh.contact.submitted`: Mailinhconect → AMOS-Consulting
- `mailinh.user.registered`: Mailinhconect → AMOS-Consulting
- `invest.report.requested`: AMOS-Invest → AMOS-Consulting
- `invest.signal.generated`: AMOS-Consulting → AMOS-Invest
- `invest.analytics.viewed`: AMOS-Invest → AMOS-Consulting
- `repo.scan.completed`: AMOS-Consulting → AMOS-Claws, AMOS-Invest
- `repo.scan.failed`: AMOS-Consulting → AMOS-Claws
- `repo.fix.completed`: AMOS-Consulting → AMOS-Claws
- `repo.fix.failed`: AMOS-Consulting → AMOS-Claws
- `model.run.completed`: AMOS-Consulting → AMOS-Claws, AMOS-Invest
- `model.run.failed`: AMOS-Consulting → AMOS-Claws
- `model.loaded`: AMOS-Consulting → AMOS-Claws
- `model.unloaded`: AMOS-Consulting → AMOS-Claws
- `workflow.started`: AMOS-Consulting → 
- `workflow.completed`: AMOS-Consulting → AMOS-Claws, Mailinhconect, AMOS-Invest
- `workflow.failed`: AMOS-Consulting → AMOS-Claws
- `workflow.step.completed`: AMOS-Consulting → 
- `universe.schema.updated`: AMOS-UNIVERSE → AMOS-Code, AMOS-Consulting, AMOS-Claws, Mailinhconect, AMOS-Invest
- `universe.contract.published`: AMOS-UNIVERSE → AMOS-Consulting, AMOS-Claws, Mailinhconect, AMOS-Invest
- `universe.ontology.changed`: AMOS-UNIVERSE → AMOS-Consulting, AMOS-Claws, Mailinhconect, AMOS-Invest
- `consulting.workflow.completed`: AMOS-Consulting → 
- `consulting.task.created`: AMOS-Consulting → AMOS-Claws
- `consulting.task.updated`: AMOS-Consulting → AMOS-Claws
- `system.alert`: AMOS-Consulting → AMOS-Claws, Mailinhconect, AMOS-Invest
- `system.health.changed`: AMOS-Consulting → AMOS-Claws, Mailinhconect, AMOS-Invest
- `system.maintenance.scheduled`: AMOS-Consulting → AMOS-Claws, Mailinhconect, AMOS-Invest

## API Endpoints (AMOS-Consulting)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/health` | GET | Health check |
| `/v1/chat` | POST | Chat completion |
| `/v1/brain/run` | POST | Execute brain cycle |
| `/v1/repo/scan` | POST | Scan repository |
| `/v1/repo/fix` | POST | Apply fixes |
| `/v1/models` | GET | List LLM models |
| `/v1/models/run` | POST | Run model inference |
| `/v1/workflow/run` | POST | Execute workflow |
| `/v1/universe/schemas` | GET | List schemas (NEW) |

## Subdomains

| Subdomain | Service | Repository |
|-----------|---------|------------|
| `api.amos.io` | API Gateway | AMOS-Consulting |
| `claws.amos.io` | Operator UI | AMOS-Claws |
| `app.amos.io` | Product UI | Mailinhconect |
| `invest.amos.io` | Investor UI | AMOS-Invest |
| `universe.amos.io` | Schema Registry | AMOS-UNIVERSE |