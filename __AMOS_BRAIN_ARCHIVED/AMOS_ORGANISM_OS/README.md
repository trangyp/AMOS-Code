# AMOS 7-System Organism

A deterministic, biologically-inspired AI operating system implementing the Unified Biological Intelligence (UBI) framework.

## Overview

The AMOS 7-System Organism is a cognitive architecture composed of 14 interconnected subsystems organized in a primary operational loop:

```
BRAIN -> SENSES -> SKELETON -> WORLD_MODEL -> QUANTUM_LAYER -> MUSCLE -> METABOLISM -> BRAIN
```

## Subsystem Architecture

| Code | Name | Role |
|------|------|------|
| 00_ROOT | Root | Identity, goals, global config, bootstrap specs |
| 01_BRAIN | Brain | Reasoning, planning, decomposition, memory, routing |
| 02_SENSES | Senses | Filesystem, environment, system load, context, emotion inputs |
| 03_IMMUNE | Immune | Safety, legal, compliance, anomaly detection |
| 04_BLOOD | Blood | Budgeting, cashflow, investing, forecasting |
| 05_SKELETON | Skeleton | Rules, constraints, hierarchy, permissions, time architecture |
| 06_MUSCLE | Muscle | Run commands, write code, deploy and automate |
| 07_METABOLISM | Metabolism | Pipelines, transforms, IO routing and cleanup |
| 08_WORLD_MODEL | World Model | Macroeconomics, geopolitics, sectors, supply chains |
| 09_SOCIAL_ENGINE | Social Engine | Humans, negotiation, influence, social patterns |
| 10_LIFE_ENGINE | Life Engine | Sleep, energy, health, mood, routines, cycles |
| 11_LEGAL_BRAIN | Legal Brain | Contracts, IP, compliance, regulatory scanning |
| 12_QUANTUM_LAYER | Quantum Layer | Timing, probability flows, synchronicities |
| 13_FACTORY | Factory | Agent creation, quality monitoring, self-upgrade |
| 14_INTERFACES | Interfaces | CLI, API, web dashboard, chat integration |

## Core Principles (Global Laws)

1. **Law of Law (L1)**: All reasoning must obey physical, biological, institutional, and legal constraints
2. **Rule of 2 (L2)**: Check at least two contrasting perspectives for every analysis
3. **Rule of 4 (L3)**: Consider four quadrants: biological, technical, economic, environmental
4. **Absolute Structural Integrity (L4)**: All outputs must be logically consistent and auditable
5. **Post-Theory Communication (L5)**: Language must be clear, grounded, and interpretable
6. **UBI Alignment (L6)**: Align with Unified Biological Intelligence principles

## Quick Start

### Run the Organism

```bash
# Interactive mode
python amos_organism.py --mode interactive

# Single cycle
python amos_organism.py --mode single --goal "system_diagnostic"

# Daemon mode (continuous)
python amos_organism.py --mode daemon
```

### Test Individual Subsystems

```bash
# Test Brain
python 01_BRAIN/brain_kernel.py

# Test Senses
python 02_SENSES/senses_kernel.py
```

## Project Structure

```
AMOS_ORGANISM_OS/
├── 00_ROOT/               # Identity and global configuration
│   ├── root_manifest.json # System identity and laws
│   └── config/
├── 01_BRAIN/              # Cognitive processing
│   ├── brain_kernel.py    # Main brain orchestrator
│   ├── memory/            # Working and canonical memory
│   └── logs/
├── 02_SENSES/             # Environmental sensing
│   ├── senses_kernel.py   # Input processing
│   └── sensors/           # Individual sensor modules
├── 03_IMMUNE/             # (Planned) Safety and compliance
├── 04_BLOOD/              # (Planned) Financial engine
├── 05_SKELETON/           # (Planned) Rules and constraints
├── 06_MUSCLE/             # (Planned) Code execution
├── 07_METABOLISM/         # (Planned) Data pipelines
├── 08_WORLD_MODEL/        # (Planned) Global context
├── 09_SOCIAL_ENGINE/      # (Planned) Social intelligence
├── 10_LIFE_ENGINE/        # (Planned) Biological cycles
├── 11_LEGAL_BRAIN/        # (Planned) Legal reasoning
├── 12_QUANTUM_LAYER/      # (Planned) Probabilistic reasoning
├── 13_FACTORY/            # (Planned) Self-modification
├── 14_INTERFACES/         # (Planned) User interfaces
├── _shared/               # Shared resources
│   ├── engines/           # Cognitive engine definitions
│   ├── kernels/           # Core kernel implementations
│   └── utils/             # Utility functions
└── amos_organism.py       # Main orchestrator
```

## Creator

**Trang Phan** - Origin Architect and Primary Systems Designer
- Vietnamese systems architect
- Creator of Unified Biological Intelligence framework
- NeuroSyncAI founder

## License

Proprietary - All frameworks, terminology, and structural methods are intellectual property.

## Connection to Legacy Brain

This organism implementation connects to the legacy AMOS brain files located at:
`/_AMOS_BRAIN/_LEGACY BRAIN/Core/`

The cognitive engines defined in the legacy JSON files (Cognition, Consciousness, Emotion, Mind, etc.) are being progressively integrated into this operational organism structure.
