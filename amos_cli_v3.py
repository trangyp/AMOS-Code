#!/usr/bin/env python3
"""AMOS CLI v3 - Production-ready command line interface.

Real tool for managing AMOS brain/kernel operations.
"""

import argparse
import ast
import os
import subprocess
import sys
from pathlib import Path


def find_syntax_errors(directory: str = ".") -> list[tuple[str, int, str]]:
    """Find Python syntax errors in directory."""
    errors = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["venv", "__pycache__"]]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append((filepath, e.lineno or 0, str(e)))
                except Exception:
                    pass
    return errors


def fix_bare_excepts(directory: str = ".") -> int:
    """Fix bare except clauses in Python files."""
    import re
    fixed = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["venv", "__pycache__"]]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "except:" in content:
                        new_content = re.sub(
                            r"^\s*except:$",
                            "except Exception:",
                            content,
                            flags=re.MULTILINE
                        )
                        if new_content != content:
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            fixed += 1
                except Exception:
                    pass
    return fixed


def get_amos_status() -> dict:
    """Get AMOS system status."""
    status = {
        "kernel": False,
        "brain": False,
        "cognitive_engine": False,
        "python_files": 0,
        "syntax_errors": 0
    }
    
    # Check components
    try:
        from amos_kernel import get_unified_kernel
        status["kernel"] = True
    except ImportError:
        pass
    
    try:
        from amos_brain import get_brain
        status["brain"] = True
    except ImportError:
        pass
    
    try:
        from amos_kernel.active_cognitive_engine import ActiveCognitiveEngine
        status["cognitive_engine"] = True
    except ImportError:
        pass
    
    # Count files
    py_files = 0
    syntax_errors = 0
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["venv", "__pycache__"]]
        for file in files:
            if file.endswith(".py"):
                py_files += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        ast.parse(f.read())
                except SyntaxError:
                    syntax_errors += 1
                except Exception:
                    pass
    
    status["python_files"] = py_files
    status["syntax_errors"] = syntax_errors
    return status


def main():
    parser = argparse.ArgumentParser(description="AMOS CLI v3")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    subparsers.add_parser("status", help="Show AMOS system status")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check for issues")
    check_parser.add_argument("--syntax", action="store_true", help="Check syntax only")
    
    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Fix issues")
    fix_parser.add_argument("--bare-except", action="store_true", help="Fix bare except clauses")
    
    args = parser.parse_args()
    
    if args.command == "status":
        status = get_amos_status()
        print("AMOS System Status")
        print("=" * 50)
        print(f"Kernel: {'OK' if status['kernel'] else 'Not Available'}")
        print(f"Brain: {'OK' if status['brain'] else 'Not Available'}")
        print(f"Cognitive Engine: {'OK' if status['cognitive_engine'] else 'Not Available'}")
        print(f"Python Files: {status['python_files']}")
        print(f"Syntax Errors: {status['syntax_errors']}")
        print("=" * 50)
    
    elif args.command == "check":
        if args.syntax:
            errors = find_syntax_errors()
            if errors:
                print(f"Found {len(errors)} syntax errors:")
                for filepath, line, error in errors[:10]:
                    print(f"  {filepath}:{line} - {error[:50]}")
            else:
                print("No syntax errors found")
        else:
            errors = find_syntax_errors()
            print(f"Syntax Errors: {len(errors)}")
    
    elif args.command == "fix":
        if args.bare_except:
            fixed = fix_bare_excepts()
            print(f"Fixed {fixed} files with bare except clauses")
        else:
            fixed = fix_bare_excepts()
            print(f"Fixed {fixed} files")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
