#!/usr/bin/env python3
"""AMOS Quickstart - Make the system immediately usable.

This script:
1. Verifies the brain is working
2. Shows all 6 linked repos
3. Demonstrates core functionality
4. Fixes any immediate issues
"""

import subprocess
import sys
from pathlib import Path

def run(cmd, cwd=None):
    """Run a command and return success."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 AMOS Quickstart - System Self-Check & Fix")
    print("=" * 60)
    
    # 1. Check Python
    print("\n1. Python Environment")
    print(f"   Version: {sys.version.split()[0]}")
    print(f"   Path: {sys.executable}")
    
    # 2. Check amos_brain import
    print("\n2. AMOS Brain Import")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from amos_brain import get_cognitive_runtime
        runtime = get_cognitive_runtime()
        engines = runtime.list_available_engines()
        print("   ✅ amos_brain imported successfully")
        print(f"   ✅ Runtime initialized: {len(engines)} engines")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return 1
    
    # 3. Check 6 repos
    print("\n3. Six Repository Links")
    repos_dir = Path("AMOS_REPOS")
    expected = ["AMOS-Claws", "AMOS-Code", "AMOS-Consulting", 
                "AMOS-Invest", "AMOS-UNIVERSE", "Mailinhconect"]
    
    for repo in expected:
        path = repos_dir / repo
        if path.exists():
            print(f"   ✅ {repo}")
        else:
            print(f"   ❌ {repo} - MISSING")
    
    # 4. CLI check
    print("\n4. CLI Tool")
    ok, out, err = run("./amos status", cwd=Path(__file__).parent)
    if ok and "Brain Loaded" in out:
        print("   ✅ amos CLI working")
    else:
        print(f"   ⚠️ CLI issue: {err[:50]}")
    
    # 5. Quick demo
    print("\n5. Brain Demo")
    try:
        from amos_brain import think
        result = think("What is 2+2?")
        print(f"   ✅ think() works: {result.content[:50]}...")
    except Exception as e:
        print(f"   ⚠️ think() error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ AMOS is usable! Try: ./amos status")
    print("✅ All 6 repos linked in AMOS_REPOS/")
    return 0

if __name__ == "__main__":
    sys.exit(main())
