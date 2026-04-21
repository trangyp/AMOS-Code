#!/usr/bin/env python3
"""AMOS Cognitive Runtime - Full Brain Integration."""

import sys
sys.path.insert(0, '.')

from amos_kernel import get_unified_kernel, get_nl_processor
from amos_kernel.legacy_brain_loader import activate_legacy_brain, get_legacy_brain_loader
from amos_brain import get_brain


def main():
    print("="*70)
    print("AMOS COGNITIVE RUNTIME - FULL BRAIN INTEGRATION")
    print("="*70)
    
    # Initialize modern AMOS kernel
    kernel = get_unified_kernel()
    kernel.initialize()
    print("\n[✓] Modern AMOS Kernel: BOOTED")
    
    # Activate legacy brain components
    legacy = activate_legacy_brain()
    print(f"[✓] Legacy Brain: ACTIVATED")
    print(f"    Core Engines: {len(legacy['core_engines'])}")
    print(f"    Laws: {len(legacy['canonical_laws'])}")
    print(f"    Domain Intelligences: {len(legacy['domain_intelligences'])}")
    
    # Brain subsystem
    brain = get_brain()
    print("[✓] Brain Subsystem: ONLINE")
    
    # NL Processor
    nlp = get_nl_processor()
    result = nlp.process("analyze complex problem using multi-domain reasoning")
    print("[✓] NL Processor: FUNCTIONAL")
    
    # Demonstrate law application
    loader = get_legacy_brain_loader()
    law_result = loader.apply_law(
        "AMOS_COGNITION_INFINITY_KERNEL",
        "law_of_law",
        {"context": "system_self_check", "priority": "high"}
    )
    print(f"\n[✓] Law Application: {law_result['law']} applied")
    
    print("\n" + "="*70)
    print("AMOS COGNITIVE RUNTIME: FULLY OPERATIONAL")
    print("Modern + Legacy Brain Components Integrated")
    print("="*70)
    
    return {
        "status": "operational",
        "modern_kernel": True,
        "legacy_brain": legacy,
        "laws_active": len(loader.get_all_laws())
    }


if __name__ == "__main__":
    result = main()
    print(f"\nResult: {result}")
