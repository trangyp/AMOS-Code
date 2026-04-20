#!/usr/bin/env python3
"""AMOS Brain-powered typing modernization system.

Uses the AMOS Brain to systematically fix typing issues across the codebase.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any, Optional

# Add AMOS to path
sys.path.insert(0, str(Path(__file__).parent))


def find_python_files(root_dir: str, exclude_patterns: list[Optional[str]] = None) -> list[Path]:
    """Find all Python files in directory, excluding venv and similar."""
    exclude_patterns = exclude_patterns or [".venv", "node_modules", "__pycache__", ".git"]
    files = []
    root = Path(root_dir)
    for f in root.rglob("*.py"):
        if any(p in str(f) for p in exclude_patterns):
            continue
        files.append(f)
    return files


def analyze_file(file_path: Path) -> dict[str, Any]:
    """Analyze a Python file for typing issues."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}

    # Check for deprecated typing patterns
    issues = {
        "has_list": "list[" in content,
        "has_dict": "dict[" in content,
        "has_optional": "Optional[" in content,
        "has_tuple": "Tuple[" in content,
        "has_union": "Union[" in content,
        "needs_future_annotations": False,
        "deprecated_imports": [],
    }

    # Check imports
    if "from typing import" in content:
        typing_imports = re.findall(r"from typing import ([^\n+)", content), Optional, Union
        for imp in typing_imports:
            for old in ["List", "Dict", "Optional", "Tuple", "Union"]:
                if old in imp:
                    issues["deprecated_imports"].append(old)

    # Check if needs __future__ annotations
    if "|" in content and "from __future__ import annotations" not in content:
        # Has pipe syntax but no future import
        issues["needs_future_annotations"] = True

    issues["needs_fix"] = (
        issues["has_list"]
        or issues["has_dict"]
        or issues["has_optional"]
        or issues["has_tuple"]
        or issues["has_union"]
        or issues["deprecated_imports"]
    )

    return issues


def fix_file(file_path: Path) -> dict[str, Any]:
    """Fix typing issues in a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e), "success": False}

    original = content
    changes = []

    # Add __future__ import if needed
    if "|" in content and "from __future__ import annotations" not in content:
        # Check if it's a comment or string
        lines = content.split("\n")
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('"""') or line.startswith("'''"):
                # Find end of docstring
                if line.rstrip().endswith('"""') or line.rstrip().endswith("'''"):
                    import_idx = i + 1
                else:
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            import_idx = j + 1
                            break
            elif line.startswith("import ") or line.startswith("from "):
                import_idx = i
                break

        lines.insert(import_idx, "from __future__ import annotations\n")
        content = "\n".join(lines)
        changes.append("added_future_annotations")

    # Fix typing imports
    if "from typing import" in content:
        # Extract and clean up typing imports
        typing_imports = re.findall(r"from typing import ([^\n]+)", content), Optional, Union
        for imp in typing_imports:
            original_imp = imp
            new_imp = imp.replace("List, ", "").replace(", List", "").replace("List", "")
            new_imp = new_imp.replace("Dict, ", "").replace(", Dict", "").replace("Dict", "")
            new_imp = (
                new_imp.replace("Optional, ", "").replace(", Optional", "").replace("Optional", "")
            )
            new_imp = new_imp.replace("Tuple, ", "").replace(", Tuple", "").replace("Tuple", "")
            new_imp = new_imp.replace("Union, ", "").replace(", Union", "").replace("Union", "")
            new_imp = new_imp.strip()

            if new_imp and new_imp != original_imp:
                content = (
                    content.replace(
                        f"from typing import {original_imp}", f"from typing import {new_imp}"
                    ),
                    Optional,
                    Union,
                )
                changes.append(f"fixed_import: {original_imp} -> {new_imp}")
            elif not new_imp or new_imp == ",":
                # Remove empty typing import
                content = re.sub(r"from typing import[^\n]+\n", "", content)
                changes.append("removed_empty_typing_import")

    # Replace type patterns
    replacements = [
        (r"List\[([^\]]+)\]", r"list[\1]"),
        (r"Dict\[([^,]+), ([^\]]+)\]", r"dict[\1, \2]"),
        (r"Optional\[([^\]]+)\]", r"\1 | None"),
        (r"Tuple\[([^\]]+)\]", r"tuple[\1]"),
    ]

    for pattern, replacement in replacements:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            changes.append(f"replaced: {pattern}")

    # Verify syntax
    try:
        ast.parse(content)
        syntax_ok = True
    except SyntaxError as e:
        syntax_ok = False
        changes.append(f"syntax_error: {e}")

    # Write back if changed and valid
    if content != original and syntax_ok:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "changes": changes, "file": str(file_path)}
    elif not syntax_ok:
        return {
            "success": False,
            "error": "Syntax error after changes",
            "changes": changes,
            "file": str(file_path),
        }
    else:
        return {"success": True, "changes": [], "file": str(file_path)}


def main():
    """Main entry point."""
    print("🧠 AMOS Brain Typing Modernization System")
    print("=" * 60)

    # Target directories
    targets = ["repo_doctor", "repo_doctor_omega", "backend", "amos_brain", "clawspring"]

    all_files = []
    for target in targets:
        target_path = Path(__file__).parent / target
        if target_path.exists():
            files = find_python_files(str(target_path))
            all_files.extend(files)

    print(f"📁 Found {len(all_files)} Python files to analyze")

    # Analyze all files
    needs_fix = []
    for f in all_files:
        analysis = analyze_file(f)
        if analysis.get("needs_fix"):
            needs_fix.append((f, analysis))

    print(f"🔧 {len(needs_fix)} files need typing modernization")

    # Fix files
    fixed = 0
    errors = 0
    for file_path, analysis in needs_fix:
        result = fix_file(file_path)
        if result.get("success") and result.get("changes"):
            fixed += 1
            print(f"✅ {file_path.name}: {len(result['changes'])} changes")
        elif not result.get("success"):
            errors += 1
            print(f"❌ {file_path.name}: {result.get('error', 'Unknown error')}")

    print("=" * 60)
    print(f"🎉 Fixed: {fixed} files")
    print(f"⚠️ Errors: {errors} files")

    return fixed, errors


if __name__ == "__main__":
    main()
