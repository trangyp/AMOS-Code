# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) documenting significant architectural decisions in the AMOS project.

## What are ADRs?

ADRs capture:
- **Context**: Why a decision was needed
- **Decision**: What was decided
- **Consequences**: Trade-offs and outcomes
- **Alternatives**: Options considered and rejected

## ADR Index

### Process & Standards
- [ADR 0001](0001-record-architecture-decisions.md) - Record Architecture Decisions

### Core Architecture
- [ADR 0002](0002-python-312-modernization.md) - Python 3.12+ Modernization
- [ADR 0003](0003-new-engines-architecture.md) - New Engine Architecture (4 Engines)
- [ADR 0008](0008-field-dynamics-computation.md) - Field Dynamics Computation Engine

### Infrastructure
- [ADR 0004](0004-kubernetes-deployment.md) - Kubernetes Deployment Strategy
- [ADR 0007](0007-deployment-automation.md) - Multi-Method Deployment Automation

### Testing & Quality
- [ADR 0005](0005-testing-strategy.md) - Three-Tier Testing Strategy

### Observability
- [ADR 0006](0006-observability-stack.md) - Observability Stack (Prometheus + Health)

## Creating New ADRs

To create a new ADR:

1. Use the next sequential number
2. Follow the template below
3. Submit for review
4. Update this index

## ADR Template

```markdown
# ADR XXXX: Title

## Status
- Proposed
- Accepted
- Deprecated
- Superseded by [ADR YYYY](YYYY-title.md)

## Context
What is the issue that we're seeing that is motivating this decision or change?

## Decision
What is the change that we're proposing or have agreed to implement?

## Consequences
What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.

## Alternatives Considered
What other options were considered and why they were rejected.

## Implementation
How the decision was implemented (files, phases, etc.)

## References
Links to relevant documents, discussions, etc.
```

## Contributing

When making significant architectural decisions:
1. Create an ADR before or during implementation
2. Share with the team for feedback
3. Update when decisions evolve
4. Mark superseded ADRs as deprecated
