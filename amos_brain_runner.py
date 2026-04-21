#!/usr/bin/env python3
"""AMOS Brain Runner - Actually uses the brain components.

This script demonstrates real brain usage from amos_brain.
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Run brain-guided operations."""
    print("="*60)
    print("AMOS BRAIN RUNNER")
    print("="*60)
    
    # 1. Import brain facade
    print("\n[1] Importing amos_brain facade...")
    try:
        from amos_brain.facade import get_brain, BrainClient
        brain = get_brain()
        print(f"   ✅ BrainClient: {type(brain).__name__}")
        print(f"   ✅ Initialized: {brain.initialized}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1
    
    # 2. Use brain.think()
    print("\n[2] Testing brain.think()...")
    try:
        result = brain.think("What is the best approach to fix code?")
        print(f"   ✅ Result: {result}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Use brain.decide()
    print("\n[3] Testing brain.decide()...")
    try:
        decision = brain.decide(
            context={"task": "code_fix", "priority": "high"},
            options=["quick_fix", "deep_refactor", "manual_review"]
        )
        print(f"   ✅ Decision: {decision}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Use brain.validate_action()
    print("\n[4] Testing brain.validate_action()...")
    try:
        validation = brain.validate_action(
            action="delete_file",
            context={"file": "important.py", "backup_exists": True}
        )
        print(f"   ✅ Validation: {validation}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Use brain.get_state()
    print("\n[5] Testing brain.get_state()...")
    try:
        state = brain.get_state()
        print(f"   ✅ State keys: {list(state.keys())}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Use kernel bridge with brain
    print("\n[6] Testing brain-kernel bridge...")
    try:
        from amos_kernel.brain_kernel_bridge import get_brain_kernel_bridge
        bridge = get_brain_kernel_bridge()
        print(f"   ✅ Bridge created")
        
        # Try to use brain through bridge
        if bridge.brain:
            print(f"   ✅ Bridge has brain access")
        else:
            print(f"   ⚠️  Bridge missing brain")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 7. Use TreeSitter from repo_doctor
    print("\n[7] Testing TreeSitter integration...")
    try:
        from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest
        ingest = TreeSitterIngest()
        print(f"   ✅ TreeSitterIngest: {type(ingest).__name__}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("BRAIN RUNNER COMPLETE")
    print("="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
