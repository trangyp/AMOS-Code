#!/usr/bin/env python3
"""Verify repository status."""

import ast
import sys
from pathlib import Path

repo_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
python_files = list(repo_path.rglob("*.py"))
python_files = [f for f in python_files if ".venv" not in str(f) and "__pycache__" not in str(f)]

syntax_errors = 0
for f in python_files:
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        print(f"SyntaxError: {f}:{e.lineno}")
        syntax_errors += 1

print(f"Files: {len(python_files)}")
print(f"Syntax errors: {syntax_errors}")

# Try importing brain
sys.path.insert(0, str(repo_path))
try:
    print("Brain: OK")
except Exception as e:
    print(f"Brain: {e}")

print("\nRepository verified.")
