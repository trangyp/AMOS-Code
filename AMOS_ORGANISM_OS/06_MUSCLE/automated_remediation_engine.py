#!/usr/bin/env python3
"""
AMOS Automated Remediation Engine
====================================

Self-healing code repair system combining formal verification with AI generation.
Closes the loop: Detect → Analyze → Generate → Validate → Execute

Architecture: Agentic Remediation Pipeline
- Detection: Invariant violations from 03_IMMUNE
- Analysis: Root cause via equation knowledge (01_BRAIN)
- Generation: Fix proposals using formal constraints
- Validation: Re-verification before application
- Execution: Safe deployment via 06_MUSCLE

State-of-the-art: Inspired by agentic security platforms, self-healing systems research
"""

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

try:
    from AMOS_ORGANISM_OS.BRAIN.cognitive_equation_layer import CognitiveEquationLayer
    from AMOS_ORGANISM_OS.BRAIN.equation_knowledge_bridge import EquationEntry

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False

try:
    from invariant_verification_engine import (
        InvariantCategory,
        InvariantVerificationEngine,
        VerificationResult,
    )

    IMMUNE_AVAILABLE = True
except ImportError:
    IMMUNE_AVAILABLE = False


class RemediationStatus(Enum):
    """Status of remediation attempt."""

    DETECTED = auto()
    ANALYZING = auto()
    GENERATING = auto()
    VALIDATING = auto()
    APPLIED = auto()
    FAILED = auto()
    ROLLED_BACK = auto()


class FixType(Enum):
    """Types of automated fixes."""

    TYPE_HINT = "add_type_annotation"
    NONE_CHECK = "add_null_check"
    MUTABLE_DEFAULT = "fix_mutable_default"
    RECURSION_GUARD = "add_recursion_base_case"
    IMPORT_ADD = "add_missing_import"
    BOUND_CHECK = "add_bounds_check"


@dataclass
class FixProposal:
    """Proposed fix for a code issue."""

    fix_type: FixType
    description: str
    original_code: str
    proposed_code: str
    confidence: float
    equation_refs: list[str] = field(default_factory=list)
    validation_passed: bool = False


@dataclass
class RemediationRecord:
    """Record of a remediation attempt."""

    id: str
    timestamp: str
    original_code: str
    language: str
    violations: list[VerificationResult]
    fixes: list[FixProposal]
    status: RemediationStatus
    applied_fix: FixProposal = None
    error_message: str = None


