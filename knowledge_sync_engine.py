#!/usr/bin/env python3
"""Knowledge Synchronization Engine - Bidirectional Code ↔ Docs Bridge"""

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List


class SyncStatus(Enum):
    SYNCED = auto()
    DOC_ONLY = auto()
    CODE_ONLY = auto()
    DIVERGED = auto()


@dataclass
class EquationSignature:
    name: str
    formula: str
    domain: str
    invariants: List[str]
    parameters: List[str]
    description: str
    source_file: str
    line_number: int
    content_hash: str


class KnowledgeSyncEngine:
    """Bidirectional sync between documentation and code."""

    def __init__(self, docs_path: str = ".", code_path: str = "amos_superbrain_equation_bridge.py"):
        self.docs_path = Path(docs_path)
        self.code_path = Path(code_path)
        self.doc_equations: Dict[str, EquationSignature] = {}
        self.code_equations: Dict[str, EquationSignature] = {}
        self.sync_state: Dict[str, SyncStatus] = {}

    def scan_documentation(self) -> Dict[str, EquationSignature]:
        """Scan markdown documents for equation definitions."""
        equations = {}
        doc_files = [
            "PHYSICS_QUANTUM_EQUATIONS_INVARIANTS.md",
            "EXHAUSTIVE_EQUATIONS_AND_INVARIANTS_MATH_SCIENCE.md",
        ]

        for doc_file in doc_files:
            filepath = self.docs_path / doc_file
            if not filepath.exists():
                continue
            content = filepath.read_text()
            section_pattern = r"^##+\s+(\d+)?\.?\s*([^\n]+)\n+([^#]+?)(?=^##|\Z)"
            sections = re.findall(section_pattern, content, re.MULTILINE | re.DOTALL)

            for num, title, body in sections:
                latex_pattern = r"\$\$([^$]+)\$\$"
                formulas = re.findall(latex_pattern, body, re.DOTALL)
                if formulas:
                    eq_name = self._sanitize_name(title)
                    invariant_pattern = r"\*\*Invariant[^*]*\*\*:\s*([^\n]+)"
                    invariants = re.findall(invariant_pattern, body)

                    sig = EquationSignature(
                        name=eq_name,
                        formula=formulas[0].strip()[:200],
                        domain=self._extract_domain(title, body),
                        invariants=invariants[:5],
                        parameters=self._extract_parameters(formulas[0]) if formulas else [],
                        description=body[:300].replace("\n", " "),
                        source_file=doc_file,
                        line_number=content[: content.find(title)].count("\n"),
                        content_hash=hashlib.md5(body.encode()).hexdigest()[:8],
                    )
                    equations[eq_name] = sig

        self.doc_equations = equations
        return equations

    def scan_implementations(self) -> Dict[str, EquationSignature]:
        """Scan code for implemented equations."""
        equations = {}
        if not self.code_path.exists():
            return equations
        content = self.code_path.read_text()

        # Find registered equations in metadata
        reg_pattern = r'"([a-z_][a-z0-9_]*)"\s*:\s*\(\s*([A-Za-z]+)\.([a-z_]+)'
        registrations = re.findall(reg_pattern, content)

        for eq_name, class_name, method_name in registrations:
            line_num = content.find(f'"{eq_name}"')
            sig = EquationSignature(
                name=eq_name,
                formula=f"{class_name}.{method_name}()",
                domain=class_name.lower(),
                invariants=[],
                parameters=[],
                description=f"Registered via {class_name}",
                source_file=str(self.code_path),
                line_number=line_num,
                content_hash="",
            )
            equations[eq_name] = sig

        self.code_equations = equations
        return equations

    def compute_diff(self) -> Dict[str, SyncStatus]:
        """Compute differential sync state."""
        all_names = set(self.doc_equations.keys()) | set(self.code_equations.keys())

        for name in all_names:
            in_doc = name in self.doc_equations
            in_code = name in self.code_equations

            if in_doc and in_code:
                self.sync_state[name] = SyncStatus.SYNCED
            elif in_doc:
                self.sync_state[name] = SyncStatus.DOC_ONLY
            elif in_code:
                self.sync_state[name] = SyncStatus.CODE_ONLY

        return self.sync_state

    def generate_report(self) -> dict:
        """Generate sync report."""
        if not self.sync_state:
            self.scan_documentation()
            self.scan_implementations()
            self.compute_diff()

        synced = sum(1 for s in self.sync_state.values() if s == SyncStatus.SYNCED)
        doc_only = sum(1 for s in self.sync_state.values() if s == SyncStatus.DOC_ONLY)
        code_only = sum(1 for s in self.sync_state.values() if s == SyncStatus.CODE_ONLY)

        return {
            "timestamp": datetime.now().isoformat(),
            "total": len(self.sync_state),
            "synced": synced,
            "doc_only": doc_only,
            "code_only": code_only,
            "coverage": synced / len(self.sync_state) * 100 if self.sync_state else 0,
            "recommendations": [
                f"Implement {doc_only} documented equations"
                if doc_only > 0
                else "All documented equations implemented",
                f"Document {code_only} code equations"
                if code_only > 0
                else "All code equations documented",
            ],
        }

    def _sanitize_name(self, title: str) -> str:
        """Convert title to snake_case."""
        name = re.sub(r"[^\w\s]", "", title.lower())
        name = re.sub(r"\s+", "_", name)
        return name[:50]

    def _extract_domain(self, title: str, body: str) -> str:
        """Extract domain from section."""
        if "quantum" in body.lower():
            return "quantum_computing"
        elif "physics" in body.lower():
            return "fundamental_physics"
        return "general"

    def _extract_parameters(self, formula: str) -> List[str]:
        """Extract parameters from LaTeX formula."""
        params = re.findall(r"([a-zA-Z])\s*[=\)]", formula)
        return list(set(params))


def main():
    """CLI for sync engine."""
    engine = KnowledgeSyncEngine()
    report = engine.generate_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
