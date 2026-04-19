# Axiom One: Master Documentation Index
## The Civilization Substrate for Technical Systems

This document serves as the **central navigation** for all Axiom One specifications.

---

## Core Architecture Documents

| Document | Description | Status |
|----------|-------------|--------|
| `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` | 13-layer substrate mapping AMOS 28 phases | ✅ Complete |
| `AXIOM_ONE_ARCHITECTURE_SUMMARY.md` | Executive summary of the complete system | ✅ Complete |

---

## Layer Specifications

### Foundation Layers (1-5)
| Layer | Document | Status |
|-------|----------|--------|
| Layer 0: Physical Substrate | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 1 | ✅ Complete |
| Layer 1: Kernel & Primitives | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Part 2 | ✅ Complete |
| Layer 2: Universal Object Graph | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 4 | ⚠️ Partial |
| Layer 3: Time/Event Fabric | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 5 | ⚠️ Partial |
| Layer 4: Execution Fabric | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 6 | ⚠️ Partial |

### Data & Knowledge Layers (6-8)
| Layer | Document | Status |
|-------|----------|--------|
| Layer 5: Data Fabric | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 4.5 | ⚠️ Partial |
| Layer 6: Observe Fabric | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 6.3 | ⚠️ Partial |
| Layer 7: Security Fabric | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 6.4 | ⚠️ Partial |
| Layer 8: Knowledge Fabric | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 6.5 | ⚠️ Partial |

### Operational Layers (9-13)
| Layer | Document | Status |
|-------|----------|--------|
| Layer 9: Workflow Fabric | See `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` Section 6.6 | ⚠️ Partial |
| **Layer 10: Agent Fabric** | `AXIOM_ONE_AGENT_FABRIC.md` | ✅ **Complete** |
| Layer 11: Economic Fabric | Not yet created | 📋 Pending |
| Layer 12: Simulation System | `AXIOM_ONE_SIMULATION_SYSTEM.md` | ✅ **Complete** |
| **Section 10: Repo Autopsy** | `AXIOM_ONE_REPO_AUTOPSY.md` | ✅ **Complete** |
| Layer 13: Civilization Interface | Not yet created | 📋 Pending |

---

## Implementation Status Summary

### ✅ Complete Specifications
1. **AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md**
   - 13-layer architecture mapping
   - AMOS 28-phase coverage analysis
   - Primitive set (96 primitives across 8 categories)

2. **AXIOM_ONE_AGENT_FABRIC.md**
   - 18 agent classes defined
   - Agent anatomy (identity, permissions, budget)
   - 10-phase execution model
   - Receipt system (non-negotiable)
   - Human control interface

3. **AXIOM_ONE_SIMULATION_SYSTEM.md**
   - 12 simulation types
   - 6-phase simulation engine
   - Impact analysis format
   - CI/CD integration (SimulationGate)
   - Report format with examples

4. **AXIOM_ONE_REPO_AUTOPSY.md**
   - 12 failure categories
   - 8-phase autopsy workflow
   - Pattern database structure
   - Autopsy engine implementation
   - Human interface for oversight

### ⚠️ Partial / Reference Only
- Object Ontology (Sections 3.1-3.8 in Architecture doc)
- Protocol definitions (Sections 6.1-6.8)
- Execution contracts (Section 6.2)
- Data fabric primitives (Section 2.4)
- Knowledge primitives (Section 2.6)

### 📋 Pending
- Economic Fabric (Layer 11) - cost attribution, business linkage
- Civilization Interface (Layer 13) - human interfaces
- Complete Object Ontology document
- Complete Protocol specifications document
- Formal Execution Contract JSON Schema

---

## Quick Reference: Key Concepts

### The 8 Primitive Categories
| Category | Primitives | Purpose |
|----------|------------|---------|
| Source | 12 primitives | Code manipulation |
| Repository | 14 primitives | Version control |
| Execution | 7 primitives | Runtime control |
| Data | 16 primitives | State management |
| Runtime | 12 primitives | Infrastructure |
| Knowledge | 16 primitives | Information layer |
| Governance | 10 primitives | Policy/compliance |
| Agent | 9 primitives | AI labor control |

### The 13 Layers
| Layer | Name | AMOS Phase Coverage |
|-------|------|---------------------|
| 0 | Physical Substrate | 01-05 |
| 1 | Kernel & Primitives | 06 |
| 2 | Universal Object Graph | Phase 27 (Repo Graph) |
| 3 | Time/Event Fabric | Phase 19 (Event Mesh) |
| 4 | Execution Fabric | Phases 07-08, 14 |
| 5 | Data Fabric | Phase 22 (Vector DB) |
| 6 | Observe Fabric | Phases 20-21, 26 |
| 7 | Security Fabric | Phase 09 |
| 8 | Knowledge Fabric | Phases 10-11, 16 |
| 9 | Workflow Fabric | Phase 23 (Temporal) |
| 10 | Agent Fabric | **NEW** - See agent fabric doc |
| 11 | Economic Fabric | **NEW** - Pending |
| 12 | Simulation System | **NEW** - See simulation doc |
| 13 | Civilization Interface | **NEW** - Pending |

---

## Next Steps (Recommended Priority)

### Phase 1: Foundation (Weeks 1-4)
1. Implement Kernel primitive interfaces
2. Create Object Graph persistence layer
3. Build Event fabric (Kafka integration)

### Phase 2: Core Systems (Weeks 5-8)
4. Implement Agent Fabric kernel
5. Build basic agent classes (repo-debugger, patch-engineer)
6. Create simulation engine core

### Phase 3: Integration (Weeks 9-12)
7. Integrate Repo Autopsy with Agent Fabric
8. Implement simulation-based CI gates
9. Build economic tracking layer

### Phase 4: Polish (Weeks 13-16)
10. Create human interfaces
11. Performance optimization
12. Documentation and examples

---

## File Locations

All Axiom One specifications are in the repository root:
```
AMOS-code/
├── AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md    # Core architecture
├── AXIOM_ONE_ARCHITECTURE_SUMMARY.md         # Executive summary  
├── AXIOM_ONE_AGENT_FABRIC.md                 # Layer 10
├── AXIOM_ONE_SIMULATION_SYSTEM.md            # Layer 12
├── AXIOM_ONE_REPO_AUTOPSY.md                 # Section 10
└── AXIOM_ONE_MASTER_INDEX.md                 # This file
```

---

## Usage Guide

### For Architects
Start with `AXIOM_ONE_ARCHITECTURE_SUMMARY.md` for the big picture, then dive into `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` for the 13-layer mapping.

### For Developers
Read `AXIOM_ONE_AGENT_FABRIC.md` to understand how AI agents work in the system, and `AXIOM_ONE_REPO_AUTOPSY.md` for the debugging system.

### For Operations
Focus on `AXIOM_ONE_SIMULATION_SYSTEM.md` for pre-deployment impact analysis.

### For Product Managers
Review the Object Ontology sections in `AXIOM_ONE_CIVILIZATION_ARCHITECTURE.md` for the data model, and Agent classes in `AXIOM_ONE_AGENT_FABRIC.md`.

---

## Document Version
- **Version:** 1.0.0
- **Date:** 2025-01
- **Based on:** AMOS 28-Phase System
- **Status:** Architecture specification complete, implementation pending

---

This is the **operating manual** for the Axiom One civilization substrate.
