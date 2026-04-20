#!/usr/bin/env python3

from typing import Any

"""AMOS Brain Repository System - Full Brain Integration

Uses actual AMOS brain components:
- BrainClient for cognitive processing
- SuperBrainRuntime for system orchestration
- ThinkingEngine for state transformation
"""

import ast
import subprocess
import sys
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from pathlib import Path

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

# Import actual AMOS brain components


from amos_brain import BrainResponse, GlobalLaws
from amos_brain.facade import BrainClient
from amos_brain.super_brain import get_super_brain
from amos_brain.thinking_engine import ThinkingEngine


class BrainRepositorySystem:
    """Repository analysis and fix system powered by AMOS Brain."""

    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = Path(repo_path).resolve()
        self.brain = BrainClient(repo_path=str(self.repo_path))
        self.super_brain = get_super_brain()
        self.thinking_engine = ThinkingEngine()
        self.laws = GlobalLaws()
        self.results: list[dict] = []

    def initialize(self) -> bool:
        """Initialize the brain system."""
        print(f"{'=' * 70}")
        print("AMOS BRAIN: Repository System Initializing")
        print(
            f"Brain ID: {self.super_brain.brain_id if hasattr(self.super_brain, 'brain_id') else 'active'}"
        )
        print(f"Repository: {self.repo_path}")
        print(f"Timestamp: {datetime.now(UTC).isoformat()}")
        print(f"{'=' * 70}")

        # Initialize super brain
        try:
            self.super_brain.initialize()
            print("✅ SuperBrain Runtime: ACTIVE")
            return True
        except Exception as e:
            print(f"⚠️ SuperBrain init: {e}")
            return False

    def get_all_python_files(self) -> list[Path]:
        """Get all Python files using brain-guided search."""
        files = []
        skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".ruff_cache"}

        for path in self.repo_path.rglob("*.py"):
            if any(s in str(path) for s in skip_dirs):
                continue
            files.append(path)

        return sorted(files)

    def check_file_syntax(self, filepath: Path) -> tuple[bool, str]:
        """Check Python file syntax."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def analyze_with_brain(self, filepath: Path) -> dict[str, Any]:
        """Use brain to analyze a file."""
        # Check syntax first
        ok, error = self.check_file_syntax(filepath)

        result = {
            "path": str(filepath),
            "syntax_ok": ok,
            "syntax_error": error,
            "brain_analysis": None,
        }

        if not ok:
            # Use brain to think about the error
            query = f"Fix syntax error in {filepath.name}: {error}"
            brain_result = self.brain.think(query, domain="software")
            result["brain_analysis"] = {
                "content": brain_result.content,
                "confidence": brain_result.confidence,
                "law_compliant": brain_result.law_compliant,
            }

        return result

    def run_ruff_fix(self, files: list[Path]) -> dict[str, Any]:
        """Run Ruff linter with auto-fix."""
        if not files:
            return {"status": "no_files"}

        # Run ruff check --fix
        cmd = [
            "ruff",
            "check",
            str(self.repo_path),
            "--fix",
            "--select",
            "E,W,F,I,UP",
            "--ignore",
            "UP042,UP043,D",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return {
            "status": "success" if result.returncode == 0 else "issues_found",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def run_ruff_format(self) -> dict[str, Any]:
        """Run Ruff formatter."""
        cmd = ["ruff", "format", str(self.repo_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}

    def process_repository(self) -> dict[str, Any]:
        """Main processing loop using brain."""
        print("\n[PHASE 1] Brain-guided repository scan...")
        files = self.get_all_python_files()
        print(f"      Found {len(files)} Python files")

        print("\n[PHASE 2] Syntax validation...")
        syntax_errors = []
        for i, filepath in enumerate(files):
            if i % 100 == 0 and i > 0:
                print(f"      Checked {i}/{len(files)}...")

            ok, error = self.check_file_syntax(filepath)
            if not ok:
                syntax_errors.append((filepath, error))

        print(f"      Syntax errors found: {len(syntax_errors)}")

        print("\n[PHASE 3] Brain analysis of errors...")
        for filepath, error in syntax_errors[:5]:  # Analyze first 5
            analysis = self.analyze_with_brain(filepath)
            if analysis["brain_analysis"]:
                print(f"      {filepath.name}: {analysis['brain_analysis']['content'][:100]}...")

        print("\n[PHASE 4] Ruff auto-fix...")
        ruff_result = self.run_ruff_fix(files)
        print(f"      Ruff status: {ruff_result['status']}")

        print("\n[PHASE 5] Ruff format...")
        format_result = self.run_ruff_format()
        print(f"      Format status: {format_result['status']}")

        # Final verification
        print("\n[PHASE 6] Final verification...")
        remaining_errors = 0
        for filepath, _ in syntax_errors:
            ok, _ = self.check_file_syntax(filepath)
            if not ok:
                remaining_errors += 1

        return {
            "total_files": len(files),
            "syntax_errors_found": len(syntax_errors),
            "syntax_errors_remaining": remaining_errors,
            "ruff_status": ruff_result["status"],
        }

    def think_about_results(self, results: dict) -> BrainResponse:
        """Use brain to analyze the results."""
        query = f"""Repository fix results:
        - Total files: {results["total_files"]}
        - Syntax errors found: {results["syntax_errors_found"]}
        - Syntax errors remaining: {results["syntax_errors_remaining"]}
        - Ruff status: {results["ruff_status"]}

        What does this indicate about code quality?"""

        return self.brain.think(query, domain="software")

    def run(self) -> None:
        """Run the complete brain-powered repository fix."""
        # Initialize
        if not self.initialize():
            print("❌ Failed to initialize brain system")
            return

        # Process repository
        results = self.process_repository()

        # Think about results
        print("\n[PHASE 7] Brain analysis of results...")
        brain_analysis = self.think_about_results(results)
        print(f"      Brain says: {brain_analysis.content[:200]}...")

        # Summary
        print(f"\n{'=' * 70}")
        print("AMOS BRAIN: Repository Fix Complete")
        print(f"{'=' * 70}")
        print(f"Total files: {results['total_files']}")
        print(f"Syntax errors found: {results['syntax_errors_found']}")
        print(
            f"Syntax errors fixed: {results['syntax_errors_found'] - results['syntax_errors_remaining']}"
        )
        print(f"Brain confidence: {brain_analysis.confidence}")
        print(f"Law compliant: {brain_analysis.law_compliant}")
        print(f"Timestamp: {datetime.now(UTC).isoformat()}")
        print(f"{'=' * 70}")


def main() -> None:
    """Main entry point."""
    system = BrainRepositorySystem()
    system.run()


if __name__ == "__main__":
    main()
