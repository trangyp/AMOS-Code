#!/usr/bin/env python3
"""AMOS Learning Kernel - 10_LEARNING Subsystem

Responsible for:
- Pattern recognition and extraction
- Feedback-based learning loops
- Skill acquisition and refinement
- Experience memory formation
- Adaptive behavior modification
- Performance improvement over time
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.learning")


class LearningType(Enum):
    """Types of learning mechanisms."""

    SUPERVISED = auto()  # Learning from labeled feedback
    UNSUPERVISED = auto()  # Pattern discovery without labels
    REINFORCEMENT = auto()  # Learning from rewards/penalties
    IMITATION = auto()  # Learning by copying
    EXPERIENTIAL = auto()  # Learning from direct experience


class SkillLevel(Enum):
    """Skill proficiency levels."""

    NOVICE = 1
    BEGINNER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5
    MASTER = 6


@dataclass
class Pattern:
    """A recognized pattern in data or behavior."""

    pattern_id: str
    signature: str  # Hash or key identifying this pattern
    pattern_type: str
    frequency: int = 1
    contexts: list[dict[str, Any]] = field(default_factory=list)
    first_seen: str = ""
    last_seen: str = ""
    confidence: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = datetime.utcnow().isoformat()
        if not self.last_seen:
            self.last_seen = self.first_seen


@dataclass
class Experience:
    """A recorded experience for learning."""

    experience_id: str
    timestamp: str
    context: dict[str, Any] = field(default_factory=dict)
    action: dict[str, Any] = field(default_factory=dict)
    outcome: dict[str, Any] = field(default_factory=dict)
    feedback: float = 0.0  # -1.0 to 1.0
    learned_patterns: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class Skill:
    """A learned skill with proficiency tracking."""

    skill_id: str
    name: str
    description: str
    level: SkillLevel = SkillLevel.NOVICE
    xp: float = 0.0  # Experience points
    max_xp: float = 100.0
    successful_uses: int = 0
    failed_uses: int = 0
    related_patterns: list[str] = field(default_factory=list)
    created_at: str = ""
    last_used: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.last_used:
            self.last_used = self.created_at

    def add_xp(self, amount: float):
        """Add experience points and potentially level up."""
        self.xp += amount
        self.successful_uses += 1
        self.last_used = datetime.utcnow().isoformat()

        # Level up check
        while self.xp >= self.max_xp and self.level.value < 6:
            self.xp -= self.max_xp
            self.max_xp *= 1.5  # Harder to level up each time
            self.level = SkillLevel(min(self.level.value + 1, 6))
            logger.info(f"Skill '{self.name}' leveled up to {self.level.name}")

    def record_failure(self):
        """Record a failed use of the skill."""
        self.failed_uses += 1
        # Small XP penalty
        self.xp = max(0, self.xp - 1)


class LearningKernel:
    """The Learning Kernel enables the organism to improve over time
    through pattern recognition, feedback learning, and skill acquisition.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.learning_path = organism_root / "10_LEARNING"
        self.memory_path = self.learning_path / "memory"
        self.patterns_path = self.learning_path / "patterns"
        self.skills_path = self.learning_path / "skills"
        self.experiences_path = self.learning_path / "experiences"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        self.skills_path.mkdir(parents=True, exist_ok=True)
        self.experiences_path.mkdir(parents=True, exist_ok=True)

        # Pattern registry
        self.patterns: dict[str, Pattern] = {}
        self.pattern_signatures: dict[str, str] = {}  # signature -> pattern_id

        # Experience memory
        self.experiences: deque = deque(maxlen=1000)

        # Skill registry
        self.skills: dict[str, Skill] = {}

        # Learning configuration
        self.learning_rate = 0.1
        self.decay_rate = 0.01

        # Statistics
        self.stats = {
            "patterns_recognized": 0,
            "experiences_recorded": 0,
            "skills_acquired": 0,
            "total_xp_earned": 0.0,
            "learning_cycles": 0,
        }

        logger.info(f"LearningKernel initialized at {self.learning_path}")

    def recognize_pattern(
        self,
        data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        pattern_type: str = "general",
    ) -> Pattern:
        """Recognize or create a pattern from data."""
        # Generate signature from data
        signature = self._generate_signature(data)

        # Check if pattern exists
        if signature in self.pattern_signatures:
            pattern_id = self.pattern_signatures[signature]
            pattern = self.patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = datetime.utcnow().isoformat()
            pattern.confidence = min(1.0, pattern.confidence + 0.05)
            if context:
                pattern.contexts.append(context)
            logger.debug(f"Recognized existing pattern: {pattern_id}")
        else:
            # Create new pattern
            pattern_id = (
                f"pattern_{len(self.patterns)}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            )
            pattern = Pattern(
                pattern_id=pattern_id,
                signature=signature,
                pattern_type=pattern_type,
                frequency=1,
                contexts=[context] if context else [],
                confidence=0.5,
            )
            self.patterns[pattern_id] = pattern
            self.pattern_signatures[signature] = pattern_id
            self.stats["patterns_recognized"] += 1
            logger.info(f"Created new pattern: {pattern_id}")

        return pattern

    def _generate_signature(self, data: dict[str, Any]) -> str:
        """Generate a unique signature for data."""
        # Normalize and hash the data
        normalized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def record_experience(
        self,
        context: dict[str, Any],
        action: dict[str, Any],
        outcome: dict[str, Any],
        feedback: Optional[float] = None,
    ) -> Experience:
        """Record an experience for future learning."""
        # Calculate feedback if not provided
        if feedback is None:
            feedback = self._calculate_feedback(outcome)

        # Extract patterns from the experience
        learned_patterns = []

        # Pattern from context
        ctx_pattern = self.recognize_pattern(context, pattern_type="context")
        learned_patterns.append(ctx_pattern.pattern_id)

        # Pattern from action-outcome pair
        action_outcome = {"action": action, "outcome": outcome}
        ao_pattern = self.recognize_pattern(action_outcome, pattern_type="action_outcome")
        learned_patterns.append(ao_pattern.pattern_id)

        # Create experience record
        experience_id = f"exp_{len(self.experiences)}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        experience = Experience(
            experience_id=experience_id,
            timestamp=datetime.utcnow().isoformat(),
            context=context,
            action=action,
            outcome=outcome,
            feedback=feedback,
            learned_patterns=learned_patterns,
        )

        self.experiences.append(experience)
        self.stats["experiences_recorded"] += 1

        logger.info(f"Recorded experience: {experience_id} (feedback: {feedback:+.2f})")
        return experience

    def _calculate_feedback(self, outcome: dict[str, Any]) -> float:
        """Calculate feedback score from outcome."""
        score = 0.0

        # Check for success indicators
        if outcome.get("success", False):
            score += 0.5

        # Check for error indicators
        if "error" in outcome:
            score -= 0.5

        # Check for efficiency metrics
        if "efficiency" in outcome:
            score += (outcome["efficiency"] - 0.5) * 0.5

        return max(-1.0, min(1.0, score))

    def acquire_skill(
        self, name: str, description: str, related_patterns: Optional[list[str]] = None
    ) -> Skill:
        """Acquire or improve a skill."""
        # Check if skill already exists
        for skill in self.skills.values():
            if skill.name == name:
                return skill

        # Create new skill
        skill_id = f"skill_{len(self.skills)}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        skill = Skill(
            skill_id=skill_id,
            name=name,
            description=description,
            related_patterns=related_patterns or [],
        )

        self.skills[skill_id] = skill
        self.stats["skills_acquired"] += 1

        logger.info(f"Acquired new skill: {name} ({skill_id})")
        return skill

    def practice_skill(
        self, skill_id: str, success: bool = True, xp_amount: Optional[float] = None
    ) -> bool:
        """Practice a skill and gain XP."""
        if skill_id not in self.skills:
            return False

        skill = self.skills[skill_id]

        if success:
            # Calculate XP based on skill level (diminishing returns)
            if xp_amount is None:
                xp_amount = 10.0 / skill.level.value

            skill.add_xp(xp_amount)
            self.stats["total_xp_earned"] += xp_amount
            logger.info(f"Skill '{skill.name}' practiced successfully (+{xp_amount:.1f} XP)")
        else:
            skill.record_failure()
            logger.info(f"Skill '{skill.name}' practice failed (-1 XP)")

        return True

    def learn_from_experiences(self, n_recent: int = 100) -> dict[str, Any]:
        """Learn from recent experiences."""
        if not self.experiences:
            return {"status": "no_experiences"}

        # Get recent experiences
        recent = list(self.experiences)[-n_recent:]

        # Analyze patterns
        pattern_performance: dict[str, list[float]] = defaultdict(list)

        for exp in recent:
            for pattern_id in exp.learned_patterns:
                pattern_performance[pattern_id].append(exp.feedback)

        # Update pattern confidences
        improvements = []
        for pattern_id, feedbacks in pattern_performance.items():
            if pattern_id in self.patterns:
                avg_feedback = sum(feedbacks) / len(feedbacks)
                self.patterns[pattern_id].confidence = 0.5 + (avg_feedback * 0.5)

                if abs(avg_feedback) > 0.3:
                    improvements.append(
                        {
                            "pattern_id": pattern_id,
                            "avg_feedback": avg_feedback,
                            "confidence": self.patterns[pattern_id].confidence,
                        }
                    )

        self.stats["learning_cycles"] += 1

        logger.info(
            f"Learning cycle completed. Analyzed {len(recent)} experiences, "
            f"updated {len(pattern_performance)} patterns"
        )

        return {
            "status": "success",
            "experiences_analyzed": len(recent),
            "patterns_updated": len(pattern_performance),
            "improvements": improvements,
        }

    def get_relevant_skills(self, context: dict[str, Any]) -> list[Skill]:
        """Get skills relevant to a given context."""
        # Simple matching based on context keys and skill names
        context_str = json.dumps(context, sort_keys=True, default=str).lower()

        scored_skills = []
        for skill in self.skills.values():
            score = 0
            # Name matching
            if skill.name.lower() in context_str:
                score += 2
            # Description matching
            if skill.description.lower() in context_str:
                score += 1
            # Level bonus
            score += skill.level.value * 0.5

            if score > 0:
                scored_skills.append((score, skill))

        # Sort by score
        scored_skills.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored_skills[:5]]  # Top 5

    def get_pattern_recommendations(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Get pattern-based recommendations for a context."""
        # Find similar contexts
        context_sig = self._generate_signature(context)
        recommendations = []

        for pattern in self.patterns.values():
            if pattern.confidence < 0.3:
                continue  # Skip low-confidence patterns

            for ctx in pattern.contexts[-10:]:  # Check recent contexts
                ctx_sig = self._generate_signature(ctx)
                if ctx_sig == context_sig or self._similarity(context, ctx) > 0.7:
                    # Found similar context
                    # Find associated outcomes
                    for exp in self.experiences:
                        if exp.learned_patterns and pattern.pattern_id in exp.learned_patterns:
                            recommendations.append(
                                {
                                    "pattern_id": pattern.pattern_id,
                                    "pattern_type": pattern.pattern_type,
                                    "confidence": pattern.confidence,
                                    "frequency": pattern.frequency,
                                    "suggested_action": exp.action,
                                    "expected_outcome": exp.outcome,
                                    "historical_feedback": exp.feedback,
                                }
                            )
                            break
                    break

        # Sort by confidence and feedback
        recommendations.sort(
            key=lambda x: (x["confidence"], x.get("historical_feedback", 0)), reverse=True
        )
        return recommendations[:5]

    def _similarity(self, dict1: dict, dict2: dict) -> float:
        """Calculate simple similarity between two dictionaries."""
        if not dict1 or not dict2:
            return 0.0

        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())

        if not keys1 or not keys2:
            return 0.0

        intersection = keys1 & keys2
        union = keys1 | keys2

        return len(intersection) / len(union) if union else 0.0

    def get_state(self) -> dict[str, Any]:
        """Get current learning state."""
        # Calculate average skill level
        avg_skill_level = 0.0
        if self.skills:
            avg_skill_level = sum(s.level.value for s in self.skills.values()) / len(self.skills)

        # Get top patterns
        top_patterns = sorted(
            self.patterns.values(), key=lambda p: (p.confidence, p.frequency), reverse=True
        )[:5]

        return {
            "patterns_stored": len(self.patterns),
            "experiences_recorded": len(self.experiences),
            "skills_acquired": len(self.skills),
            "avg_skill_level": round(avg_skill_level, 2),
            "total_xp": round(self.stats["total_xp_earned"], 1),
            "learning_cycles": self.stats["learning_cycles"],
            "top_patterns": [
                {"id": p.pattern_id, "type": p.pattern_type, "confidence": round(p.confidence, 2)}
                for p in top_patterns
            ],
            "skill_summary": [
                {"name": s.name, "level": s.level.name, "xp": round(s.xp, 1)}
                for s in list(self.skills.values())[:5]
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }


if __name__ == "__main__":
    # Test the learning kernel
    root = Path(__file__).parent.parent
    learning = LearningKernel(root)

    print("Learning State (initial):")
    print(json.dumps(learning.get_state(), indent=2))

    print("\n=== Test 1: Pattern Recognition ===")

    # Recognize some patterns
    pattern1 = learning.recognize_pattern(
        {"input_type": "file_read", "file_ext": "py"}, pattern_type="file_operation"
    )
    print(f"Pattern 1: {pattern1.pattern_id}, confidence: {pattern1.confidence}")

    # Same pattern again
    pattern1_again = learning.recognize_pattern(
        {"input_type": "file_read", "file_ext": "py"}, pattern_type="file_operation"
    )
    print(
        f"Pattern 1 again: frequency={pattern1_again.frequency}, confidence={pattern1_again.confidence}"
    )

    # Different pattern
    pattern2 = learning.recognize_pattern(
        {"input_type": "api_call", "method": "GET"}, pattern_type="network_operation"
    )
    print(f"Pattern 2: {pattern2.pattern_id}, type: {pattern2.pattern_type}")

    print("\n=== Test 2: Record Experiences ===")

    # Record successful experience
    exp1 = learning.record_experience(
        context={"task": "read_file", "file": "test.py"},
        action={"tool": "file_read", "params": {"path": "test.py"}},
        outcome={"success": True, "size": 1024},
        feedback=0.8,
    )
    print(f"Recorded experience 1: {exp1.experience_id}, feedback: {exp1.feedback}")

    # Record failed experience
    exp2 = learning.record_experience(
        context={"task": "delete_file", "file": "protected.txt"},
        action={"tool": "file_delete", "params": {"path": "protected.txt"}},
        outcome={"success": False, "error": "permission_denied"},
        feedback=-0.5,
    )
    print(f"Recorded experience 2: {exp2.experience_id}, feedback: {exp2.feedback}")

    print("\n=== Test 3: Skill Acquisition ===")

    # Acquire skill
    skill = learning.acquire_skill(
        name="file_operations",
        description="Reading and writing files efficiently",
        related_patterns=[pattern1.pattern_id],
    )
    print(f"Acquired skill: {skill.name} (level: {skill.level.name})")

    # Practice skill
    learning.practice_skill(skill.skill_id, success=True, xp_amount=15)
    learning.practice_skill(skill.skill_id, success=True, xp_amount=20)
    learning.practice_skill(skill.skill_id, success=False)
    print(f"After practice: XP={skill.xp:.1f}, Level={skill.level.name}")

    print("\n=== Test 4: Learn from Experiences ===")

    result = learning.learn_from_experiences()
    print(f"Learning result: {result['status']}")
    print(f"Experiences analyzed: {result['experiences_analyzed']}")
    print(f"Patterns updated: {result['patterns_updated']}")

    print("\n=== Test 5: Get Recommendations ===")

    # Get skill recommendations
    relevant = learning.get_relevant_skills({"task": "read_file", "operation": "file_read"})
    print(f"Relevant skills: {[s.name for s in relevant]}")

    # Get pattern recommendations
    recs = learning.get_pattern_recommendations({"input_type": "file_read"})
    print(f"Pattern recommendations: {len(recs)}")

    print("\nFinal State:")
    print(json.dumps(learning.get_state(), indent=2))
