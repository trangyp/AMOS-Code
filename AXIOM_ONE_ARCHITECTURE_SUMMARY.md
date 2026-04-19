# Axiom One: Technical Architecture Summary

## Overview

Axiom One is defined as a **typed, event-sourced, graph-native operating environment** for technical civilization. This document provides the complete technical specification as executable state machines.

---

## The Six Core Engines

| Engine | Responsibility | State Machine |
|--------|---------------|---------------|
| **Kernel** | Object identity, permissions, transactional state | Object lifecycle (DRAFT → ACTIVE → DEPRECATED → ARCHIVED) |
| **Graph** | Typed relations, impact computation, ownership | Edge creation/invalidation, traversal, blast radius |
| **Execution** | Unified action runtime (local, remote, container) | Execution lifecycle (PENDING → VALIDATING → RUNNING → COMPLETED/FAILED) |
| **Observation** | Logs, metrics, traces, evidence | Telemetry ingestion, query by object/time |
| **Knowledge** | Docs, tickets, ADRs, semantic memory | Knowledge creation, semantic search, explanation |
| **Agent** | Bounded autonomy, tool access, receipts | Agent run lifecycle, step execution, policy checks |

---

## Core State Machines

### 1. Object Lifecycle (Kernel)
```
DRAFT → ACTIVATE → ACTIVE → DEPRECATE → DEPRECATED → ARCHIVE → ARCHIVED
   ↓        ↓         ↓          ↓            ↓
DELETE   DELETE    DELETE     RESTORE      RESTORE
   ↓        ↓         ↓          ↓            ↓
DELETED  DELETED  DELETED    ACTIVE       DEPRECATED
```

### 2. Execution Lifecycle (Execution Engine)
```
PENDING → VALIDATING → PREPARING → RUNNING → COMPLETED
                                     ↓
                                SUSPENDED (approval)
                                     ↓
                                CANCELLED/FAILED
                                     ↓
                                ROLLING_BACK → ROLLED_BACK
```

### 3. Agent Lifecycle (Agent Engine)
```
PLANNED → APPROVED (if required) → RUNNING → COMPLETED
                                      ↓
                                 PARTIAL_SUCCESS
                                      ↓
                                 FAILED (rollback available)
```

---

## Universal Object Schema

All objects share:
```python
id: str              # ULID: ax_<timestamp>
type: str            # repo|service|function|incident|agent|...
name: str
workspace_id: str
owner_id: str
created_at: datetime
updated_at: datetime
version: int
status: KernelState
criticality: str     # low|medium|high|critical
security_class: str  # public|internal|sensitive|restricted
relations: list[str] # Edge IDs
metadata: dict
```

---

## Graph Edge Types

| Edge Type | Direction | Semantics |
|-----------|-----------|-----------|
| CONTAINS | parent → child | Composition |
| DEPENDS_ON | dependent → dependency | Runtime dependency |
| CALLS | caller → callee | Function call graph |
| DEPLOYS_FROM | service → repo | Deployment source |
| IMPACTS | incident → object | Incident effect |
| OWNS | team → object | Responsibility |
| GOVERNS | policy → object | Policy coverage |
| USED_TOOL | agent → tool | Agent action |

---

## Command System

The universal command grammar:

```
/inspect <type> <id>
/explain <type> <id>
/diff <env_a> <env_b>
/test <repo> [--failed-only]
/patch <repo> [--safe-fixes]
/simulate deploy <service> --to <env>
/trace <request_id>
/show blast-radius <service>
```

---

## Event Sourcing

Every action produces:
```python
AxiomEvent:
    event_id: str
    timestamp: datetime
    actor_type: str          # human|agent|system
    actor_id: str
    action: str              # create|update|delete|deploy|rollback
    target_object_ids: list[str]
    result: str              # success|failure|partial
    diff_ref: str | None
    receipt_ref: str | None
    rollback_ref: str | None
```

This enables: replay, causality, forensics, compliance, simulation

---

## Workspace Surfaces

| Surface | Purpose | Key Views |
|---------|---------|-----------|
| **Studio** | Build | Editor, terminal, test runner, AI operator |
| **Navigator** | Explore | Dependency graph, ownership graph, blast radius |
| **Forge** | Validate | CI/CD matrix, failed tests, coverage heatmap |
| **Orbit** | Release | Deploy pipeline, rollout state, rollback controls |
| **Pulse** | Observe | Logs, metrics, traces, live incidents |
| **Sentinel** | Secure | Vulnerabilities, policy violations, audit |
| **Ledger** | Economic | Service cost, ROI, debt priority |
| **Flow** | Orchestrate | Workflows, approvals, agent actions |

