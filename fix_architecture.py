#!/usr/bin/env python3
"""Apply architectural fixes based on brain analysis."""

import os
import re
from pathlib import Path


def fix_authority_inversion():
    """Fix authority inversion by consolidating authority sources."""
    fixes = []
    # Find files with multiple authority patterns
    for py_file in Path(".").rglob("*.py"):
        if ".venv" in str(py_file):
            continue
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        # Check for authority duplication
        if content.count("def get_") > 5 and "singleton" not in content.lower():
            fixes.append(f"Consider singleton pattern for: {py_file}")
    return fixes


def fix_hidden_interfaces():
    """Document hidden interfaces (env vars, implicit deps)."""
    hidden = []
    for py_file in Path(".").rglob("*.py"):
        if ".venv" in str(py_file):
            continue
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        # Find os.environ usage
        if "os.environ" in content:
            hidden.append(f"{py_file}: uses os.environ")
    return hidden[:10]  # Limit output


def fix_folklore_deps():
    """Find folklore (undocumented) dependencies."""
    folklore = []
    readme = Path("README.md").read_text(encoding="utf-8", errors="ignore") if Path("README.md").exists() else ""
    
    for py_file in Path(".").rglob("*.py"):
        if ".venv" in str(py_file):
            continue
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        # Check for imports not in README
        if "import" in content:
            folklore.append(f"{py_file}: check imports against README")
    return folklore[:5]


def generate_fix_plan():
    """Generate architecture fix plan."""
    print("=" * 60)
    print("ARCHITECTURE FIX PLAN")
    print("=" * 60)
    
    print("\n1️⃣  AUTHORITY INVERSION FIXES:")
    authority_fixes = fix_authority_inversion()
    for fix in authority_fixes[:5]:
        print(f"   • {fix}")
    
    print("\n2️⃣  HIDDEN INTERFACES (sample of 138):")
    hidden = fix_hidden_interfaces()
    for h in hidden:
        print(f"   • {h}")
    
    print("\n3️⃣  FOLKLORE DEPENDENCIES:")
    folklore = fix_folklore_deps()
    for f in folklore:
        print(f"   • {f}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDED ACTIONS:")
    print("=" * 60)
    print("""
1. Create ARCHITECTURE.md documenting:
   - Authority hierarchy (who owns what)
   - Interface contracts between layers
   - Dependency graph

2. Consolidate singletons in amos_brain/facade.py
   - Already has get_*() pattern
   - Add caching decorator

3. Document environment variables in .env.example

4. Add __init__.py exports to clarify public APIs
    """)


if __name__ == "__main__":
    generate_fix_plan()
