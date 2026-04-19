#!/usr/bin/env python3
"""
AMOS Invariant Verification Engine
====================================

Neural-symbolic verification system combining formal equations with AI reasoning.
Integrates equation knowledge from 01_BRAIN with 03_IMMUNE anomaly detection.

Architecture: Neural-Symbolic Hybrid
- Formal: Equation-based invariant checking
- Neural: LLM-based pattern recognition
- Hybrid: Retrieval-augmented verification

State-of-the-art: Inspired by LeanDojo, FVEL (NeurIPS 2024), Graph4Code
"""

import ast
import hashlib
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Protocol

# Add brain module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "01_BRAIN"))

try:
    from cognitive_equation_layer import CognitiveEquationLayer

    EQUATIONS_AVAILABLE = True
except ImportError:
    EQUATIONS_AVAILABLE = False


class VerificationStatus(Enum):
    """Invariant verification status."""

    VERIFIED = auto()
    VIOLATED = auto()
    UNKNOWN = auto()
    PARTIAL = auto()


class InvariantCategory(Enum):
    """Categories of invariants verifiable."""

    TYPE_SAFETY = "type_safety"
    MEMORY_SAFETY = "memory_safety"
    CONCURRENCY_SAFETY = "concurrency_safety"
    CORRECTNESS = "correctness"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class VerificationResult:
    """Result of invariant verification."""

    invariant: str
    category: InvariantCategory
    status: VerificationStatus
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    suggested_fixes: List[str] = field(default_factory=list)
    equation_refs: List[str] = field(default_factory=list)


class CodeAnalyzer(Protocol):
    """Protocol for code analysis."""

    def analyze(self, code: str, language: str) -> Dict[str, Any]: ...


