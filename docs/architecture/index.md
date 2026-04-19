# Architecture

Deep dive into AMOS architecture, components, and design principles.

## Overview

AMOS follows a layered architecture designed for modularity, scalability, and maintainability.

```mermaid
graph TB
    subgraph "Tier 7: Interface"
        UI[Dashboard UI]
        API[REST API]
        WS[WebSocket]
    end

    subgraph "Tier 6: Security"
        Auth[Authentication]
        RBAC[Authorization]
        Rate[Rate Limiting]
    end

    subgraph "Tier 5: Cognitive Engine"
        Orchestrator[Hybrid Orchestrator]
        Agents[Agent Pool]
        Laws[Law Engine]
    end

    subgraph "Tier 4: Memory"
        WM[Working Memory]
        STM[Short-term Memory]
        EM[Episodic Memory]
        SM[Semantic Memory]
        PM[Procedural Memory]
        VM[Vector Memory]
    end

    subgraph "Tier 3: Tools"
        MCP[MCP Bridge]
        FS[Filesystem]
        Git[Git]
        Web[Web Search]
        DB[Database]
        Code[Code Execution]
    end

    subgraph "Tier 2: Infrastructure"
        Config[Configuration]
        Obs[Observability]
        CI[CI/CD]
    end

    subgraph "Tier 1: Substrate"
        LLM[LLM Providers]
        Docker[Docker]
        K8s[Kubernetes]
    end

    UI --> API
    API --> Auth
    Auth --> Orchestrator
    Orchestrator --> Agents
    Agents --> Laws
    Agents --> WM
    WM --> STM --> EM --> SM --> VM
    Agents --> MCP
    MCP --> FS & Git & Web & DB & Code
    Orchestrator --> Config & Obs
```

## Design Principles

### 1. Hybrid Neural-Symbolic

AMOS combines neural network pattern recognition with symbolic logical reasoning:

- **Neural**: Pattern matching, semantic understanding, generation
- **Symbolic**: Logical deduction, rule enforcement, structured reasoning
- **Hybrid**: Best of both worlds for complex tasks

### 2. Safety First

Global Laws L1-L6 are enforced on all operations:

- Every action is validated
- Violations are blocked with explanations
- Human oversight for critical decisions

### 3. Tiered Memory

Five memory tiers for optimal information retention:

| Tier | Purpose | Persistence |
|------|---------|-------------|
| Working | Current context | Session |
| Short-term | Recent interactions | Minutes-Hours |
| Episodic | Past experiences | Days-Weeks |
| Semantic | Facts & concepts | Permanent |
| Procedural | Skills & procedures | Permanent |

### 4. Tool Extensibility

MCP (Model Context Protocol) enables tool integration:

- Standardized tool interface
- Easy to add new tools
- Secure execution sandbox

## Architecture Sections

### [Overview](overview.md)
High-level architectural concepts and design decisions.

### [Components](components.md)
Detailed documentation of each AMOS component.

### [Data Flow](data-flow.md)
How data flows through the system during different operations.

---

## Scalability

AMOS is designed to scale:

- **Horizontal**: Multiple AMOS instances behind a load balancer
- **Vertical**: Resource scaling for larger models
- **Agent Pool**: Dynamic agent creation and destruction
- **Memory**: Distributed memory backends

## Security Architecture

Security is built into every layer:

```mermaid
graph LR
    User -->|JWT| Auth[Authentication]
    Auth -->|Token| RBAC[Authorization]
    RBAC -->|Permissions| API[API Gateway]
    API -->|Rate Limit| Core[Core Services]
    Core -->|Validation| Laws[Law Engine]
    Laws -->|Audit| Logger[Audit Logger]
```

---

!!! info "Contributing"
    Interested in contributing to AMOS architecture? See the [Development Guide](../development/index.md).
