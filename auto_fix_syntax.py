#!/usr/bin/env python3
"""Auto-fix syntax errors - removes misplaced typing imports."""

import ast
import re
from pathlib import Path

# Files to fix with their problematic patterns
FILES_TO_FIX = [
    ("amos_translation_layer.py", 2178),
    ("amos_event_streaming_platform.py", 27),
    ("amos_equation_cli.py", 42),
    ("test_organism_subsystems.py", 31),
    ("amos_code_analyzer.py", 216),
    ("amos_error_handling.py", 70),
    ("amos_ultra_low_latency_runtime.py", 1089),
    ("amos_service_mesh.py", 788),
    ("start_math_dashboard.py", 128),
    ("fix_all_python39.py", 13),
    ("amos_equation_api.py", 362),
    ("amos_v4_runtime.py", 608),
    ("amos_operational.py", 171),
    ("equation_knowledge_manager.py", 319),
    ("amos_equation_verifier.py", 567),
    ("brain_f821_fix.py", 15),
    ("amos_fastloop_classifier.py", 217),
    ("amos_github_connector.py", 326),
    ("amos_local.py", 37),
    ("amos_unified_api.py", 559),
    ("amos_event_bus.py", 12),
    ("fix_imports.py", 20),
    ("amos_cognitive_file_processor.py", 46),
    ("amos_equation_massive.py", 223),
    ("amos_superbrain_api.py", 548),
    ("amos_api_integration.py", 65),
    ("amos_cognitive_runtime.py", 952),
    ("amos_cognitive_bridge.py", 505),
    ("equation_docs.py", 886),
    ("admin_api.py", 31),
]


def fix_file(filepath: Path) -> bool:
    """Fix common syntax errors in a file."""
    try:
        with open(filepath) as f:
            content = f.read()

        # Pattern 1: Misplaced typing import after indented code
        # Matches: "    code\nfrom typing import X\n    more code"
        pattern1 = r"(\n[ \t]+.*\n)from typing import[^\n]+(\n[ \t]+)"
        content = re.sub(pattern1, r"\1\2", content)

        # Pattern 2: Misplaced import at wrong indentation level
        lines = content.split("\n")
        fixed_lines = []
        prev_indent = 0

        for i, line in enumerate(lines):
            if line.strip().startswith("from typing import") or line.strip().startswith(
                "import typing"
            ):
                # Check if this line has wrong indentation
                curr_indent = len(line) - len(line.lstrip())
                if curr_indent == 0 and prev_indent > 0:
                    # Skip this line - it's a misplaced import
                    continue

            fixed_lines.append(line)
            if line.strip():
                prev_indent = len(line) - len(line.lstrip())

        content = "\n".join(fixed_lines)

        # Verify syntax is now valid
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"  Could not fix {filepath}: {e}")
            return False

        # Write fixed content
        with open(filepath, "w") as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"  Error processing {filepath}: {e}")
        return False


def main():
    """Fix all syntax errors."""
    repo_root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    fixed_count = 0
    for filename, _ in FILES_TO_FIX:
        filepath = repo_root / filename
        if filepath.exists():
            print(f"Fixing {filename}...")
            if fix_file(filepath):
                fixed_count += 1
                print("  ✓ Fixed")
            else:
                print("  ✗ Failed")
        else:
            print(f"  ✗ Not found: {filename}")

    print(f"\nFixed {fixed_count}/{len(FILES_TO_FIX)} files")


if __name__ == "__main__":
    main()
