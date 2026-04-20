#!/usr/bin/env python3
"""AMOS Immune Kernel - 03_IMMUNE Subsystem

Responsible for:
- Safety validation and boundary detection
- Legal and compliance checking
- Anomaly detection for operations
- Threat assessment and risk flags
- Integration with SKELETON rules
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.immune")


class ThreatLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AnomalyType(Enum):
    PATTERN_DEVIATION = "pattern_deviation"
    BOUNDARY_VIOLATION = "boundary_violation"
    RATE_ANOMALY = "rate_anomaly"
    PERMISSION_ESCALATION = "permission_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    IRREVERSIBLE_ACTION = "irreversible_action"


@dataclass
class Threat:
    """A detected threat."""

    threat_id: str
    level: ThreatLevel
    source: str
    description: str
    context: dict[str, Any]
    timestamp: str = ""
    mitigated: bool = False

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


@dataclass
class Anomaly:
    """An detected anomaly."""

    anomaly_id: str
    anomaly_type: AnomalyType
    confidence: float
    description: str
    affected_subsystem: str
    indicators: list[str]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


@dataclass
class SafetyReport:
    """Safety assessment report."""

    operation: str
    safe: bool
    threats: list[Threat]
    anomalies: list[Anomaly]
    required_confirmations: list[str]
    risk_score: float  # 0.0 - 1.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


class ImmuneKernel:
    """The Immune Kernel provides organism defense through
    safety validation, anomaly detection, and threat assessment.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.immune_path = organism_root / "03_IMMUNE"
        self.memory_path = self.immune_path / "memory"
        self.logs_path = self.immune_path / "logs"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Threat registry
        self.active_threats: dict[str, Threat] = {}
        self.threat_history: list[Threat] = []

        # Anomaly patterns
        self.baseline_patterns: dict[str, dict[str, Any]] = {}
        self.detected_anomalies: list[Anomaly] = []

        # Safety boundaries
        self.boundaries: dict[str, dict[str, Any]] = self._load_default_boundaries()

        # Compliance rules
        self.compliance_rules: dict[str, dict[str, Any]] = {}

        # Operation history for pattern analysis
        self.operation_history: list[dict[str, Any]] = []
        self.max_history = 1000

        logger.info(f"ImmuneKernel initialized at {self.immune_path}")

    def _load_default_boundaries(self) -> dict[str, dict[str, Any]]:
        """Load default safety boundaries."""
        return {
            "filesystem": {
                "protected_paths": [
                    "/etc",
                    "/usr/bin",
                    "/System",
                    "/sbin",
                    "~/.ssh",
                    "~/.aws",
                    "~/.kube",
                ],
                "max_write_size_mb": 100,
                "allowed_extensions": [".py", ".json", ".md", ".txt", ".yaml", ".yml"],
            },
            "network": {
                "allowed_ports": [80, 443, 8080, 3000],
                "blocked_hosts": [],
                "max_connections_per_minute": 60,
            },
            "execution": {
                "blocked_commands": [
                    "rm -rf /",
                    "dd if=/dev/zero",
                    ":(){ :|:& };:",
                    "mkfs",
                    "format",
                    "fdisk",
                ],
                "max_execution_time_seconds": 300,
                "require_confirmation_for": ["delete", "format", "drop", "truncate"],
            },
            "data": {
                "max_export_size_mb": 10,
                "sensitive_patterns": [
                    r"password\s*=\s*['\"][^'\"]+['\"]",
                    r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
                    r"secret\s*=\s*['\"][^'\"]+['\"]",
                    r"private[_-]?key",
                    r"BEGIN RSA PRIVATE KEY",
                ],
                "pii_patterns": [
                    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
                ],
            },
        }

    def check_safety(self, operation: str, context: dict[str, Any]) -> SafetyReport:
        """Comprehensive safety check for an operation.

        Args:
            operation: Type of operation (execute, write, delete, etc.)
            context: Operation details (command, path, data, etc.)

        Returns:
            SafetyReport with threats, anomalies, and risk assessment
        """
        threats: list[Threat] = []
        anomalies: list[Anomaly] = []
        required_confirmations: list[str] = []

        # 1. Check boundaries
        boundary_threats = self._check_boundary_violations(operation, context)
        threats.extend(boundary_threats)

        # 2. Check for irreversible actions
        if self._is_irreversible(operation, context):
            threats.append(
                Threat(
                    threat_id=self._generate_id(),
                    level=ThreatLevel.HIGH,
                    source="boundary_check",
                    description=f"Irreversible operation detected: {operation}",
                    context={"operation": operation, **context},
                )
            )
            required_confirmations.append("irreversible_action")

        # 3. Check for sensitive data exposure
        sensitive_leaks = self._check_sensitive_data(context)
        if sensitive_leaks:
            threats.append(
                Threat(
                    threat_id=self._generate_id(),
                    level=ThreatLevel.CRITICAL,
                    source="data_safety",
                    description=f"Sensitive data patterns detected: {sensitive_leaks}",
                    context={"patterns_found": sensitive_leaks},
                )
            )

        # 4. Detect anomalies
        anomaly = self._detect_anomaly(operation, context)
        if anomaly:
            anomalies.append(anomaly)

        # 5. Check rate limits
        rate_threat = self._check_rate_limit(operation)
        if rate_threat:
            threats.append(rate_threat)

        # 6. Validate against compliance
        compliance_issues = self._check_compliance(operation, context)
        required_confirmations.extend(compliance_issues)

        # Calculate risk score
        risk_score = self._calculate_risk_score(threats, anomalies)

        # Log operation
        self._log_operation(operation, context, threats, anomalies)

        # Determine if operation is safe
        safe = not any(
            t.level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] for t in threats
        ) and not any(a.confidence > 0.8 for a in anomalies)

        report = SafetyReport(
            operation=operation,
            safe=safe,
            threats=threats,
            anomalies=anomalies,
            required_confirmations=required_confirmations,
            risk_score=risk_score,
        )

        # Store threats
        for threat in threats:
            self.active_threats[threat.threat_id] = threat
            self.threat_history.append(threat)

        self.detected_anomalies.extend(anomalies)

        if not safe:
            logger.warning(f"Safety check FAILED for {operation}: risk={risk_score:.2f}")
        else:
            logger.info(f"Safety check PASSED for {operation}: risk={risk_score:.2f}")

        return report

    def _check_boundary_violations(self, operation: str, context: dict[str, Any]) -> list[Threat]:
        """Check if operation violates safety boundaries."""
        threats = []

        if operation in ["write", "delete", "modify"]:
            path = context.get("path", "")
            for protected in self.boundaries["filesystem"]["protected_paths"]:
                if protected in path:
                    threats.append(
                        Threat(
                            threat_id=self._generate_id(),
                            level=ThreatLevel.CRITICAL,
                            source="filesystem_boundary",
                            description=f"Attempted access to protected path: {protected}",
                            context={"path": path, "protected": protected},
                        )
                    )

        if operation == "execute":
            command = context.get("command", "")
            for blocked in self.boundaries["execution"]["blocked_commands"]:
                if blocked in command:
                    threats.append(
                        Threat(
                            threat_id=self._generate_id(),
                            level=ThreatLevel.CRITICAL,
                            source="execution_boundary",
                            description=f"Blocked dangerous command pattern: {blocked}",
                            context={"command": command},
                        )
                    )

        return threats

    def _is_irreversible(self, operation: str, context: dict[str, Any]) -> bool:
        """Check if operation is irreversible."""
        irreversible_ops = ["delete", "drop", "truncate", "format", "destroy"]
        if operation in irreversible_ops:
            return True

        command = context.get("command", "")
        irreversible_patterns = ["rm -rf", "drop", "delete from", "truncate"]
        return any(pattern in command.lower() for pattern in irreversible_patterns)

    def _check_sensitive_data(self, context: dict[str, Any]) -> list[str]:
        """Check for sensitive data patterns in context."""
        found_patterns = []

        # Check all string values in context
        for key, value in context.items():
            if isinstance(value, str):
                for pattern in self.boundaries["data"]["sensitive_patterns"]:
                    if re.search(pattern, value, re.IGNORECASE):
                        found_patterns.append(f"{key}: sensitive pattern match")

        return found_patterns

    def _detect_anomaly(self, operation: str, context: dict[str, Any]) -> Anomaly:
        """Detect anomalies in operation patterns."""
        # Check for unusual patterns
        recent_ops = [op for op in self.operation_history[-50:] if op["operation"] == operation]

        if len(self.operation_history) > 100:
            # Check rate
            recent_count = len(recent_ops)
            if recent_count > 20:  # More than 20 same operations in last 100
                return Anomaly(
                    anomaly_id=self._generate_id(),
                    anomaly_type=AnomalyType.RATE_ANOMALY,
                    confidence=min(0.9, recent_count / 30),
                    description=f"Unusual rate of {operation} operations",
                    affected_subsystem=context.get("subsystem", "unknown"),
                    indicators=[f"{recent_count} operations in recent history"],
                )

        # Check for permission escalation attempt
        if operation == "permission_change":
            return Anomaly(
                anomaly_id=self._generate_id(),
                anomaly_type=AnomalyType.PERMISSION_ESCALATION,
                confidence=0.85,
                description="Permission change operation detected",
                affected_subsystem=context.get("subsystem", "unknown"),
                indicators=["permission modification request"],
            )

        return None

    def _check_rate_limit(self, operation: str) -> Threat:
        """Check if operation exceeds rate limits."""
        recent = [op for op in self.operation_history[-60:] if op["operation"] == operation]
        if len(recent) > 30:  # More than 30 per minute
            return Threat(
                threat_id=self._generate_id(),
                level=ThreatLevel.MEDIUM,
                source="rate_limit",
                description=f"Rate limit exceeded for {operation}",
                context={"count": len(recent), "timeframe": "1 minute"},
            )
        return None

    def _check_compliance(self, operation: str, context: dict[str, Any]) -> list[str]:
        """Check compliance requirements."""
        confirmations = []

        # Check if operation requires explicit confirmation
        exec_boundary = self.boundaries["execution"]
        for trigger in exec_boundary.get("require_confirmation_for", []):
            if trigger in operation or trigger in context.get("command", ""):
                confirmations.append(f"confirmation_required:{trigger}")

        return confirmations

    def _calculate_risk_score(self, threats: list[Threat], anomalies: list[Anomaly]) -> float:
        """Calculate overall risk score."""
        score = 0.0

        # Add threat risk
        for threat in threats:
            if threat.level == ThreatLevel.CRITICAL:
                score += 0.4
            elif threat.level == ThreatLevel.HIGH:
                score += 0.3
            elif threat.level == ThreatLevel.MEDIUM:
                score += 0.15
            elif threat.level == ThreatLevel.LOW:
                score += 0.05

        # Add anomaly risk
        for anomaly in anomalies:
            score += anomaly.confidence * 0.2

        return min(1.0, score)

    def _log_operation(
        self,
        operation: str,
        context: dict[str, Any],
        threats: list[Threat],
        anomalies: list[Anomaly],
    ):
        """Log operation for pattern analysis."""
        op_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "operation": operation,
            "context_hash": self._hash_context(context),
            "threat_count": len(threats),
            "anomaly_count": len(anomalies),
        }

        self.operation_history.append(op_record)

        # Trim history
        if len(self.operation_history) > self.max_history:
            self.operation_history = self.operation_history[-self.max_history :]

    def _hash_context(self, context: dict[str, Any]) -> str:
        """Create hash of context for comparison."""
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()[:16]

    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid

        return str(uuid.uuid4())[:8]

    def mitigate_threat(self, threat_id: str) -> bool:
        """Mark a threat as mitigated."""
        if threat_id in self.active_threats:
            self.active_threats[threat_id].mitigated = True
            logger.info(f"Threat {threat_id} marked as mitigated")
            return True
        return False

    def get_active_threats(self, min_level: ThreatLevel = ThreatLevel.LOW) -> list[Threat]:
        """Get all active threats at or above specified level."""
        return [
            t
            for t in self.active_threats.values()
            if not t.mitigated and t.level.value >= min_level.value
        ]

    def get_state(self) -> dict[str, Any]:
        """Get current immune system state."""
        active = self.get_active_threats()
        return {
            "active_threats": len(active),
            "critical_threats": len([t for t in active if t.level == ThreatLevel.CRITICAL]),
            "total_threats_ever": len(self.threat_history),
            "anomalies_detected": len(self.detected_anomalies),
            "operations_checked": len(self.operation_history),
            "boundaries_defined": len(self.boundaries),
            "timestamp": datetime.now(UTC).isoformat(),
        }