class CodeFixGenerator:
    """Generates fixes based on violation type and equation knowledge."""

    def __init__(self, equation_layer: CognitiveEquationLayer = None):
        self.equation_layer = equation_layer

    def generate_fix(
        self,
        violation: VerificationResult,
        code_context: str,
        language: str,
    ) -> FixProposal:
        """Generate appropriate fix for violation."""
        if violation.category == InvariantCategory.MEMORY_SAFETY:
            return self._fix_memory_safety(violation, code_context, language)
        elif violation.category == InvariantCategory.TYPE_SAFETY:
            return self._fix_type_safety(violation, code_context, language)
        elif violation.category == InvariantCategory.CORRECTNESS:
            return self._fix_correctness(violation, code_context, language)
        return None

    def _fix_memory_safety(
        self,
        violation: VerificationResult,
        code: str,
        language: str,
    ) -> FixProposal:
        """Generate memory safety fix."""
        # Python: Fix mutable default arguments
        if language == "python" and "mutable default" in str(violation.violations):
            # Find function with mutable default
            match = re.search(
                r"def\s+(\w+)\s*\([^)]*=\s*(\[|{)",
                code,
            )
            if match:
                func_name = match.group(1)
                # Generate fix: use None as default
                original = match.group(0)
                # Extract full parameter list
                full_match = re.search(
                    rf"def\s+{func_name}\s*\((.*?)\):",
                    code,
                    re.DOTALL,
                )
                if full_match:
                    params = full_match.group(1)
                    # Replace mutable defaults with None
                    fixed_params = re.sub(
                        r"(\w+)\s*=\s*(\[.*?\]|\{.*?\})",
                        r"\1=None",
                        params,
                    )
                    # Add initialization inside function
                    fixed_code = code.replace(params, fixed_params)
                    # Add initialization after def line
                    lines = fixed_code.split("\n")
                    for i, line in enumerate(lines):
                        if line.strip().startswith("def ") and func_name in line:
                            indent = len(line) - len(line.lstrip()) + 4
                            init_lines = []
                            for param_match in re.finditer(
                                r"(\w+)=None",
                                fixed_params,
                            ):
                                param = param_match.group(1)
                                if param in params:
                                    init_lines.append(" " * indent + f"if {param} is None:\n")
                                    init_lines.append(" " * (indent + 4) + f"{param} = []\n")
                            lines.insert(i + 1, "".join(init_lines))
                            break
                    fixed_code = "".join(lines)

                    return FixProposal(
                        fix_type=FixType.MUTABLE_DEFAULT,
                        description="Fix mutable default argument",
                        original_code=code,
                        proposed_code=fixed_code,
                        confidence=0.95,
                        equation_refs=violation.equation_refs,
                    )
        return None

    def _fix_type_safety(
        self,
        violation: VerificationResult,
        code: str,
        language: str,
    ) -> FixProposal:
        """Generate type safety fix."""
        if language == "python":
            # Add type hints to function
            match = re.search(r"def\s+(\w+)\s*\(([^)]*)\)(\s*->\s*[^:]*)?:", code)
            if match and not match.group(3):  # No return type
                func_name = match.group(1)
                params = match.group(2)

                # Generate type hints
                typed_params = []
                for param in params.split(","):
                    param = param.strip()
                    if param and "=" not in param and ":" not in param:
                        # Guess type from name
                        if "count" in param or "index" in param or "num" in param:
                            typed_params.append(f"{param}: int")
                        elif "name" in param or "text" in param or "str" in param:
                            typed_params.append(f"{param}: str")
                        elif "items" in param or "list" in param:
                            typed_params.append(f"{param}: list")
                        elif "data" in param or "dict" in param:
                            typed_params.append(f"{param}: dict")
                        else:
                            typed_params.append(f"{param}: Any")
                    elif param:
                        typed_params.append(param)

                new_params = ", ".join(typed_params)
                fixed_code = code.replace(f"({params})", f"({new_params})", 1)
                fixed_code = fixed_code.replace(
                    f"def {func_name}({new_params}):",
                    f"def {func_name}({new_params}) -> Any:",
                )

                return FixProposal(
                    fix_type=FixType.TYPE_HINT,
                    description="Add type annotations",
                    original_code=code,
                    proposed_code=fixed_code,
                    confidence=0.8,
                )
        return None

    def _fix_correctness(
        self,
        violation: VerificationResult,
        code: str,
        language: str,
    ) -> FixProposal:
        """Generate correctness fix."""
        if "recursion" in str(violation.evidence).lower():
            # Add base case for recursion
            match = re.search(r"def\s+(\w+)\s*\([^)]*\):", code)
            if match:
                func_name = match.group(1)
                # Find first line after def
                lines = code.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().startswith("def ") and func_name in line:
                        indent = len(line) - len(line.lstrip()) + 4
                        # Add base case guard
                        base_case = " " * indent + "if not x:\n" + " " * (indent + 4) + "return x\n"
                        lines.insert(i + 1, base_case)
                        break

                fixed_code = "".join(lines)
                return FixProposal(
                    fix_type=FixType.RECURSION_GUARD,
                    description="Add recursion base case",
                    original_code=code,
                    proposed_code=fixed_code,
                    confidence=0.7,
                )
        return None


