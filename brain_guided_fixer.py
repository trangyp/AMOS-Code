#!/usr/bin/env python3
"""
Brain-guided fixer - Uses AMOS brain to analyze and fix real files
"""
import ast
import os
import sys
from pathlib import Path
from amos_brain_working import think

def check_file_syntax(filepath: str) -> dict:
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {"valid": False, "error": f"Line {e.lineno}: {e.msg}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def find_files_with_errors(repo_path: str, limit: int = 50) -> list:
    """Find Python files with syntax errors."""
    error_files = []
    count = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.venv']]
        
        for filename in files:
            if not filename.endswith('.py'):
                continue
            if count >= limit:
                break
                
            filepath = os.path.join(root, filename)
            result = check_file_syntax(filepath)
            
            if not result["valid"]:
                error_files.append({
                    "filepath": filepath,
                    "error": result["error"]
                })
                count += 1
    
    return error_files

def use_brain_to_prioritize(error_files: list) -> dict:
    """Use AMOS brain to prioritize which files to fix first."""
    context = {
        "task": "prioritize_syntax_fixes",
        "error_count": len(error_files),
        "error_files": [f["filepath"] for f in error_files[:20]],
        "goal": "fix_critical_production_blockers"
    }
    
    result = think(
        "Analyze these files with syntax errors and prioritize them for fixing. "
        "Consider: 1) Files in backend/ are critical for API, 2) Files in clawspring/amos_brain/ are critical for brain, "
        "3) Files with simple import errors are quick wins. Return a prioritized list with fix strategy.",
        context
    )
    
    return result

def main():
    repo_path = "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
    
    print("=" * 70)
    print("🧠 BRAIN-GUIDED SYNTAX FIXER")
    print("=" * 70)
    
    # Find files with errors
    print("\n[Phase 1] Scanning for syntax errors...")
    error_files = find_files_with_errors(repo_path, limit=30)
    print(f"Found {len(error_files)} files with syntax errors")
    
    if not error_files:
        print("\n✓ No syntax errors found!")
        return
    
    # Show first 10 errors
    print("\n[Phase 2] Syntax errors found:")
    for i, err in enumerate(error_files[:10], 1):
        print(f"\n{i}. {err['filepath'].replace(repo_path + '/', '')}")
        print(f"   Error: {err['error']}")
    
    # Use brain to prioritize
    print("\n[Phase 3] Consulting brain for prioritization...")
    brain_result = use_brain_to_prioritize(error_files)
    
    print(f"\nBrain Status: {brain_result.get('status', 'unknown')}")
    print(f"Mode: {brain_result.get('mode', 'unknown')}")
    print(f"Brain Used: {brain_result.get('brain_used', False)}")
    
    # Get recommendations
    recommendations = brain_result.get('recommendations', [])
    if recommendations:
        print("\n📝 BRAIN RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:10], 1):
            print(f"\n{i}. {rec.get('file', 'Unknown')}")
            print(f"   Priority: {rec.get('priority', 'medium')}")
            print(f"   Fix: {rec.get('fix', 'Review manually')}")
    
    # Show fixable errors
    print("\n[Phase 4] Quick fixes needed:")
    import_errors = [f for f in error_files if "import" in f["error"].lower()]
    for err in import_errors[:5]:
        print(f"\n  - {err['filepath']}")
        print(f"    {err['error']}")
    
    print("\n" + "=" * 70)
    print(f"\nTotal files with errors: {len(error_files)}")
    print(f"Import-related errors (quick fixes): {len(import_errors)}")
    
    # Save results
    output = {
        "brain_result": brain_result,
        "error_files": error_files,
        "import_errors": import_errors,
        "total": len(error_files)
    }
    
    import json
    with open("/tmp/brain_fixer_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print("\nResults saved to /tmp/brain_fixer_results.json")

if __name__ == "__main__":
    main()
