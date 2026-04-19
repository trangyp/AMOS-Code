#!/usr/bin/env python3
"""
Brain-driven production fixer - Uses AMOS brain to analyze and fix critical production blockers
"""
import os
import re
import ast
from pathlib import Path
from amos_brain_working import think

# Files identified by brain as having critical syntax errors
CRITICAL_FILES = [
    "amos_observability_engine.py",
    "amos_brain_cli_legacy.py",
    "amos_mcp_enhanced.py",
    "amos_event_architecture_enhanced.py",
    "amos_equation_jax.py",
    "amos_fastloop_brain_bridge.py",
    "amos_alert_manager.py",
    "amos_data_infrastructure.py",
    "amos_performance_profiler.py",
    "amos_intelligent_modernizer.py",
    "amos_secrets_manager.py",
    "amos_real_brain_integration.py",
]

def fix_common_syntax_errors(content: str) -> str:
    """Fix common syntax error patterns."""
    # Fix 1: Remove misplaced typing imports inside try blocks
    # Pattern: try:\n\s+from typing import
    content = re.sub(
        r'(try:\s*\n)(\s+)(from typing import[^\n]+\n)+',
        r'\1',
        content
    )
    
    # Fix 2: Remove duplicate typing imports
    lines = content.split('\n')
    seen_imports = set()
    fixed_lines = []
    
    for line in lines:
        if line.startswith('from typing import'):
            if line in seen_imports:
                continue  # Skip duplicate
            seen_imports.add(line)
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_file(filepath: Path) -> dict:
    """Fix a single file using brain-guided analysis."""
    result = {"file": str(filepath), "fixed": False, "changes": [], "error": None}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        result["error"] = f"Read error: {e}"
        return result
    
    # Apply common fixes
    content = fix_common_syntax_errors(original)
    
    # Verify syntax
    try:
        ast.parse(content)
        result["syntax_valid"] = True
    except SyntaxError as e:
        result["syntax_valid"] = False
        result["error"] = f"Line {e.lineno}: {e.msg}"
    
    # Write if changed and valid
    if content != original and result.get("syntax_valid"):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        result["fixed"] = True
        result["changes"].append("Fixed common syntax patterns")
    
    return result

def main():
    repo_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    
    print("=" * 70)
    print("🧠 BRAIN-DRIVEN PRODUCTION FIXER")
    print("=" * 70)
    
    # Use brain to prioritize
    context = {
        "files": CRITICAL_FILES,
        "goal": "production_blockers"
    }
    
    brain_result = think(
        "Prioritize these critical files for fixing. Consider: 1) Core functionality impact, "
        "2) Dependencies on other files, 3) Complexity of fixes. Return top 5 priorities with fix strategy.",
        context
    )
    
    print(f"\nBrain Status: {brain_result.get('status', 'unknown')}")
    print(f"Mode: {brain_result.get('mode', 'unknown')}")
    
    # Get priority from brain
    priorities = brain_result.get('priorities', CRITICAL_FILES[:5])
    
    print("\n📝 Brain Priority List:")
    for i, p in enumerate(priorities[:5], 1):
        print(f"  {i}. {p}")
    
    # Fix files
    print("\n" + "=" * 70)
    print("FIXING FILES...")
    print("=" * 70)
    
    fixed_count = 0
    error_count = 0
    
    for filename in priorities[:5]:
        filepath = repo_path / filename
        if not filepath.exists():
            print(f"\n? {filename} - NOT FOUND")
            continue
        
        print(f"\n→ {filename}")
        result = fix_file(filepath)
        
        if result["fixed"]:
            print(f"  ✓ Fixed")
            fixed_count += 1
        elif result.get("syntax_valid"):
            print(f"  ✓ Already valid")
        else:
            print(f"  ✗ Error: {result.get('error', 'Unknown')}")
            error_count += 1
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {fixed_count} fixed, {error_count} errors remaining")
    
    # Brain analysis of results
    if error_count > 0:
        context = {"errors": error_count, "fixed": fixed_count}
        analysis = think(
            f"Analysis: Fixed {fixed_count} files, {error_count} still have errors. "
            "What should be the next steps for remaining errors?",
            context
        )
        print(f"\nBrain Recommendation: {analysis.get('recommendation', 'Continue fixing')}")

if __name__ == "__main__":
    main()
