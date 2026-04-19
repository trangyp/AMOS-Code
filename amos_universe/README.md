# AMOS Universe

Canonical knowledge, ontology, and contract layer for the AMOS ecosystem.

## Overview

This is the **AMOS-UNIVERSE** repository - the single source of truth for:
- API contracts (Pydantic models)
- Event schemas
- Ontology definitions
- ADRs (Architecture Decision Records)
- Generated SDKs

## Design Principle

**AMOS-UNIVERSE owns the "what", implementation repos own the "how".**

- Zero runtime dependencies on other AMOS repos
- Contracts can be imported by any repo
- Published as `amos-universe` package

## Installation

```bash
pip install -e .
```

## Usage

```python
from amos_universe.contracts.pydantic import ChatRequest, ChatResponse
from amos_universe.contracts.pydantic import RepoScanRequest, RepoScanResult
from amos_universe.contracts.pydantic import EventType, BaseEvent

# Use in your API
request = ChatRequest(message="Hello", context=...)
```

## Directory Structure

```
contracts/
  pydantic/       # Pydantic models for API contracts
    __init__.py
    base.py       # BaseAMOSModel, TimestampsMixin
    chat.py       # ChatRequest, ChatResponse, etc.
    repo.py       # RepoScanRequest, RepoScanResult, etc.
    models.py     # ModelInfo, ModelRequest, etc.
    session.py    # User, Workspace, SessionContext
    brain.py      # BrainRunRequest, BrainRunResponse
    workflow.py   # WorkflowRunRequest, WorkflowRunResponse
    errors.py     # ApiError, ErrorCode, etc.
    events.py     # EventType, BaseEvent, typed events
ontology/         # Ontology definitions
specs/            # OpenAPI specs, JSON schemas
adrs/             # Architecture Decision Records
generated/        # Auto-generated SDKs
docs/             # Documentation
tests/            # Tests
```

## Package

Published as `amos-universe` on PyPI.

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["contracts*", "ontology*", "specs*", "adrs*"]
```

## 6-Repo Integration

| Repo | Package | Role |
|------|---------|------|
| AMOS-UNIVERSE | `amos-universe` | Contracts, schemas, ontology |
| AMOS-Code | `amos-brain` | Core brain library |
| AMOS-Consulting | `amos-platform` | API gateway (this repo) |
| AMOS-Claws | `amos-claws` | Operator frontend |
| Mailinhconect | `mailinh-web` | Product frontend |
| AMOS-Invest | `amos-invest` | Investor frontend |

## Dependencies

- pydantic>=2.0.0
- pydantic-settings>=2.0.0
- typing-extensions>=4.0.0

Zero runtime dependencies on other AMOS repos.
