# Axiom One: Core Engines Specification

## 1. KERNEL ENGINE

```python
class KernelState(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DELETED = "deleted"

class AxiomObject:
    id: str                    # ULID format
    type: str                  # repo|service|function|incident|agent
    name: str
    workspace_id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    version: int
    status: KernelState
    criticality: str           # low|medium|high|critical
    security_class: str        # public|internal|sensitive|restricted
    cost_center: str | None
    relations: list[str]       # Edge IDs
    metadata: dict
    tags: list[str]
    audit_ref: str | None
```

## 2. GRAPH ENGINE

```python
class EdgeType(Enum):
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    CALLS = "calls"
    EMITS_TO = "emits_to"
    DEPLOYS_FROM = "deploys_from"
    IMPACTS = "impacts"
    OWNS = "owns"
    GOVERNS = "governs"
    USED_TOOL = "used_tool"

class Edge:
    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    confidence: float = 1.0
    is_active: bool = True
```

## 3. EXECUTION ENGINE

```python
class ExecutionState(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"

class ExecutionRequest:
    execution_id: str
    kind: str                  # shell|python|build|test|deploy|agent
    target: str              # local|remote|cluster|sandbox
    environment: str         # dev|staging|prod
    permissions: list[str]
    timeout_seconds: int
    command_or_payload: str
    rollback_eligible: bool
```

## 4. EVENT MODEL

```python
class AxiomEvent:
    event_id: str              # ULID
    timestamp: datetime
    actor_type: str          # human|agent|system
    actor_id: str
    action: str              # create|update|delete|deploy|rollback
    target_object_ids: list[str]
    result: str              # success|failure|partial
    diff_ref: str | None
    receipt_ref: str | None
```

## 5. AGENT PROTOCOL

```python
class AgentRun:
    run_id: str
    agent_role: str          # repo-debugger|patch-generator|test-writer
    goal: str
    scope: AgentScope
    tools_allowed: list[str]
    max_steps: int
    budget: float

class AgentReceipt:
    run_id: str
    steps: list[AgentStep]
    policies_checked: list[str]
    final_result: str        # success|partial_success|failure
    rollback_available: bool
```

## 6. COMMAND SYSTEM

```
/inspect repo <name>
/explain service <name>
/diff env <a> <b>
/test repo <name> --failed-only
/patch repo <name> --safe-fixes
/simulate deploy service <name> --to prod
/trace request <id>
/show blast-radius service <name>
```

## 7. REPO AUTOPSY PIPELINE

Phase A: Identity - Detect language, packages, build systems
Phase B: Static Analysis - Packaging, imports, paths, tests, CI, docs
Phase C: Dynamic Validation - Install, build, test, smoke tests
Phase D: Fault Tree - Root cause classification
Phase E: Repair - Safe autofixes
Phase F: Verify - Re-run validation
Phase G: Deliver - Report, diff, PR

## 8. BUILD ORDER

Layer 1: Repo Operating Core (Editor, Terminal, Git, Autopsy, Tests)
Layer 2: Runtime Control (Environments, Releases, Logs, Rollback)
Layer 3: Graph & Governance (Ownership, Dependencies, Policies)
Layer 4: Data & Cost (Schema, DB, Cost graph)
Layer 5: Bounded Autonomy (Agents, Simulation, Self-healing)

## 9. STORAGE TIERS

- Graph: Neo4j - typed relations
- Event Log: Kafka - append-only
- Document: PostgreSQL - docs, tickets
- Artifact: S3 - builds, logs
- Time-Series: TimescaleDB - metrics
- Vector: pgvector - semantic search
- Secret: Vault - credentials

## 10. WORKSPACE SURFACES

Studio: Build surface (editor, terminal, test runner)
Navigator: Graph explorer (dependencies, blast radius)
Forge: Validation surface (CI/CD, test matrix)
Orbit: Release surface (deploy pipeline, rollback)
Pulse: Observe surface (logs, metrics, traces)
Sentinel: Security surface (vulnerabilities, policies)
Ledger: Economic surface (costs, ROI)
Flow: Workflow surface (triggers, approvals)

## 11. CORE INVARIANTS

- Every object has exactly one canonical identifier
- Events are append-only and verifiable
- All edges have explicit types
- Every action produces a verifiable receipt
- Policy checks occur before action dispatch
- Every effect must be attributable to a cause
- All operations are recorded in the event log

## 12. SIMULATION OUTPUT

- Confidence score
- Estimated breakage
- Rollback recommendation
- Required approvals
- Cost impact
- Tenant impact
- Security impact

## 13. SELF-HEALING ACTIONS

- Repair imports
- Fix packaging
- Regenerate docs
- Rollback deploy
- Restart workers
- Rotate secrets
- Quarantine nodes
- Disable feature flags
- Rerun failed tests

## 14. ECONOMIC TRACKING

- Infrastructure cost
- Model/AI cost
- Support burden
- Incident cost
- Revenue attributed
- Cost per customer
- ROI by project
- Debt priority by financial impact

---
Status: Technical Specification v1.0.0 Complete
Classification: Core System Blueprint
Next: Implementation phase
