#!/usr/bin/env python3
"""AMOS Auto Repair - Self-healing system using AMOS brain.

Uses cognitive engine to analyze and fix codebase issues automatically.
"""

import ast
import os
import re
from pathlib import Path
from typing import Optional


class AMOSAutoRepair:
    """Automated code repair using AMOS patterns."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.fixed_files: list[str] = []
        self.errors: list[str] = []

    def scan_syntax_errors(self) -> list[tuple[str, int, str]]:
        """Scan for Python syntax errors."""
        errors = []
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["venv", "__pycache__"]
            ]
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

    def fix_empty_if_statements(self, filepath: str) -> bool:
        """Fix empty if str(p) not in sys.path: statements."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            original = content
            # Pattern: if str(...) not in sys.path: followed by blank line
            pattern = r'(if str\([^)]+\) not in sys\.path:)\s*\n\s*\n'
            replacement = r'\1\n    sys.path.insert(0, str(p))\n\n'

            content = re.sub(pattern, replacement, content)

            if content != original:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False
        except Exception:
            return False

    def fix_bare_excepts(self, filepath: str) -> bool:
        """Fix bare except: clauses."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            original = content
            content = re.sub(
                r"^\s*except:$", "except Exception:", content, flags=re.MULTILINE
            )

            if content != original:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            return False
        except Exception:
            return False

    def repair_all(self) -> dict[str, any]:
        """Run all repair operations."""
        results = {
            "syntax_errors_found": 0,
            "syntax_errors_fixed": 0,
            "empty_if_fixed": 0,
            "bare_except_fixed": 0,
            "files_modified": [],
            "errors": [],
        }

        # Fix empty if statements in backend
        backend_api = self.root_path / "backend" / "api"
        if backend_api.exists():
            for pyfile in backend_api.glob("*.py"):
                if self.fix_empty_if_statements(str(pyfile)):
                    results["empty_if_fixed"] += 1
                    results["files_modified"].append(str(pyfile))

        # Fix bare excepts in amos_kernel
        amos_kernel = self.root_path / "amos_kernel"
        if amos_kernel.exists():
            for pyfile in amos_kernel.rglob("*.py"):
                if self.fix_bare_excepts(str(pyfile)):
                    results["bare_except_fixed"] += 1
                    if str(pyfile) not in results["files_modified"]:
                        results["files_modified"].append(str(pyfile))

        # Check remaining syntax errors
        errors = self.scan_syntax_errors()
        results["syntax_errors_found"] = len(errors)

        return results


def main():
    """Run AMOS auto repair."""
    repair = AMOSAutoRepair()
    print("AMOS Auto Repair - Starting...")
    print("=" * 50)

    results = repair.repair_all()

    print(f"Empty if statements fixed: {results['empty_if_fixed']}")
    print(f"Bare except clauses fixed: {results['bare_except_fixed']}")
    print(f"Files modified: {len(results['files_modified'])}")
    print(f"Syntax errors remaining: {results['syntax_errors_found']}")

    if results["files_modified"]:
        print("\nModified files:")
        for f in results["files_modified"][:10]:
            print(f"  - {f}")

    print("=" * 50)
    print("AMOS Auto Repair - Complete")


if __name__ == "__main__":
    main()
