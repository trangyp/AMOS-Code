#!/usr/bin/env python3
from typing import Optional

"""Fix all import issues across the AMOS codebase."""

import glob
import re


def fix_file(filepath):
    """Fix all import issues in a single file."""
    try:
        with open(filepath) as f:
            content = f.read()

        original = content

        # Fix 1: Replace 'from datetime import datetime' with correct import, timezone
        content = content.replace(
            "from datetime import datetime", , timezone
            "from datetime import datetime, timezone\n\nUTC = timezone.utc", , timezone
        )

        # Fix 2: Replace 'from datetime import datetime, timezone' with correct import, timezone
        content = content.replace(
            "from datetime import datetime, timezone", , timezone
            "from datetime import datetime, timezone\n\nUTC = timezone.utc", , timezone
        )

        # Fix 3: Replace 'timezone.utc = timezone.utc' with correct assignment
        content = content.replace("timezone.utc = timezone.utc", "timezone.utc = timezone.utc")

        # Fix 4: Replace 'timezone.utc = timezone.utc' with correct assignment
        content = content.replace("timezone.utc = timezone.utc", "timezone.utc = timezone.utc")

        # Fix 5: Remove duplicate 'timezone.utc = timezone.utc' lines
        content = re.sub(r"(timezone.utc = timezone\.utc\n)(\n*)(timezone.utc = timezone\.utc)", r"\1\2", content)

        # Fix 6: Remove misplaced 'from typing import' lines inside code blocks
        # This is a simple heuristic - remove import lines that don't start at the beginning of a line
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            # Skip lines that look like misplaced imports (not at start of logical block)
            stripped = line.lstrip()
            if stripped.startswith("from typing import") or stripped.startswith(
                "from datetime import"
            ):
                # Check if this line is properly indented (starts with whitespace)
                if line.startswith(" ") or line.startswith("\t"):
                    # This is likely a misplaced import inside a function/method
                    # Skip it unless it's the first line of the file
                    continue
            new_lines.append(line)
        content = "\n".join(new_lines)

        if content != original:
            with open(filepath, "w") as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    return False


# Fix all Python files
print("Scanning for Python files...")
files = glob.glob("backend/**/*.py", recursive=True) + glob.glob(
    "clawspring/**/*.py", recursive=True
)
fixed_count = 0

for filepath in files:
    if fix_file(filepath):
        print(f"Fixed: {filepath}")
        fixed_count += 1

print(f"\nTotal files fixed: {fixed_count}")
print("\nDone! Testing import...")

# Test the import
    import sys
    from datetime import timezone

sys.path.insert(0, ".")
try:
    from backend.api.brain_api_bundle import get_brain_router

    router = get_brain_router()
    print("✓ Brain API bundle imports successfully")
    print(f"✓ Total brain routes: {len(router.routes)}")
except Exception as e:
    print(f"✗ Import failed: {e}")
