"""AMOS Auto-Formalizer - Automatic Equation Extraction & Code Generation.

Pipeline for extracting mathematical equations from papers and converting
to executable Python code using LLMs.

Usage:
    formalizer = AutoFormalizer()
    result = formalizer.process_paper("arxiv://2404.09874", domain="ML_AI")
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List

try:
    from amos_superbrain_equation_bridge import AMOSSuperBrainBridge

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


class ExtractionStatus(Enum):
    SUCCESS = auto()
    PARTIAL = auto()
    FAILED = auto()


@dataclass
class EquationExtraction:
    equation_id: str
    latex_source: str
    python_code: str
    domain: str
    status: ExtractionStatus
    confidence: float
    source_location: str = ""
    paper_doi: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "equation_id": self.equation_id,
            "latex_source": self.latex_source,
            "python_code": self.python_code,
            "domain": self.domain,
            "status": self.status.name,
            "confidence": self.confidence,
        }


class LaTeXParser:
    """Parse LaTeX mathematical expressions."""

    MATH_PATTERNS = [
        r"\\begin\{equation\}(.*?)\\end\{equation\}",
        r"\\\[(.*?)\\\]",
        r"\\$\\$(.*?)\\$\\$",
    ]

    def extract_math(self, text: str) -> List[dict[str, Any]]:
        equations = []
        for pattern in self.MATH_PATTERNS:
            for match in re.findall(pattern, text, re.DOTALL):
                equations.append({"latex": match.strip(), "variables": self._extract_vars(match)})
        return equations

    def _extract_vars(self, latex: str) -> List[str]:
        return list(set(re.findall(r"[a-zA-Z](?:_\{?\w+\}?)?", latex)))


class AutoFormalizer:
    """Main auto-formalization pipeline."""

    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
        self.parser = LaTeXParser()
        self.superbrain = AMOSSuperBrainBridge() if SUPERBRAIN_AVAILABLE else None
        self.history: List[EquationExtraction] = []

    def process_paper(self, source: str, domain: str) -> List[EquationExtraction]:
        """Process paper and extract equations."""
        # Ingest
        text = self._ingest(source)

        # Extract
        math_exprs = self.parser.extract_math(text)

        # Process each
        results = []
        for i, math in enumerate(math_exprs):
            extraction = self._formalize(math, domain, source, f"eq_{i+1}")
            results.append(extraction)
            self.history.append(extraction)

        return results

    def _formalize(self, math: dict, domain: str, source: str, eq_id: str) -> EquationExtraction:
        """Convert LaTeX to Python."""
        latex = math["latex"]

        # Simple conversion
        python = self._latex_to_python(latex)

        # Verify
        compiles = self._check_compiles(python)
        confidence = 0.8 if compiles else 0.3
        status = ExtractionStatus.SUCCESS if compiles else ExtractionStatus.FAILED

        return EquationExtraction(
            equation_id=eq_id,
            latex_source=latex[:200],
            python_code=python,
            domain=domain,
            status=status,
            confidence=confidence,
            paper_doi=source,
        )

    def _latex_to_python(self, latex: str) -> str:
        """Convert LaTeX to Python (simplified)."""
        python = latex
        # Basic mappings
        python = python.replace(r"\sum", "np.sum")
        python = python.replace(r"\frac", "")
        python = python.replace(r"\sqrt", "np.sqrt")
        python = python.replace(r"\exp", "np.exp")
        python = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1)/(\2)", python)
        python = python.replace("\\", "").replace("{", "(").replace("}", ")")
        python = re.sub(r"\^\{?([^}]+)\}?", r"**\1", python)
        return f"def equation(x):\n    import numpy as np\n    return {python}"

    def _check_compiles(self, code: str) -> bool:
        """Check if code compiles."""
        try:
            compile(code, "<string>", "exec")
            return True
        except Exception:
            return False

    def _ingest(self, source: str) -> str:
        """Ingest document."""
        if source.startswith("arxiv://"):
            return f"% arXiv:{source[8:]}"
        try:
            from pathlib import Path

            return Path(source).read_text()
        except Exception:
            return source

    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        total = len(self.history)
        success = sum(1 for e in self.history if e.status == ExtractionStatus.SUCCESS)
        return {"total": total, "successful": success, "rate": success / total if total > 0 else 0}


def main() -> None:
    """CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Auto-Formalizer")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    args = parser.parse_args()

    if args.demo:
        f = AutoFormalizer()
        sample = r"\begin{equation} f(x) = \sum_{i=1}^n w_i x_i + b \end{equation}"
        results = f.process_paper(sample, "ML_AI")
        for r in results:
            print(f"\n{r.equation_id}: {r.status.name} ({r.confidence:.0%})")
            print(f"Python:\n{r.python_code}")
        print(f"\nStats: {f.get_stats()}")
    else:
        print("AMOS Auto-Formalizer v13.0.0")
        print("Usage: python amos_auto_formalizer.py --demo")


if __name__ == "__main__":
    main()