---

## Repo Autopsy Pipeline

Phase A: Identity (language, packages, build systems)
Phase B: Static Analysis (packaging, imports, paths, tests, CI, docs)
Phase C: Dynamic Validation (install, build, test, smoke tests)
Phase D: Fault Tree (root cause classification)
Phase E: Repair (safe autofixes, patches)
Phase F: Verify (re-run validation)
Phase G: Deliver (report, diff, branch, PR)

---

## Storage Model

| Store | Technology | Purpose |
|-------|------------|---------|
| Graph | Neo4j/ArangoDB | Typed relations |
| Event Log | Kafka | Append-only events |
| Document | PostgreSQL | Docs, tickets, ADRs |
| Artifact | S3/GCS | Builds, logs, reports |
| Time-Series | TimescaleDB | Metrics |
| Trace | Jaeger | Request traces |
| Search | Elasticsearch | Code/docs full-text |
| Vector | pgvector | Semantic search |
| Secret | Vault | Credentials |
| Snapshot | Volume backups | Replayable state |

---

## Data Contracts

```python
CONTRACTS = {
    "studio_kernel": ["object_lookup", "permission_check", "apply_diff"],
    "forge_execution": ["run_build", "run_test_matrix", "collect_artifacts"],
    "orbit_execution": ["create_release_plan", "deploy", "rollback"],
    "pulse_observation": ["subscribe_logs", "correlate_alerts"],
    "sentinel_kernel": ["evaluate_policy", "record_exceptions"],
    "agent_all": ["read_graph", "request_execution", "emit_receipt"],
}
```

---

## Build Order (Layered)

### Layer 1: Repo Operating Core
- Editor, terminal, git/PR
- Repo Autopsy
- Path/import/packaging repair
- Test/build runner
- Fix branch generation

### Layer 2: Runtime Control
- Environment management
- Release control
- Logs/traces/metrics
- Rollback
- Preview environments

### Layer 3: Graph & Governance
- Ownership tracking
- Dependencies
- Blast radius
- Policy engine
- Audit receipts

### Layer 4: Data & Cost
- Schema/migration explorer
- DB operations
- Cost graph
- Customer impact graph

### Layer 5: Bounded Autonomy
- Specialized agents
- Simulation
- Auto-remediation
- Self-healing workflows

---

## Connection to AMOS

This Axiom One specification subsumes and extends the existing AMOS architecture:

| Axiom One Engine | AMOS Equivalent | Extension |
|-----------------|-----------------|-----------|
| Kernel | AMOS object models + ACL | Event sourcing, universal schema |
| Graph | AMOS relation system | Blast radius, typed edges |
| Execution | AMOS production runtime | Sandbox targets, rollback |
| Observation | AMOS metrics/health | Full telemetry, traces |
| Knowledge | AMOS docs/tickets | Semantic search, explanations |
| Agent | AMOS agent bridge | Bounded autonomy, receipts |

---

## System Invariants (Must Never Be Violated)

1. **OBJECT_IDENTITY**: Every object has exactly one canonical identifier
2. **EVENT_IMMUTABILITY**: Events are append-only and verifiable
3. **RELATION_TYPED**: All edges have explicit, schema-validated types
4. **ACTION_RECEIPT**: Every action produces a verifiable receipt
5. **ROLLBACK_ELIGIBILITY**: Every state change has calculable reversibility
6. **POLICY_PRECEDENCE**: Policy checks occur before action dispatch
7. **FULL_TRACEABILITY**: Every effect must be attributable to a cause
8. **COMPLETE_AUDIT**: All operations are recorded in the event log

---

## Files Created

1. `AXIOM_ONE_CORE_ENGINES.md` - Core engine specifications
2. `AXIOM_ONE_PROTOCOLS.py` - Protocol definitions for all engines
3. `AXIOM_ONE_STATE_MACHINE.py` - Executable state machine implementation
4. `AXIOM_ONE_ARCHITECTURE_SUMMARY.md` - This document

---

## Next Steps

1. **Product PRD**: Screen-by-screen UX specification
2. **System Architecture**: Database schemas, API contracts
3. **Implementation**: Begin Layer 1 (Repo Operating Core)

The architecture is now completely defined at the technical state machine level.
