#!/usr/bin/env python3
"""Diagnostic script to find real issues in AMOS codebase"""

import os
import py_compile
import sys

sys.path.insert(0, ".")


def check_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("AMOS DIAGNOSTIC REPORT")
    print("=" * 60)

    # 1. Check backend files for syntax errors
    print("\n1. Checking backend files for syntax errors...")
    backend_files = []
    for root, dirs, files in os.walk("backend"):
        for f in files:
            if f.endswith(".py"):
                backend_files.append(os.path.join(root, f))

    errors = []
    for f in backend_files:
        ok, err = check_syntax(f)
        if not ok:
            errors.append((f, err))

    if errors:
        print(f"   ❌ Found {len(errors)} files with syntax errors:")
        for f, e in errors[:5]:
            print(f"      {f}: {e}")
    else:
        print(f"   ✅ All {len(backend_files)} backend files have valid syntax")

    # 2. Try importing critical modules
    print("\n2. Testing critical module imports...")
    modules = [
        "backend.main",
        "backend.api.schemas",
        "backend.api.agents",
        "backend.api.auth",
        "backend.health",
        "backend.database",
    ]

    for mod in modules:
        try:
            __import__(mod)
            print(f"   ✅ {mod}")
        except Exception as e:
            print(f"   ❌ {mod}: {str(e)[:50]}")

    # 3. Check for Python 3.9 compatibility issues
    print("\n3. Checking Python 3.9 compatibility...")
    issues = []
    for f in backend_files[:50]:
        try:
            with open(f) as file:
                content = file.read()
            if "" in content or "| int" in content or "| str" in content:
                issues.append(f)
        except Exception:
            pass

    if issues:
        print(f"   ⚠️  {len(issues)} files may have Python 3.9 compatibility issues:")
        for f in issues[:5]:
            print(f"      {f}")
    else:
        print("   ✅ Python 3.9 compatibility OK")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