if __name__ == "__main__":
    # Test the immune kernel
    root = Path(__file__).parent.parent
    immune = ImmuneKernel(root)

    print("Immune State:")
    print(json.dumps(immune.get_state(), indent=2))

    print("\n=== Test 1: Safe operation ===")
    report1 = immune.check_safety("read", {"path": "/tmp/test.txt", "subsystem": "02_SENSES"})
    print(f"Safe: {report1.safe}, Risk: {report1.risk_score:.2f}")
    print(f"Threats: {len(report1.threats)}, Anomalies: {len(report1.anomalies)}")

    print("\n=== Test 2: Dangerous operation ===")
    report2 = immune.check_safety(
        "execute", {"command": "rm -rf /important/data", "subsystem": "06_MUSCLE"}
    )
    print(f"Safe: {report2.safe}, Risk: {report2.risk_score:.2f}")
    print(f"Threats: {len(report2.threats)}")
    for t in report2.threats:
        print(f"  - {t.level.name}: {t.description}")

    print("\n=== Test 3: Protected path access ===")
    report3 = immune.check_safety(
        "write", {"path": "/etc/passwd", "data": "test", "subsystem": "06_MUSCLE"}
    )
    print(f"Safe: {report3.safe}, Risk: {report3.risk_score:.2f}")
    for t in report3.threats:
        print(f"  - {t.level.name}: {t.description}")

    print("\nFinal State:")
    print(json.dumps(immune.get_state(), indent=2))