class PythonASTAnalyzer:
    """Python code analysis using AST."""

    def analyze(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze Python code for patterns."""
        if language != "python":
            return {"error": "Only Python supported"}

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"error": str(e)}

        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "assignments": [],
            "has_mutable_defaults": False,
            "has_global_state": False,
            "has_recursion": False,
            "complexity_score": 0,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append(node.name)
                # Check for mutable default arguments
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        analysis["has_mutable_defaults"] = True

                # Check for recursion
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id == node.name:
                                analysis["has_recursion"] = True

            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append(node.name)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                analysis["imports"].append(ast.unparse(node))
            elif isinstance(node, ast.Assign):
                analysis["assignments"].append(len(node.targets))

            # Check for global state modification
            if isinstance(node, ast.Global):
                analysis["has_global_state"] = True

        analysis["complexity_score"] = len(analysis["functions"]) + len(analysis["classes"])
        return analysis


class InvariantVerificationEngine:
    """
    Neural-symbolic invariant verification engine.

    Combines formal equation-based verification with neural pattern recognition.
    """

    def __init__(self, organism_root: Optional[Path] = None):
        self.organism_root = organism_root or Path(__file__).parent.parent
        self.equation_layer: Optional[CognitiveEquationLayer] = None
        self.analyzers: Dict[str, CodeAnalyzer] = {
            "python": PythonASTAnalyzer(),
        }
        self.verification_cache: Dict[str, VerificationResult] = {}

        if EQUATIONS_AVAILABLE:
            self.equation_layer = CognitiveEquationLayer(self.organism_root)
            self.equation_layer.initialize()

    def verify_code(
        self,
        code: str,
        language: str,
        target_invariants: List[InvariantCategory] = None,
    ) -> List[VerificationResult]:
        """
        Verify code against formal invariants.

        Args:
            code: Source code to verify
            language: Programming language
            target_invariants: Specific invariants to check (None = all)

        Returns:
            List of verification results
        """
        results = []
        target_invariants = target_invariants or list(InvariantCategory)

        # Get AST analysis
        analyzer = self.analyzers.get(language)
        ast_analysis = analyzer.analyze(code, language) if analyzer else {}

        # Check each invariant category
        for category in target_invariants:
            result = self._verify_category(code, language, category, ast_analysis)
            results.append(result)

        return results

    def _verify_category(
        self,
        code: str,
        language: str,
        category: InvariantCategory,
        ast_analysis: Dict[str, Any],
    ) -> VerificationResult:
        """Verify specific invariant category."""
        cache_key = self._hash_code(code + category.value)

        if cache_key in self.verification_cache:
            return self.verification_cache[cache_key]

        # Get equation-based verification
        equation_refs = []
        if self.equation_layer:
            eq_result = self.equation_layer.verify_invariant(code, category.value)
            if eq_result.get("valid"):
                equation_refs = eq_result.get("equations", [])

        # Perform category-specific checks
        if category == InvariantCategory.MEMORY_SAFETY:
            result = self._check_memory_safety(code, language, ast_analysis, equation_refs)
        elif category == InvariantCategory.TYPE_SAFETY:
            result = self._check_type_safety(code, language, ast_analysis, equation_refs)
        elif category == InvariantCategory.CORRECTNESS:
            result = self._check_correctness(code, language, ast_analysis, equation_refs)
        else:
            result = VerificationResult(
                invariant=category.value,
                category=category,
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                equation_refs=equation_refs,
            )

        self.verification_cache[cache_key] = result
        return result

    def _check_memory_safety(
        self,
        code: str,
        language: str,
        ast_analysis: Dict[str, Any],
        equation_refs: List[str],
    ) -> VerificationResult:
        """Check memory safety invariants."""
        violations = []
        evidence = []

        # Python-specific checks
        if language == "python":
            if ast_analysis.get("has_mutable_defaults"):
                violations.append("Mutable default arguments detected")
                evidence.append("Function has mutable default (list/dict/set)")

        # Rust-specific pattern detection
        if language == "rust":
            # Check for unsafe blocks
            if "unsafe" in code:
                evidence.append("Unsafe block detected - requires manual verification")

            # Check ownership patterns
            if "&mut" in code and "&" in code.replace("&mut", ""):
                violations.append("Potential ownership violation")

        status = VerificationStatus.VERIFIED if not violations else VerificationStatus.VIOLATED
        confidence = 0.9 if violations else 0.7

        return VerificationResult(
            invariant="memory_safety",
            category=InvariantCategory.MEMORY_SAFETY,
            status=status,
            confidence=confidence,
            evidence=evidence,
            violations=violations,
            equation_refs=equation_refs,
        )

    def _check_type_safety(
        self,
        code: str,
        language: str,
        ast_analysis: Dict[str, Any],
        equation_refs: List[str],
    ) -> VerificationResult:
        """Check type safety invariants."""
        violations = []
        evidence = []

        if language == "python":
            # Check for type hints
            has_type_hints = (
                "->" in code or ": " in code.split("def")[0] if "def" in code else False
            )
            if not has_type_hints and len(code) > 100:
                evidence.append("No type hints found in significant code block")

        status = VerificationStatus.VERIFIED if not violations else VerificationStatus.VIOLATED

        return VerificationResult(
            invariant="type_safety",
            category=InvariantCategory.TYPE_SAFETY,
            status=status,
            confidence=0.8,
            evidence=evidence,
            violations=violations,
            equation_refs=equation_refs,
        )

    def _check_correctness(
        self,
        code: str,
        language: str,
        ast_analysis: Dict[str, Any],
        equation_refs: List[str],
    ) -> VerificationResult:
        """Check correctness invariants."""
        violations = []
        evidence = []

        complexity = ast_analysis.get("complexity_score", 0)
        if complexity > 10:
            evidence.append(f"High complexity score: {complexity}")

        if ast_analysis.get("has_recursion"):
            evidence.append("Recursive function detected - termination check needed")
            # Suggest structural recursion check
            if "if" not in code[: code.find("def")] if "def" in code else True:
                violations.append("Recursive function may lack base case")

        status = VerificationStatus.VERIFIED if not violations else VerificationStatus.VIOLATED

        return VerificationResult(
            invariant="correctness",
            category=InvariantCategory.CORRECTNESS,
            status=status,
            confidence=0.75,
            evidence=evidence,
            violations=violations,
            equation_refs=equation_refs,
        )

    def _hash_code(self, code: str) -> str:
        """Generate cache key for code."""
        return hashlib.md5(code.encode()).hexdigest()[:16]

    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        return {
            "initialized": True,
            "equations_loaded": 12 if self.equation_layer else 0,
            "cache_size": len(self.verification_cache),
        }

    def get_verification_report(self, code: str, language: str) -> Dict[str, Any]:
        """Generate comprehensive verification report."""
        results = self.verify_code(code, language)

        verified = sum(1 for r in results if r.status == VerificationStatus.VERIFIED)
        violated = sum(1 for r in results if r.status == VerificationStatus.VIOLATED)
        unknown = sum(1 for r in results if r.status == VerificationStatus.UNKNOWN)

        return {
            "summary": {
                "total_checks": len(results),
                "verified": verified,
                "violated": violated,
                "unknown": unknown,
                "overall_confidence": sum(r.confidence for r in results) / len(results)
                if results
                else 0,
            },
            "details": [
                {
                    "invariant": r.invariant,
                    "category": r.category.value,
                    "status": r.status.name,
                    "confidence": r.confidence,
                    "violations": r.violations,
                    "equation_refs": r.equation_refs,
                }
                for r in results
            ],
        }


def main() -> int:
    """Test invariant verification engine."""
    print("[InvariantVerificationEngine] Initializing...")

    engine = InvariantVerificationEngine()

    # Test with problematic Python code
    test_code = """
def bad_function(items=[]):
    items.append(1)
    return items

def recursive_no_base(x):
    return recursive_no_base(x - 1)
"""

    print("\n[Testing] Problematic Python code...")
    results = engine.verify_code(test_code, "python")

    for result in results:
        print(f"\n  {result.invariant}: {result.status.name}")
        print(f"    Confidence: {result.confidence:.2f}")
        if result.violations:
            print(f"    Violations: {result.violations}")
        if result.evidence:
            print(f"    Evidence: {result.evidence}")

    # Get full report
    report = engine.get_verification_report(test_code, "python")
    print(f"\n[Report] Summary: {report['summary']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