class AutomatedRemediationEngine:
    """
    Self-healing code remediation engine.

    Closes the loop between detection and repair.
    """

    def __init__(self, organism_root: Path = None):
        self.organism_root = organism_root or Path(__file__).parent.parent
        self.verifier: InvariantVerificationEngine = None
        self.fix_generator: CodeFixGenerator = None
        self.history: list[RemediationRecord] = []

        if IMMUNE_AVAILABLE:
            self.verifier = InvariantVerificationEngine(self.organism_root)

        if BRAIN_AVAILABLE:
            layer = CognitiveEquationLayer(self.organism_root)
            layer.initialize()
            self.fix_generator = CodeFixGenerator(layer)

    def remediate(
        self,
        code: str,
        language: str,
        auto_apply: bool = False,
    ) -> RemediationRecord:
        """
        Full remediation pipeline.

        Args:
            code: Source code to remediate
            language: Programming language
            auto_apply: Whether to automatically apply fixes

        Returns:
            Remediation record with results
        """
        record_id = f"REM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Step 1: Detect violations
        if not self.verifier:
            return RemediationRecord(
                id=record_id,
                timestamp=datetime.now().isoformat(),
                original_code=code,
                language=language,
                violations=[],
                fixes=[],
                status=RemediationStatus.FAILED,
                error_message="Verification engine not available",
            )

        violations = self.verifier.verify_code(code, language)
        violation_objs = [v for v in violations if v.violations]

        if not violation_objs:
            return RemediationRecord(
                id=record_id,
                timestamp=datetime.now().isoformat(),
                original_code=code,
                language=language,
                violations=violations,
                fixes=[],
                status=RemediationStatus.APPLIED,  # No fixes needed
            )

        # Step 2: Generate fixes
        fixes = []
        for violation in violation_objs:
            if self.fix_generator:
                fix = self.fix_generator.generate_fix(violation, code, language)
                if fix:
                    fixes.append(fix)

        # Step 3: Validate fixes
        validated_fixes = []
        for fix in fixes:
            if self._validate_fix(fix, language):
                fix.validation_passed = True
                validated_fixes.append(fix)

        # Step 4: Apply or return
        record = RemediationRecord(
            id=record_id,
            timestamp=datetime.now().isoformat(),
            original_code=code,
            language=language,
            violations=violations,
            fixes=validated_fixes,
            status=RemediationStatus.GENERATING,
        )

        if auto_apply and validated_fixes:
            # Apply highest confidence fix
            best_fix = max(validated_fixes, key=lambda f: f.confidence)
            record.applied_fix = best_fix
            record.status = RemediationStatus.APPLIED

        self.history.append(record)
        return record

    def _validate_fix(self, fix: FixProposal, language: str) -> bool:
        """Validate fix by re-verifying."""
        if not self.verifier:
            return False

        # Verify the proposed code
        new_results = self.verifier.verify_code(fix.proposed_code, language)
        new_violations = [v for v in new_results if v.violations]

        # Check if original violation is resolved
        return len(new_violations) < fix.confidence

    def get_remediation_report(self) -> dict[str, Any]:
        """Generate summary report."""
        total = len(self.history)
        applied = sum(1 for r in self.history if r.status == RemediationStatus.APPLIED)
        failed = sum(1 for r in self.history if r.status == RemediationStatus.FAILED)

        return {
            "total_attempts": total,
            "successful": applied,
            "failed": failed,
            "success_rate": applied / total if total > 0 else 0,
            "fix_types": self._count_fix_types(),
        }

    def _count_fix_types(self) -> dict[str, int]:
        """Count fix types in history."""
        counts = {}
        for record in self.history:
            for fix in record.fixes:
                ft = fix.fix_type.value
                counts[ft] = counts.get(ft, 0) + 1
        return counts


def main() -> int:
    """Test automated remediation."""
    print("[AutomatedRemediationEngine] Testing...")

    engine = AutomatedRemediationEngine()

    # Test with problematic code
    test_code = """
def bad_function(items=[]):
    items.append(1)
    return items
"""

    print("\n[Test] Mutable default argument...")
    result = engine.remediate(test_code, "python", auto_apply=True)

    print(f"  Status: {result.status.name}")
    print(f"  Violations: {len([v for v in result.violations if v.violations])}")
    print(f"  Fixes generated: {len(result.fixes)}")

    if result.applied_fix:
        print(f"\n  Applied fix: {result.applied_fix.fix_type.value}")
        print(f"  Confidence: {result.applied_fix.confidence}")
        print(f"  Proposed code:\n{result.applied_fix.proposed_code[:200]}...")

    # Report
    report = engine.get_remediation_report()
    print(f"\n[Report] {report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
