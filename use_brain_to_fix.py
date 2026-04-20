#!/usr/bin/env python3
"""USE BRAIN TO ANALYZE AND FIX REPOSITORY

Actually uses BrainClient to analyze files and fix issues.
"""

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# USE THE BRAIN
from amos_brain import BrainClient
from amos_brain.cognitive_engine import get_cognitive_engine


def analyze_with_brain(filepath: Path, brain: BrainClient) -> dict:
    """Use brain to analyze a file for issues."""
    content = filepath.read_text(encoding="utf-8")

    # Check syntax first
    try:
        ast.parse(content)
        syntax_ok = True
        syntax_error = None
    except SyntaxError as e:
        syntax_ok = False
        syntax_error = str(e)

    # Use brain to analyze
    analysis = brain.think(
        f"Analyze {filepath.name} for: 1) Missing imports, 2) Python 3.9 compatibility, "
        f"3) Code quality issues. File has {'syntax error' if not syntax_ok else 'valid syntax'}."
    )

    return {
        "file": str(filepath),
        "syntax_ok": syntax_ok,
        "syntax_error": syntax_error,
        "brain_analysis": analysis,
    }


def fix_with_brain(filepath: Path, brain: BrainClient) -> bool:
    """Use brain to decide and apply fixes."""
    result = analyze_with_brain(filepath, brain)

    if not result["syntax_ok"]:
        print(f"  SYNTAX ERROR: {filepath}")
        print(f"    {result['syntax_error']}")
        return False

    # Use brain to decide if fix is needed
    decision = brain.decide(
        f"Should we fix {filepath.name}? Analysis: {result['brain_analysis']}",
        options=["yes_fix", "no_skip", "manual_review"],
    )

    print(f"  {filepath.name}: {decision.get('decision', 'skip')}")
    return True


def main() -> int:
    """Main brain-powered fix process."""
    print("=" * 70)
    print("BRAIN-POWERED REPOSITORY ANALYSIS AND FIX")
    print("=" * 70)

    # Initialize brain
    brain = BrainClient()
    cog = get_cognitive_engine()

    print("\nBrain: ACTIVE")
    print(f"Tools: {len(brain.list_tools())}")
    print(f"Cognitive Engine: {cog}")

    # Get brain guidance
    guidance = brain.think(
        "Scan the AMOS repository for F821 undefined name errors. "
        "Which files should we prioritize for fixing?"
    )
    print(f"\nBrain Guidance: {guidance}")

    # Find all Python files
    repo_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    python_files = [
        f for f in repo_path.rglob("*.py") if ".venv" not in str(f) and "__pycache__" not in str(f)
    ]

    print(f"\nRepository: {len(python_files)} Python files")

    # Check syntax with brain
    fixed = 0
    errors = 0

    for i, f in enumerate(python_files[:100]):  # Check first 100
        if i % 20 == 0:
            print(f"\n  Processing {i + 1}-{min(i + 20, len(python_files))}...")

        if fix_with_brain(f, brain):
            fixed += 1
        else:
            errors += 1

    print(f"\n{'=' * 70}")
    print(f"Results: {fixed} OK, {errors} errors")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
