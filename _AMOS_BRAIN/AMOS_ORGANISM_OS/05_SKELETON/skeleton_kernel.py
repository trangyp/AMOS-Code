#!/usr/bin/env python3
"""AMOS Skeleton Kernel - 05_SKELETON Subsystem

Responsible for:
- Rules and constraint enforcement
- Permission system and access control
- Subsystem hierarchy management
- Time architecture (scheduling, timeouts, lifecycle)
- Policy registry and validation
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.skeleton")


class PermissionLevel(Enum):
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 3
    ADMIN = 4


class ConstraintType(Enum):
    MUST = "must"  # Must be satisfied
    MUST_NOT = "must_not"  # Must not violate
    SHOULD = "should"  # Should be satisfied (warning if not)
    MAX = "max"  # Maximum value
    MIN = "min"  # Minimum value
    PATTERN = "pattern"  # Regex pattern match
    ENUM = "enum"  # Must be one of allowed values


@dataclass
class Rule:
    """A single rule/constraints definition."""

    rule_id: str
    name: str
    description: str
    constraint_type: ConstraintType
    target: str  # What this rule applies to
    value: Any  # The constraint value
    priority: int = 5  # 1-10, lower = higher priority
    enabled: bool = True
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


@dataclass
class Permission:
    """A permission grant."""

    subsystem: str
    resource: str
    level: PermissionLevel
    granted_by: str
    granted_at: str = ""
    expires_at: str = None

    def __post_init__(self):
        if not self.granted_at:
            self.granted_at = datetime.now(UTC).isoformat()


@dataclass
class ValidationResult:
    """Result of constraint validation."""

    valid: bool
    violations: List[str]
    warnings: List[str]
    checked_rules: List[str]


class SkeletonKernel:
    """The Skeleton Kernel provides structural integrity through
    rules, permissions, and time management.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.skeleton_path = organism_root / "05_SKELETON"
        self.memory_path = self.skeleton_path / "memory"
        self.logs_path = self.skeleton_path / "logs"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Rule registry
        self.rules: Dict[str, Rule] = {}

        # Permission registry
        self.permissions: dict[str, list[Permission]] = {}

        # Hierarchy: parent -> children
        self.hierarchy: dict[str, list[str]] = {
            "00_ROOT": ["01_BRAIN", "02_SENSES", "03_IMMUNE", "04_BLOOD", "05_SKELETON"],
            "01_BRAIN": ["08_WORLD_MODEL", "12_QUANTUM_LAYER"],
            "05_SKELETON": ["06_MUSCLE", "07_METABOLISM"],
            "02_SENSES": ["09_SOCIAL_ENGINE", "10_LIFE_ENGINE"],
            "03_IMMUNE": ["11_LEGAL_BRAIN"],
            "06_MUSCLE": ["13_FACTORY", "14_INTERFACES"],
        }

        # Time-based schedules
        self.schedules: dict[str, dict[str, Any]] = {}

        # Load default rules
        self._load_default_rules()

        logger.info(f"SkeletonKernel initialized at {self.skeleton_path}")

    def _load_default_rules(self):
        """Load the default AMOS global laws as rules."""
        default_rules = [
            Rule(
                rule_id="L1_law_of_law",
                name="Law of Law",
                description="All reasoning must obey highest applicable law",
                constraint_type=ConstraintType.MUST,
                target="all_operations",
                value="hierarchical_law_compliance",
                priority=1,
            ),
            Rule(
                rule_id="L2_rule_of_2",
                name="Rule of 2",
                description="Check at least two contrasting perspectives",
                constraint_type=ConstraintType.MUST,
                target="analysis_operations",
                value="dual_perspective_check",
                priority=1,
            ),
            Rule(
                rule_id="L3_rule_of_4",
                name="Rule of 4",
                description="Consider four quadrants for important decisions",
                constraint_type=ConstraintType.SHOULD,
                target="important_decisions",
                value="quadrant_coverage",
                priority=2,
            ),
            Rule(
                rule_id="L4_structural_integrity",
                name="Absolute Structural Integrity",
                description="All outputs must be logically consistent",
                constraint_type=ConstraintType.MUST,
                target="all_outputs",
                value="consistency_check",
                priority=1,
            ),
            Rule(
                rule_id="S1_no_irreversible",
                name="No Irreversible Without Confirmation",
                description="Irreversible actions require explicit confirmation",
                constraint_type=ConstraintType.MUST_NOT,
                target="muscle_operations",
                value="irreversible_without_confirm",
                priority=1,
            ),
            Rule(
                rule_id="S2_deterministic",
                name="Deterministic Execution",
                description="No hidden randomness in control flow",
                constraint_type=ConstraintType.MUST,
                target="control_operations",
                value="deterministic_behavior",
                priority=2,
            ),
            Rule(
                rule_id="S3_log_all",
                name="Every Decision Loggable",
                description="All decisions must be auditable",
                constraint_type=ConstraintType.MUST,
                target="all_decisions",
                value="audit_trail_required",
                priority=2,
            ),
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

        logger.info(f"Loaded {len(default_rules)} default rules")

    def add_rule(self, rule: Rule) -> bool:
        """Add a new rule to the registry."""
        if rule.rule_id in self.rules:
            logger.warning(f"Rule {rule.rule_id} already exists")
            return False

        self.rules[rule.rule_id] = rule
        self._persist_rules()
        logger.info(f"Added rule: {rule.rule_id}")
        return True

    def _persist_rules(self):
        """Persist rules to disk."""
        rules_file = self.memory_path / "rules.json"
        with open(rules_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.rules.items()}, f, indent=2)

    def validate_operation(
        self, operation: str, context: Dict[str, Any], target_rules: list[str] = None
    ) -> ValidationResult:
        """Validate an operation against applicable rules.

        Args:
            operation: The operation being performed
            context: Operation context/data
            target_rules: Specific rules to check (None = all applicable)

        Returns:
            ValidationResult with violations and warnings
        """
        violations = []
        warnings = []
        checked = []

        # Determine which rules to check
        rules_to_check = []
        if target_rules:
            rules_to_check = [self.rules.get(rid) for rid in target_rules if rid in self.rules]
        else:
            # Find rules applicable to this operation
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                if self._rule_applies(rule, operation, context):
                    rules_to_check.append(rule)

        # Check each rule
        for rule in rules_to_check:
            if rule is None:
                continue
            checked.append(rule.rule_id)
            result = self._check_constraint(rule, context)

            if not result:
                if rule.constraint_type == ConstraintType.MUST:
                    violations.append(f"{rule.rule_id}: {rule.description}")
                elif rule.constraint_type == ConstraintType.MUST_NOT:
                    violations.append(f"{rule.rule_id}: Prohibited action detected")
                elif rule.constraint_type == ConstraintType.SHOULD:
                    warnings.append(f"{rule.rule_id}: {rule.description}")

        return ValidationResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            checked_rules=checked,
        )

    def _rule_applies(self, rule: Rule, operation: str, context: Dict[str, Any]) -> bool:
        """Determine if a rule applies to an operation."""
        target = rule.target.lower()

        # Check target patterns
        if target == "all_operations":
            return True
        if target == "all_outputs":
            return operation in ["output", "generate", "emit"]
        if target == "all_decisions":
            return operation in ["decide", "choose", "select"]
        if target == "muscle_operations":
            return operation in ["execute", "run", "deploy", "write"]
        if target == "analysis_operations":
            return operation in ["analyze", "think", "process"]
        if target == "control_operations":
            return operation in ["control", "route", "schedule"]
        if target == "important_decisions":
            # Check if marked as important
            return context.get("important", False)

        return False

    def _check_constraint(self, rule: Rule, context: Dict[str, Any]) -> bool:
        """Check if a specific constraint is satisfied."""
        constraint_type = rule.constraint_type

        if constraint_type == ConstraintType.MUST:
            # Check if required field/condition exists
            return context.get(rule.value, False) is not False

        if constraint_type == ConstraintType.MUST_NOT:
            # Check prohibited condition is not present
            prohibited = context.get("action_type", "")
            return rule.value not in str(prohibited)

        if constraint_type == ConstraintType.SHOULD:
            # Check recommended condition
            return context.get(rule.value) is not None

        if constraint_type == ConstraintType.PATTERN:
            value = str(context.get(rule.target, ""))
            pattern = re.compile(rule.value)
            return pattern.match(value) is not None

        return True

    def grant_permission(
        self, subsystem: str, resource: str, level: PermissionLevel, granted_by: str = "00_ROOT"
    ) -> Permission:
        """Grant a permission to a subsystem."""
        perm = Permission(
            subsystem=subsystem, resource=resource, level=level, granted_by=granted_by
        )

        if subsystem not in self.permissions:
            self.permissions[subsystem] = []

        self.permissions[subsystem].append(perm)
        logger.info(f"Granted {level.name} permission on {resource} to {subsystem}")
        return perm

    def check_permission(
        self, subsystem: str, resource: str, required_level: PermissionLevel
    ) -> bool:
        """Check if a subsystem has required permission."""
        if subsystem not in self.permissions:
            return False

        for perm in self.permissions[subsystem]:
            if perm.resource == resource or perm.resource == "*":
                if perm.level.value >= required_level.value:
                    return True

        return False

    def get_hierarchy(self, subsystem: str) -> Dict[str, Any]:
        """Get hierarchy information for a subsystem."""
        # Find parent
        parent = None
        for p, children in self.hierarchy.items():
            if subsystem in children:
                parent = p
                break

        # Get children
        children = self.hierarchy.get(subsystem, [])

        return {
            "subsystem": subsystem,
            "parent": parent,
            "children": children,
            "depth": self._calculate_depth(subsystem),
        }

    def _calculate_depth(self, subsystem: str, current_depth: int = 0) -> int:
        """Calculate depth in hierarchy."""
        # Find parent
        for p, children in self.hierarchy.items():
            if subsystem in children:
                return self._calculate_depth(p, current_depth + 1)

        return current_depth

    def schedule_task(
        self, task_id: str, subsystem: str, action: str, when: datetime, recurring: bool = False
    ):
        """Schedule a task for future execution."""
        self.schedules[task_id] = {
            "subsystem": subsystem,
            "action": action,
            "when": when.isoformat(),
            "recurring": recurring,
            "created": datetime.now(UTC).isoformat(),
        }
        logger.info(f"Scheduled task {task_id} for {when}")

    def get_due_tasks(self) -> list[dict[str, Any]]:
        """Get all tasks that are due for execution."""
        now = datetime.now(UTC)
        due = []

        for task_id, schedule in self.schedules.items():
            task_time = datetime.fromisoformat(schedule["when"])
            if task_time <= now:
                due.append({"task_id": task_id, **schedule})

        return due

    def get_state(self) -> Dict[str, Any]:
        """Get current skeleton state."""
        return {
            "rules_count": len(self.rules),
            "permissions_granted": sum(len(p) for p in self.permissions.values()),
            "hierarchy_nodes": len(self.hierarchy),
            "scheduled_tasks": len(self.schedules),
            "active_rules": [r.rule_id for r in self.rules.values() if r.enabled],
            "timestamp": datetime.now(UTC).isoformat(),
        }


if __name__ == "__main__":
    # Test the skeleton kernel
    root = Path(__file__).parent.parent
    skeleton = SkeletonKernel(root)

    print("Skeleton State:")
    print(json.dumps(skeleton.get_state(), indent=2))

    print("\nValidating operation:")
    result = skeleton.validate_operation("execute", {"action_type": "deploy", "important": True})
    print(json.dumps(asdict(result), indent=2))

    print("\nHierarchy for 01_BRAIN:")
    print(json.dumps(skeleton.get_hierarchy("01_BRAIN"), indent=2))

    print("\nGranting permission:")
    perm = skeleton.grant_permission("06_MUSCLE", "filesystem", PermissionLevel.WRITE)
    print(f"Granted: {perm.subsystem} -> {perm.resource} ({perm.level.name})")

    print("\nChecking permission:")
    has_perm = skeleton.check_permission("06_MUSCLE", "filesystem", PermissionLevel.READ)
    print(f"06_MUSCLE has READ on filesystem: {has_perm}")
