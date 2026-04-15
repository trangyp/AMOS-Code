# AMOS Brain Ω∞∞∞ - Onboarding Guide

Welcome to the AMOS (Adaptive Meta-Organizational System) Brain. This guide will help you understand and work with the system.

## Quick Start

### Prerequisites
- Python 3.10+
- Git
- Optional: Ollama or LM Studio for local LLM support

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd AMOS-code

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "from amos_brain.facade import AMOSBrainFacade; print('✓ AMOS Brain ready')"
```

## System Architecture

The AMOS Brain consists of multiple layers:

1. **Cognitive Layer (8 layers)** - Sensory to Value processing
2. **Meta-Architecture Layer** - Self-aware structural integrity
3. **Repo Doctor Ω∞∞∞** - Repository verification and repair

## Key Components

### Repo Doctor Ω∞∞∞
Repository verification engine with:
- **8 Substrates**: Tree-sitter, Import, API, Entrypoint, Packaging, Status, Test, Security
- **21 Invariants**: Parse, Import, API, Entrypoint, Packaging, Status, Test, Security + 13 meta
- **39 Basis Vectors**: Complete state space including meta-architecture
- **Z3 Solver**: SMT-based repair optimization
- **Temporal Mechanics**: Drift tracking, bisect automation
- **Graph Analysis**: Entanglement matrix M_ij

### Running Repo Doctor
```python
from repo_doctor_omega.invariants.meta import LawHierarchyInvariant, LegibilityInvariant

# Check law hierarchy
inv = LawHierarchyInvariant()
result = inv.check(".")
print(f"Passed: {result.passed}")

# Check legibility
legib = LegibilityInvariant()
result = legib.check(".")
print(f"Has onboarding: {result.metadata['found_onboarding']}")
```

## Development Workflow

### Making Changes
1. Run Repo Doctor before committing
2. Check for invariant violations
3. Review entanglement report for coupling issues
4. Ensure all tests pass

### Testing
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_repo_doctor.py -v
```

## Emergency Procedures

### System Recovery
If the brain detects critical failures:
1. Check energy level: `state.compute_energy()`
2. Identify collapsed subsystems: `state.collapsed_subsystems()`
3. Run repair optimizer for fix suggestions
4. Execute safe repairs in recommended order

### Escalation Path
1. **Level 1**: Automated repair (safe batch)
2. **Level 2**: Human-reviewed repair (risky batch)
3. **Level 3**: Emergency constitution activation

## Architecture Decision Records (ADRs)

Key architectural decisions are documented in:
- `BRAIN_DECISION_SUMMARY.md` - Complete decision history
- `ARCHITECTURE.md` - System architecture overview
- `OMEGA_AXIOMS.md` - Formal axiomatic foundation

## Common Tasks

### Adding a New Invariant
```python
from repo_doctor_omega.invariants.hard import HardInvariant, InvariantKind
from repo_doctor_omega.state.basis import BasisVector

class MyInvariant(HardInvariant):
    def __init__(self):
        super().__init__(InvariantKind.MY, BasisVector.MY)
    
    def check(self, repo_path: str, context=None):
        # Implementation
        pass
```

### Running Security Analysis
```python
from repo_doctor_omega.ingest import SecuritySubstrate

sub = SecuritySubstrate(".")
analysis = sub.analyze_repository()
print(f"Critical issues: {analysis.critical_count}")
print(f"High issues: {analysis.high_count}")
```

### Entanglement Analysis
```python
from repo_doctor_omega.graph.entanglement import EntanglementAnalyzer

analyzer = EntanglementAnalyzer(".")
matrix = analyzer.analyze()
print(f"Total entanglement: {matrix.total_entanglement}")
high = matrix.get_highly_entangled(threshold=0.8)
print(f"Highly coupled pairs: {len(high)}")
```

## Getting Help

### Documentation
- `README.md` - Project overview
- `AMOS_BRAIN_GUIDE.md` - Brain architecture guide
- `REPO_DOCTOR_QUICK_REFERENCE.md` - Repo Doctor reference
- `docs/` - Additional documentation

### Debugging
```python
from amos_brain.debug_utils import ic, trace, pretty_print

# Use icecream for debugging
ic(variable_name)

# Trace function execution
with trace():
    my_function()

# Pretty print complex structures
pretty_print(my_complex_object)
```

## Governance

### Constitutional Structure
The AMOS Brain operates under a formal constitutional structure:
- **Law Hierarchy**: Invariant precedence rules
- **Emergency Constitution**: Incident response procedures
- **Meta-Architecture**: Self-governance mechanisms

### Contributing
1. Follow the 8-layer cognitive architecture
2. Maintain invariant compliance
3. Document all architectural decisions
4. Ensure legibility for future maintainers

## Next Steps

1. Explore `examples/` directory for usage examples
2. Read `BRAIN_DECISION_SUMMARY.md` for architecture evolution
3. Run `python3 amos_8layer_demo.py` for live demonstration
4. Review `test_repo_doctor.py` for integration patterns

---

**Version**: AMOS v∞.Ω.Λ.X  
**Last Updated**: 2026-04-15  
**Maintainer**: AMOS Brain Architecture Team
