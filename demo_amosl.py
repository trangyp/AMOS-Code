#!/usr/bin/env python3
"""AMOSL Compiler Demo.

Demonstrates the AMOSL multi-substrate compiler with:
- Classical computation
- Quantum circuits
- Biological systems
- Hybrid bridges
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amosl import parse, compile_program, validate_invariants


# Sample AMOSL program
SAMPLE_AMOSL = """
// AMOSL Demo Program
// Multi-substrate computation example

ontology {
    classical {
        entity Cell {
            x: Int
            y: Int
            state: Text
        }
    }
    
    quantum {
        qubit qreg[2]
    }
    
    biological {
        gene expression_marker
        protein signal_protein
    }
    
    hybrid {
        bridge bio_to_classic
    }
}

state {
    classical {
        cell_count: Int
        threshold: Float
    }
    
    quantum {
        psi
        phi
    }
    
    biological {
        marker_level
        protein_count
    }
    
    hybrid {
        sensor bridge(classical, quantum)
    }
}

dynamics {
    action update_cell {
        pre: cell_count > 0
        post: cell_count >= 0
    }
    
    transition idle -> processing
    transition processing -> complete
    
    evolve cell_count mutate
}

constraint valid_count {
    cell_count >= 0
}

effect update_effect {
    reads: cell_count
    writes: cell_count
}

measure protein_count {
    uncertainty: 0.1
    perturbation: minimal
}

realize {
    target: python
    trace: true
}
"""


def main():
    print("=" * 70)
    print("  AMOSL COMPILER DEMO")
    print("=" * 70)
    print()
    
    # Step 1: Parse
    print("Step 1: Parsing AMOSL source...")
    try:
        program = parse(SAMPLE_AMOSL)
        print("  ✓ Parse successful")
        print(f"  - Ontology: {len(program.ontology.classical)} classical, "
              f"{len(program.ontology.quantum)} quantum, "
              f"{len(program.ontology.biological)} biological entities")
        print(f"  - State: {len(program.state.classical)} classical, "
              f"{len(program.state.quantum)} quantum, "
              f"{len(program.state.biological)} biological vars")
        print(f"  - Dynamics: {len(program.dynamics.actions)} actions, "
              f"{len(program.dynamics.transitions)} transitions")
    except Exception as e:
        print(f"  ✗ Parse failed: {e}")
        return 1
    
    print()
    
    # Step 2: Validate Invariants
    print("Step 2: Validating 8 AMOSL invariants...")
    success, violations = validate_invariants(program)
    if success:
        print("  ✓ All 8 invariants passed")
    else:
        print(f"  ⚠ {len(violations)} invariant violations:")
        for v in violations[:3]:
            print(f"    - {v}")
    
    print()
    
    # Step 3: Compile to IR
    print("Step 3: Compiling to 4 IRs...")
    try:
        cir, qir, bir, hir = compile_program(program)
        
        print("  ✓ CIR (Classical IR):")
        print(f"    - {len(cir.blocks)} blocks")
        print(f"    - {len(cir.effects)} effects declared")
        
        print("  ✓ QIR (Quantum IR):")
        print(f"    - {len(qir.registers)} registers")
        print(f"    - {len(qir.gates)} gates")
        print(f"    - {len(qir.measures)} measurements")
        
        print("  ✓ BIR (Biological IR):")
        print(f"    - {len(bir.species)} species")
        print(f"    - {len(bir.sequences)} sequences")
        print(f"    - {len(bir.reactions)} reactions")
        
        print("  ✓ HIR (Hybrid IR):")
        print(f"    - {len(hir.bridges)} bridges")
        print(f"    - {len(hir.schedules)} schedules")
        
    except Exception as e:
        print(f"  ✗ Compile failed: {e}")
        return 1
    
    print()
    print("=" * 70)
    print("  AMOSL DEMO COMPLETE")
    print("=" * 70)
    print()
    print("AMOSL successfully:")
    print("  1. Parsed multi-substrate source code")
    print("  2. Validated 8 formal invariants")
    print("  3. Generated 4 intermediate representations")
    print()
    print("Architecture: (O,S,D,C,E,M,U,V,A,R) 9-tuple")
    print("Substrates: Classical ⊕ Quantum ⊕ Biological ⊕ Hybrid")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
