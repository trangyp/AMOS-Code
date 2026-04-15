"""Quantum Decision Engine for AMOS"""

from __future__ import annotations

import json
import random
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class DecisionPath:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    expected_value: float = 0.0
    uncertainty: float = 0.5  # 0-1
    probability: float = 0.5
    outcomes: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


class QuantumDecisionEngine:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.decisions: list[dict] = []
        self._load_data()

    def _load_data(self):
        f = self.data_dir / "decisions.json"
        if f.exists():
            try:
                self.decisions = json.loads(f.read_text()).get("decisions", [])
            except Exception:
                pass

    def save(self):
        f = self.data_dir / "decisions.json"
        f.write_text(
            json.dumps(
                {"saved_at": datetime.utcnow().isoformat(), "decisions": self.decisions}, indent=2
            )
        )

    def evaluate_paths(self, paths: list[DecisionPath]) -> dict[str, Any]:
        if not paths:
            return {"error": "No paths provided"}
        # Calculate expected values with uncertainty
        for p in paths:
            p.probability = 1.0 / len(paths)  # Equal weight initially

        # Sort by expected value
        paths.sort(key=lambda x: x.expected_value, reverse=True)
        best = paths[0]

        return {
            "best_path": best.to_dict(),
            "confidence": 1.0 - best.uncertainty,
            "alternatives": [p.to_dict() for p in paths[1:]],
            "recommendation": f"Choose {best.name} (EV: {best.expected_value:.2f})",
        }

    def probabilistic_decide(self, paths: list[DecisionPath]) -> DecisionPath:
        """Collapse to one path based on probabilities"""
        if not paths:
            return DecisionPath(name="no_options")
        weights = [1.0 / len(paths) for _ in paths]  # Equal probability
        return random.choices(paths, weights=weights, k=1)[0]

    def multi_path_explore(self, paths: list[DecisionPath], top_n: int = 3) -> list[DecisionPath]:
        """Keep top N paths in superposition"""
        paths.sort(key=lambda x: x.expected_value, reverse=True)
        return paths[:top_n]


_ENGINE: Optional[QuantumDecisionEngine] = None


def get_quantum_decision_engine(data_dir=None):
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = QuantumDecisionEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Quantum Decision Engine (12_QUANTUM_LAYER)")
    qde = get_quantum_decision_engine()
    paths = [
        DecisionPath(
            name="Fast", description="Quick solution", expected_value=0.7, uncertainty=0.3
        ),
        DecisionPath(
            name="Thorough", description="Comprehensive", expected_value=0.9, uncertainty=0.2
        ),
    ]
    result = qde.evaluate_paths(paths)
    print(f"Recommendation: {result['recommendation']}")
