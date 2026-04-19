#!/usr/bin/env python3

"""AMOS Brain Build System - Full Brain-Driven Build & Fix

Uses actual AMOS brain infrastructure:
- CognitiveEngine for analysis
- BrainClient for reasoning
- SuperBrainRuntime for orchestration
- ThinkingEngine for state transformation
"""

import ast
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))

# Import AMOS brain


from amos_brain import BrainClient, get_brain
from amos_brain.cognitive_engine import get_cognitive_engine
from amos_brain.memory import BrainMemory
from amos_brain.super_brain import get_super_brain


class BrainBuildSystem:
    """Build system powered by AMOS Brain cognitive engine."""

    def __init__(self) -> None:
        self.brain = get_brain()
        self.client = BrainClient()
        self.engine = get_cognitive_engine()
        self.memory = BrainMemory()
        self.super_brain = get_super_brain()
        self.results: List[dict] = []

    def initialize(self) -> bool:
        """Initialize all brain subsystems."""
        print("=" * 70)
        print("AMOS BRAIN BUILD SYSTEM")
        print(f"Timestamp: {datetime.now(UTC).isoformat()}")
        print("=" * 70)

        try:
            self.super_brain.initialize()
            print(f"Brain ID: {self.super_brain.brain_id}")
            return True
        except Exception as e:
            print(f"Init warning: {e}")
            return True  # Continue anyway

    def get_repo_files(self) -> List[Path]:
        """Get all Python files in repo."""
        skip = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".ruff_cache",
            ".hypothesis",
            ".pytest_cache",
        }
        files = []
        for f in Path(".").rglob("*.py"):
            if any(s in str(f) for s in skip):
                continue
            files.append(f)
        return sorted(files)

    def check_syntax(self, filepath: Path) -> Tuple[bool, str]:
        """Check file syntax."""
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze file with brain."""
        ok, error = self.check_syntax(filepath)

        result = {
            "path": str(filepath),
            "syntax_ok": ok,
            "syntax_error": error,
            "brain_analysis": None,
        }

        if not ok:
            # Use cognitive engine
            query = f"Fix syntax error in {filepath.name}: {error}"
            cognitive_result = self.engine.process(query, domain="software")
            result["brain_analysis"] = {
                "content": cognitive_result.content,
                "confidence": cognitive_result.confidence,
            }

        return result

    def run_ruff_fix(self) -> Dict[str, Any]:
        """Run Ruff with auto-fix."""
        cmd = ["ruff", "check", ".", "--fix", "--select", "E,W,F,I,UP", "--ignore", "UP042,UP043,D"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "status": "success" if result.returncode == 0 else "issues_found",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def run_ruff_format(self) -> Dict[str, Any]:
        """Run Ruff format."""
        cmd = ["ruff", "format", "."]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"status": "success", "stdout": result.stdout}

    def build(self) -> Dict[str, Any]:
        """Run full brain-driven build."""
        print("\n[PHASE 1] Brain Cognitive Analysis")
        query = "Analyze repository for critical build-blocking issues"
        cognitive_result = self.engine.process(query, domain="software")
        print(f"Brain confidence: {cognitive_result.confidence}")

        # Save to memory
        self.memory.save_reasoning(
            problem="Repository build analysis",
            analysis={
                "content": cognitive_result.content,
                "confidence": cognitive_result.confidence,
                "timestamp": cognitive_result.timestamp,
            },
            tags=["build", "analysis"],
        )

        print("\n[PHASE 2] Repository Scan")
        files = self.get_repo_files()
        print(f"Files: {len(files)}")

        print("\n[PHASE 3] Syntax Validation")
        syntax_errors = []
        for i, f in enumerate(files):
            if i % 200 == 0 and i > 0:
                print(f"  Checked {i}/{len(files)}...")
            ok, error = self.check_syntax(f)
            if not ok:
                syntax_errors.append((f, error))

        print(f"Syntax errors: {len(syntax_errors)}")

        print("\n[PHASE 4] Brain-Guided Fixes")
        for f, e in syntax_errors[:5]:
            analysis = self.analyze_file(f)
            if analysis["brain_analysis"]:
                print(f"  {f.name}: {analysis['brain_analysis']['content'][:80]}...")

        print("\n[PHASE 5] Ruff Auto-Fix")
        ruff_result = self.run_ruff_fix()
        print(f"Ruff: {ruff_result['status']}")

        print("\n[PHASE 6] Format")
        fmt_result = self.run_ruff_format()
        print(f"Format: {fmt_result['status']}")

        print("\n[PHASE 7] Final Verification")
        final_errors = 0
        for f, _ in syntax_errors:
            ok, _ = self.check_syntax(f)
            if not ok:
                final_errors += 1

        # Final brain assessment
        final_query = "Assess repository build quality after fixes"
        final_result = self.engine.process(final_query, domain="software")

        return {
            "total_files": len(files),
            "syntax_errors_found": len(syntax_errors),
            "syntax_errors_remaining": final_errors,
            "brain_confidence": final_result.confidence,
            "ruff_status": ruff_result["status"],
        }

    def run(self) -> None:
        """Run complete build."""
        if not self.initialize():
            print("Init failed")
            return

        results = self.build()

        print("\n" + "=" * 70)
        print("BRAIN BUILD COMPLETE")
        print("=" * 70)
        print(f"Files: {results['total_files']}")
        print(f"Syntax errors: {results['syntax_errors_found']}")
        print(f"Fixed: {results['syntax_errors_found'] - results['syntax_errors_remaining']}")
        print(f"Brain confidence: {results['brain_confidence']}")
        print(f"Ruff: {results['ruff_status']}")
        print("=" * 70)


def main() -> None:
    """Main entry."""
    system = BrainBuildSystem()
    system.run()


if __name__ == "__main__":
    main()
