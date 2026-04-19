"""Evolution Memory & Learning System - Persistent Knowledge Layer.

Stores evolution outcomes, learns patterns, and enables intelligent
recommendations for future structural improvements.

Key capabilities:
- Persistent storage of evolution contracts and outcomes
- Pattern recognition across evolution history
- Success rate learning per pattern type
- Recommendation engine for detected hotspots
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .contract import EvolutionContract, EvolutionStatus


@dataclass
class EvolutionMemory:
    """A recorded evolution outcome for learning."""

    memory_id: str
    evolution_id: str
    pattern_type: str
    target_files: List[str]
    problem_pattern: str
    expected_improvement: str
    actual_improvement: str
    status: str
    created_at: str
    completed_at: str = None
    patches_applied: int = 0
    patches_rolled_back: int = 0
    lessons_learned: str = ""


@dataclass
class PatternSignature:
    """Identifiable signature of a structural pattern."""

    pattern_hash: str
    pattern_type: str
    signature_features: Dict[str, Any]
    first_seen: str
    occurrence_count: int
    success_count: int
    failure_count: int


class EvolutionMemoryStore:
    """Persistent store for evolution memory and learning."""

    def __init__(self, storage_path: str = None) -> None:
        """Initialize memory store."""
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(".amos_evolution_memory")

        self.storage_path.mkdir(exist_ok=True)
        self.memories: List[EvolutionMemory] = []
        self.patterns: Dict[str, PatternSignature] = {}
        self._load()

    def _load(self) -> None:
        """Load memories from disk."""
        memory_file = self.storage_path / "evolution_memories.jsonl"
        if memory_file.exists():
            with open(memory_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.memories.append(EvolutionMemory(**data))

        patterns_file = self.storage_path / "learned_patterns.json"
        if patterns_file.exists():
            with open(patterns_file) as f:
                patterns_data = json.load(f)
                for k, v in patterns_data.items():
                    self.patterns[k] = PatternSignature(**v)

    def save(self) -> None:
        """Save memories to disk."""
        memory_file = self.storage_path / "evolution_memories.jsonl"
        with open(memory_file, "w") as f:
            for memory in self.memories:
                f.write(json.dumps(asdict(memory)) + "\n")

        patterns_file = self.storage_path / "learned_patterns.json"
        with open(patterns_file, "w") as f:
            patterns_dict = {k: asdict(v) for k, v in self.patterns.items()}
            json.dump(patterns_dict, f, indent=2)

    def record(
        self, contract: EvolutionContract, patches_applied: int = 0, lessons: str = ""
    ) -> None:
        """Record an evolution outcome."""
        memory = EvolutionMemory(
            memory_id=hashlib.md5(
                f"{contract.evolution_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12],
            evolution_id=contract.evolution_id,
            pattern_type=contract.owner,
            target_files=contract.target_files,
            problem_pattern=contract.problem_pattern,
            expected_improvement=contract.expected_improvement,
            actual_improvement=contract.actual_improvement,
            status=contract.status.value,
            created_at=contract.created_at.isoformat(),
            completed_at=datetime.now().isoformat()
            if contract.status in [EvolutionStatus.COMPLETED, EvolutionStatus.ROLLED_BACK]
            else None,
            patches_applied=patches_applied,
            lessons_learned=lessons,
        )
        self.memories.append(memory)
        self._update_pattern_learning(contract)
        self.save()

    def _update_pattern_learning(self, contract: EvolutionContract) -> None:
        """Update pattern learning from evolution outcome."""
        # Create pattern signature hash
        features = {
            "pattern_type": contract.owner,
            "file_count": len(contract.target_files),
            "description_length": len(contract.problem_pattern),
        }
        pattern_hash = hashlib.md5(json.dumps(features, sort_keys=True).encode()).hexdigest()[:16]

        if pattern_hash not in self.patterns:
            self.patterns[pattern_hash] = PatternSignature(
                pattern_hash=pattern_hash,
                pattern_type=contract.owner,
                signature_features=features,
                first_seen=datetime.now().isoformat(),
                occurrence_count=0,
                success_count=0,
                failure_count=0,
            )

        pattern = self.patterns[pattern_hash]
        pattern.occurrence_count += 1

        if contract.status == EvolutionStatus.COMPLETED:
            pattern.success_count += 1
        elif contract.status == EvolutionStatus.ROLLED_BACK:
            pattern.failure_count += 1

    def get_success_rate(self, pattern_type: str) -> float:
        """Get success rate for a pattern type."""
        relevant = [
            m
            for m in self.memories
            if m.pattern_type == pattern_type and m.status in ["completed", "rolled_back"]
        ]
        if not relevant:
            return 0.5  # Unknown - neutral

        completed = sum(1 for m in relevant if m.status == "completed")
        return completed / len(relevant)

    def get_recommendation(self, pattern_type: str, problem_description: str) -> Dict[str, Any]:
        """Get recommendation based on learned patterns."""
        # Find similar past evolutions
        similar = [
            m for m in self.memories if m.pattern_type == pattern_type and m.status == "completed"
        ]

        if not similar:
            return None

        # Return best practice from successful evolutions
        best = max(similar, key=lambda m: m.patches_applied)

        return {
            "recommended_action": best.actual_improvement,
            "confidence": len(similar)
            / max(len([m for m in self.memories if m.pattern_type == pattern_type]), 1),
            "based_on": f"{len(similar)} similar successful evolutions",
            "lessons": best.lessons_learned,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        total = len(self.memories)
        completed = sum(1 for m in self.memories if m.status == "completed")
        rolled_back = sum(1 for m in self.memories if m.status == "rolled_back")

        pattern_stats = {}
        for pattern_hash, pattern in self.patterns.items():
            if pattern.occurrence_count > 0:
                success_rate = (
                    pattern.success_count / (pattern.success_count + pattern.failure_count)
                    if (pattern.success_count + pattern.failure_count) > 0
                    else 0
                )
                pattern_stats[pattern.pattern_type] = {
                    "occurrences": pattern.occurrence_count,
                    "success_rate": success_rate,
                }

        return {
            "total_evolutions": total,
            "completed": completed,
            "rolled_back": rolled_back,
            "success_rate": completed / total if total > 0 else 0,
            "learned_patterns": len(self.patterns),
            "pattern_statistics": pattern_stats,
        }


class LearningEngine:
    """Intelligent recommendations based on evolution history."""

    def __init__(self, memory_store: EvolutionMemoryStore) -> None:
        """Initialize learning engine."""
        self.memory = memory_store

    def predict_success(self, contract: EvolutionContract) -> float:
        """Predict probability of success for a proposed evolution."""
        # Base on pattern type success rate
        base_rate = self.memory.get_success_rate(contract.owner)

        # Adjust based on mutation budget
        file_count = len(contract.target_files)
        if file_count > 5:
            base_rate *= 0.8  # Large changes riskier
        elif file_count <= 2:
            base_rate *= 1.1  # Small changes safer

        return min(base_rate, 1.0)

    def suggest_optimization(self, contract: EvolutionContract) -> List[str]:
        """Suggest optimizations for an evolution contract."""
        suggestions = []

        # Check mutation budget
        if len(contract.target_files) > 5:
            suggestions.append("Consider splitting into smaller evolutions (max 5 files)")

        # Check if pattern has been tried before
        existing = [m for m in self.memory.memories if m.evolution_id == contract.evolution_id]
        if existing:
            failed = [m for m in existing if m.status == "rolled_back"]
            if failed:
                suggestions.append(
                    f"Warning: {len(failed)} previous attempts failed - review approach"
                )

        # Get pattern-specific recommendations
        rec = self.memory.get_recommendation(contract.owner, contract.problem_pattern)
        if rec and rec["confidence"] > 0.5:
            suggestions.append(f"Learned approach: {rec['recommended_action']}")

        return suggestions
