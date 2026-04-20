#!/usr/bin/env python3
"""Batch fix remaining sys.path.insert files."""

import re
from pathlib import Path

# Files to fix (from grep search)
FILES_TO_FIX = [
    "amos_api.py",
    "amos_api_hub.py",
    "amos_brain/__main__.py",
    "amos_brain/tools.py",
    "amos_brain_cli_legacy.py",
    "amos_brain_launcher.py",
    "amos_brain_tutorial.py",
    "amos_clawspring.py",
    "amos_execution_mcp_server.py",
    "amos_mcp_server.py",
    "backend/tests/conftest.py",
    "clawspring/agent.py",
    "clawspring/amos_plugin.py",
    "clawspring/tests/test_compaction.py",
    "clawspring/tests/test_diff_view.py",
    "debug_integration_example.py",
    "examples/hello_biological.py",
    "examples/hello_classical.py",
    "examples/hello_hybrid.py",
    "examples/hello_quantum.py",
    "tests/test_amos_brain.py",
    "tests/test_full_integration.py",
    "tests/test_integration.py",
    "tests/test_model_backends.py",
    "tests/test_orchestrator_integration.py",
    "tests/test_spec_hierarchy.py",
]


def fix_file(filepath: Path) -> tuple[bool, str]:
    """Fix a single file by removing sys.path.insert lines."""
    try:
        content = filepath.read_text()
        original = content

        # Pattern to match sys.path.insert with os.path patterns
        pattern = r"\n?#.*\n?sys\.path\.insert\(0,\s*os\.path\.[^)]+\)\n?"

        # Remove the sys.path.insert lines
        content = re.sub(pattern, "\n", content)

        # Clean up multiple consecutive blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        if content != original:
            filepath.write_text(content)
            return True, "Fixed"
        return False, "No changes needed"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    base_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    fixed = 0
    errors = []

    for file_path in FILES_TO_FIX:
        full_path = base_path / file_path
        if full_path.exists():
            was_fixed, msg = fix_file(full_path)
            if was_fixed:
                fixed += 1
                print(f"✓ Fixed: {file_path}")
            elif "Error" in msg:
                errors.append(f"✗ {file_path}: {msg}")
            else:
                print(f"- {file_path}: {msg}")
        else:
            errors.append(f"✗ {file_path}: File not found")

    print(f"\n{'=' * 60}")
    print(f"Batch Fix Complete: {fixed} files fixed")
    if errors:
        print(f"Errors ({len(errors)}):")
        for err in errors[:10]:
            print(f"  {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")


if __name__ == "__main__":
    main()
