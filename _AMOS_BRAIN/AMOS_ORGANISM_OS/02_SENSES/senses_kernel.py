#!/usr/bin/env python3
"""AMOS Senses Kernel - 02_SENSES Subsystem

Responsible for:
- Filesystem monitoring
- Environment sensing (system load, context)
- Emotion/state input detection
- Input routing and preprocessing
"""

import json
import logging
import os
import platform
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

UTC = UTC
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.senses")


@dataclass
class SensoryInput:
    """A piece of sensory input from the environment."""

    timestamp: str
    source: str  # filesystem, system, user, environment
    input_type: str
    payload: dict[str, Any]
    priority: int = 5  # 1-10, lower is higher priority
    raw_data: str = None


@dataclass
class EnvironmentState:
    """Current state of the environment."""

    timestamp: str
    platform: str
    cwd: str
    python_version: str
    env_vars: dict[str, str]
    system_load: dict[str, float] = None


class SensesKernel:
    """The Senses Kernel monitors and processes environmental inputs."""

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.senses_path = organism_root / "02_SENSES"
        self.memory_path = self.senses_path / "memory"
        self.logs_path = self.senses_path / "logs"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Input buffer
        self.input_buffer: list[SensoryInput] = []
        self.buffer_capacity = 100

        # Registered sensors
        self.sensors: dict[str, callable] = {}

        logger.info(f"SensesKernel initialized at {self.senses_path}")

    def register_sensor(self, name: str, sensor_fn: callable) -> None:
        """Register a sensor function."""
        self.sensors[name] = sensor_fn
        logger.info(f"Registered sensor: {name}")

    def scan_filesystem(self, path: Path = None, depth: int = 2) -> dict[str, Any]:
        """Scan the filesystem for relevant files."""
        target = path or self.root
        structure = {}

        try:
            for item in target.iterdir():
                if item.is_dir() and depth > 0:
                    structure[item.name] = self.scan_filesystem(item, depth - 1)
                elif item.is_file():
                    structure[item.name] = {
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    }
        except PermissionError:
            structure["_error"] = "permission_denied"

        return structure

    def sense_environment(self) -> EnvironmentState:
        """Capture current environment state."""
        return EnvironmentState(
            timestamp=datetime.now(UTC).isoformat(),
            platform=platform.platform(),
            cwd=str(Path.cwd()),
            python_version=platform.python_version(),
            env_vars={
                k: v for k, v in os.environ.items() if k.startswith(("AMOS", "PYTHON", "PATH"))
            },
        )

    def receive_input(
        self, source: str, input_type: str, payload: dict[str, Any], priority: int = 5
    ) -> SensoryInput:
        """Receive and buffer an input."""
        # Manage buffer
        if len(self.input_buffer) >= self.buffer_capacity:
            # Remove lowest priority oldest item
            self.input_buffer.pop(0)

        input_obj = SensoryInput(
            timestamp=datetime.now(UTC).isoformat(),
            source=source,
            input_type=input_type,
            payload=payload,
            priority=priority,
        )

        self.input_buffer.append(input_obj)

        # Log
        log_file = self.logs_path / f"{datetime.now(UTC).strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(input_obj), ensure_ascii=False) + "\n")

        return input_obj

    def get_prioritized_inputs(self, max_items: int = 10) -> list[SensoryInput]:
        """Get inputs sorted by priority."""
        sorted_inputs = sorted(self.input_buffer, key=lambda x: (x.priority, x.timestamp))
        return sorted_inputs[:max_items]

    def sense_all(self) -> dict[str, Any]:
        """Run all registered sensors and return combined result."""
        results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "environment": asdict(self.sense_environment()),
            "filesystem_scan": self.scan_filesystem(depth=1),
            "buffered_inputs": len(self.input_buffer),
            "sensor_results": {},
        }

        for name, sensor_fn in self.sensors.items():
            try:
                results["sensor_results"][name] = sensor_fn()
            except Exception as e:
                results["sensor_results"][name] = {"error": str(e)}
                logger.warning(f"Sensor {name} failed: {e}")

        return results

    def detect_user_state(self, text_input: str) -> dict[str, Any]:
        """Detect emotional/cognitive state from text input.
        Simple heuristic implementation.
        """
        markers = {
            "urgency": ["urgent", "asap", "immediately", "now", "hurry"],
            "frustration": ["frustrated", "annoying", "stuck", "can't", "won't work"],
            "confusion": ["confused", "don't understand", "unclear", "what?", "how?"],
            "satisfaction": ["great", "thanks", "perfect", "awesome", "works"],
            "fatigue": ["tired", "exhausted", "sleepy", "late", "long day"],
        }

        detected = {}
        text_lower = text_input.lower()

        for state, keywords in markers.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                detected[state] = score

        # Calculate simple valence/arousal
        valence = 0.0
        arousal = 0.5

        if "satisfaction" in detected:
            valence += 0.5
        if "frustration" in detected or "confusion" in detected:
            valence -= 0.3
            arousal += 0.2
        if "urgency" in detected:
            arousal += 0.3
        if "fatigue" in detected:
            arousal -= 0.2

        return {
            "detected_markers": detected,
            "valence_estimate": max(-1.0, min(1.0, valence)),
            "arousal_estimate": max(0.0, min(1.0, arousal)),
            "recommendation": "reduce_complexity"
            if "fatigue" in detected or "confusion" in detected
            else "normal",
        }


if __name__ == "__main__":
    # Test the senses kernel
    root = Path(__file__).parent.parent
    senses = SensesKernel(root)

    # Test environment sensing
    env = senses.sense_environment()
    print("Environment State:")
    print(json.dumps(asdict(env), indent=2))

    # Test input reception
    senses.receive_input(
        source="user",
        input_type="text_query",
        payload={"text": "How do I implement this feature urgently?"},
        priority=2,
    )

    # Test state detection
    state = senses.detect_user_state("I'm confused and tired, how does this work?")
    print("\nDetected User State:")
    print(json.dumps(state, indent=2))

    # Test full sense
    print("\nFull Sense Results:")
    print(json.dumps(senses.sense_all(), indent=2, default=str))
