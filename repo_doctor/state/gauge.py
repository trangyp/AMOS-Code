"""
Repo Doctor Ω∞ - Gauge Symmetry

Semantic equivalence under gauge transforms:
x ~ y iff semantically equivalent under compatibility transforms

Handles:
- provider/model vs provider:model notation
- Alias commands
- Relative vs absolute imports
- Compatibility properties vs canonical fields
- Multiple accepted CLI spellings

Hard no-gauge zones:
- entrypoint target path
- actual callable signature
- status truthfulness
- security sink/source path
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class GaugeTransform:
    """A gauge transformation rule."""

    name: str
    transform: Callable[[str], str]
    applies_to: list[str]


class GaugeSymmetry:
    """
    Manage gauge equivalences for semantic comparison.

    Distinguishes real drift from representation drift.
    """

    # Hard no-gauge zones - these must match exactly
    HARD_ZONES = {
        "entrypoint_target",
        "callable_signature",
        "status_truth",
        "security_sink_source",
    }

    def __init__(self):
        self.transforms: list[GaugeTransform] = []
        self._register_default_transforms()

    def _register_default_transforms(self) -> None:
        """Register default gauge transformations."""
        # provider/model <-> provider:model
        self.transforms.append(
            GaugeTransform(
                name="provider_separator",
                transform=lambda x: x.replace("/", ":"),
                applies_to=["model_ref", "provider_ref"],
            )
        )

        # Hyphen <-> underscore
        self.transforms.append(
            GaugeTransform(
                name="separator_normalize",
                transform=lambda x: x.replace("-", "_"),
                applies_to=["command_name", "module_name"],
            )
        )

        # Relative <-> absolute import (simplified)
        self.transforms.append(
            GaugeTransform(
                name="import_normalize",
                transform=lambda x: x.replace(".", "/"),
                applies_to=["import_path"],
            )
        )

    def are_gauge_equivalent(self, x: str, y: str, zone: str) -> bool:
        """
        Check if x and y are gauge equivalent in given zone.

        Hard zones require exact match.
        Other zones allow transforms.
        """
        if zone in self.HARD_ZONES:
            return x == y

        # Direct match
        if x == y:
            return True

        # Try transforms
        for gt in self.transforms:
            if zone in gt.applies_to or zone == "any":
                if gt.transform(x) == y or gt.transform(y) == x:
                    return True
                if gt.transform(x) == gt.transform(y):
                    return True

        return False

    def normalize(self, x: str, zone: str = "any") -> str:
        """Apply all applicable transforms to normalize."""
        result = x
        for gt in self.transforms:
            if zone in gt.applies_to or zone == "any":
                result = gt.transform(result)
        return result

    def is_hard_zone(self, zone: str) -> bool:
        """Check if zone requires exact matching."""
        return zone in self.HARD_ZONES

    def check_contract_drift(
        self, public_claim: dict[str, Any], runtime_reality: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Check for contract drift modulo gauge symmetry.

        Returns list of actual drifts (not just representation differences).
        """
        drifts = []

        for key in public_claim:
            if key not in runtime_reality:
                # Missing is always drift
                drifts.append(
                    {
                        "type": "missing",
                        "key": key,
                        "claimed": public_claim[key],
                    }
                )
            elif not self.are_gauge_equivalent(
                str(public_claim[key]), str(runtime_reality[key]), key
            ):
                drifts.append(
                    {
                        "type": "mismatch",
                        "key": key,
                        "claimed": public_claim[key],
                        "actual": runtime_reality[key],
                    }
                )

        return drifts
