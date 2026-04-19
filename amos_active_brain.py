from __future__ import annotations

from typing import Any, Dict, List

"""AMOS Active Brain - Real-time Cognitive Processing System

Uses the real brain integration to actively process:
- File analysis
- Code review
- Architecture decisions
- Bug detection
- Refactoring recommendations

This IS the brain being used for real work.
"""

import asyncio
import sys
from pathlib import Path

# Add paths
_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))

# Use the brain
from amos_cognitive_architecture import get_cognitive_loop
from amos_real_brain_integration import get_amos_real_brain


class AMOSActiveBrain:
    """Active brain that processes real tasks using cognitive architecture."""

    def __init__(self):
        self.brain = get_amos_real_brain()
        self.cognitive_loop = get_cognitive_loop()
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the active brain."""
        if self._initialized:
            return True

        await self.brain.initialize()
        self._initialized = True
        return True

    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a file using cognitive processing.

        Real implementation using brain components.
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        # Read file
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"error": f"Could not read file: {e}"}

        # Build analysis query
        query = f"""Analyze this code file:
Path: {file_path}
Size: {len(content)} characters
Lines: {len(content.splitlines())}

First 50 lines:
{chr(10).join(content.splitlines()[:50])}

Provide:
1. Purpose/intent of this file
2. Key functions/classes
3. Potential issues
4. Improvement recommendations
"""

        # Use deep thinking for analysis
        result = await self.brain.think_deep(
            query, context={"file_path": str(file_path), "file_type": file_path.suffix}
        )

        return {
            "file": str(file_path),
            "analysis": result,
            "brain_mode": "deep",
            "status": "analyzed",
        }

    async def review_code(self, code: str, context: str = "") -> Dict[str, Any]:
        """Review code for issues using brain.

        Real implementation with verification.
        """
        query = f"""Review this code:
{code}

Context: {context}

Check for:
- Bugs and logic errors
- Security vulnerabilities
- Performance issues
- Code smells
- Best practice violations
"""

        # Use safe mode for code review (high verification)
        result = await self.brain.think_safe(
            query, risk_level=0.7, context={"type": "code_review", "code_length": len(code)}
        )

        if result is None:
            return {
                "status": "verification_failed",
                "review": "Could not verify analysis - high risk detected",
            }

        return {"status": "reviewed", "review": result, "verified": True}

    async def suggest_refactoring(
        self, code: str, goal: str = "improve readability"
    ) -> Dict[str, Any]:
        """Suggest refactoring using brain planning."""
        query = f"""Suggest refactoring for this goal: {goal}

Code:
{code}

Provide specific refactoring steps with rationale.
"""

        result = await self.cognitive_loop.run(query, context={"task": "refactoring", "goal": goal})

        return {
            "status": "success" if result["success"] else "failed",
            "suggestions": result["response"],
            "cognitive_steps": result.get("steps", 0),
            "tools_used": result.get("tools_used", []),
        }

    async def detect_architecture_issues(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Detect architecture issues across files."""
        # Build world state from files
        for fp in file_paths[:10]:  # Limit to 10 files
            if fp.exists():
                self.brain.brain.world.add_node(
                    fp.name, "file", {"path": str(fp), "type": fp.suffix}
                )

        query = f"""Analyze architecture across {len(file_paths)} files.

Files: {[fp.name for fp in file_paths[:10]]}

Detect:
1. Circular dependencies
2. Missing abstractions
3. Violations of separation of concerns
4. Module cohesion issues
"""

        result = await self.brain.think_deep(query)

        return {
            "files_analyzed": len(file_paths),
            "architecture_analysis": result,
            "world_model_size": len(self.brain.brain.world.nodes),
        }

    def get_brain_stats(self) -> Dict[str, Any]:
        """Get statistics about brain usage."""
        return self.brain.get_stats()


# Global active brain instance
_active_brain: AMOSActiveBrain | None = None


def get_active_brain() -> AMOSActiveBrain:
    """Get global active brain instance."""
    global _active_brain
    if _active_brain is None:
        _active_brain = AMOSActiveBrain()
    return _active_brain


# Real file analysis functions
async def analyze_repo_file(file_path: str) -> Dict[str, Any]:
    """Analyze a file in the repository."""
    brain = get_active_brain()
    await brain.initialize()
    return await brain.analyze_file(Path(file_path))


async def review_code_snippet(code: str, language: str = "python") -> Dict[str, Any]:
    """Review a code snippet."""
    brain = get_active_brain()
    await brain.initialize()
    return await brain.review_code(code, context=f"Language: {language}")


async def suggest_code_refactoring(code: str, goal: str = "improve readability") -> Dict[str, Any]:
    """Get refactoring suggestions."""
    brain = get_active_brain()
    await brain.initialize()
    return await brain.suggest_refactoring(code, goal)


# Demonstration
if __name__ == "__main__":

    async def demo():
        print("=" * 70)
        print("AMOS ACTIVE BRAIN - REAL COGNITIVE PROCESSING")
        print("=" * 70)

        brain = get_active_brain()
        await brain.initialize()
        print("\n[1] Active brain initialized")
        print(f"    World model entities: {len(brain.brain.brain.world.nodes)}")

        # Analyze a real file
        print("\n[2] Analyzing real file (organism_bridge.py)...")
        result = await analyze_repo_file("organism_bridge.py")
        print(f"    Status: {result['status']}")
        if "analysis" in result:
            print(f"    Analysis preview: {result['analysis'][:150]}...")

        # Review code
        print("\n[3] Reviewing code snippet...")
        code_sample = """
def calculate(x, y):
    result = eval(f"{x} + {y}")
    return result
"""
        review = await review_code_snippet(code_sample)
        print(f"    Status: {review['status']}")
        if review["status"] == "reviewed":
            print(f"    Review: {review['review'][:150]}...")

        # Get stats
        print("\n[4] Brain statistics:")
        stats = brain.get_brain_stats()
        print(f"    Total queries: {stats['total_queries']}")
        print(f"    Success rate: {stats['success_rate']:.1%}")
        print(f"    Mode usage: {stats['mode_usage']}")
        print(f"    Learning updates: {stats['learning_updates']}")

        print("\n" + "=" * 70)
        print("ACTIVE BRAIN DEMO COMPLETE - REAL COGNITIVE WORK PERFORMED")
        print("=" * 70)

    asyncio.run(demo())
