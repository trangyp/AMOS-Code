"""Probability Engine for AMOS"""
from __future__ import annotations

import json
import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class ProbabilityDistribution:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    outcomes: dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {**asdict(self), "total_prob": sum(self.outcomes.values())}


class ProbabilityEngine:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.distributions: list[ProbabilityDistribution] = []
        self._load_data()

    def _load_data(self):
        f = self.data_dir / "probabilities.json"
        if f.exists():
            try:
                data = json.loads(f.read_text())
                for d in data.get("distributions", []):
                    self.distributions.append(
                        ProbabilityDistribution(
                            id=d["id"],
                            name=d["name"],
                            outcomes=d["outcomes"],
                            created_at=d["created_at"],
                        )
                    )
            except Exception:
                pass

    def save(self):
        f = self.data_dir / "probabilities.json"
        f.write_text(
            json.dumps(
                {
                    "saved_at": datetime.utcnow().isoformat(),
                    "distributions": [d.to_dict() for d in self.distributions],
                },
                indent=2,
            )
        )

    def create_distribution(self, name: str, outcomes: dict[str, float]) -> ProbabilityDistribution:
        total = sum(outcomes.values())
        if total > 0:
            outcomes = {k: v / total for k, v in outcomes.items()}
        dist = ProbabilityDistribution(name=name, outcomes=outcomes)
        self.distributions.append(dist)
        self.save()
        return dist

    def calculate_entropy(self, dist_id: str) -> float:
        for d in self.distributions:
            if d.id == dist_id:
                return -sum(p * math.log2(p) for p in d.outcomes.values() if p > 0)
        return 0.0

    def get_expected_value(self, dist_id: str, value_map: dict[str, float]) -> float:
        for d in self.distributions:
            if d.id == dist_id:
                return sum(p * value_map.get(k, 0) for k, p in d.outcomes.items())
        return 0.0

    def monte_carlo_sample(self, dist_id: str, n_samples: int = 1000) -> dict[str, int]:
        import random

        for d in self.distributions:
            if d.id == dist_id:
                results = {k: 0 for k in d.outcomes.keys()}
                outcomes, weights = zip(*d.outcomes.items())
                for _ in range(n_samples):
                    results[random.choices(outcomes, weights=weights)[0]] += 1
                return {k: v / n_samples for k, v in results.items()}
        return {}


_ENGINE: Optional[ProbabilityEngine] = None


def get_probability_engine(data_dir=None):
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = ProbabilityEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Probability Engine (12_QUANTUM_LAYER)")
    pe = get_probability_engine()
    dist = pe.create_distribution("task_success", {"success": 0.8, "failure": 0.2})
    print(f"Created: {dist.name}, Entropy: {pe.calculate_entropy(dist.id):.2f}")
