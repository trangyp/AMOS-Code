"""Amplitude calculation for repository state dimensions."""

from __future__ import annotations

from dataclasses import dataclass

from .basis import StateDimension


@dataclass
class StateAmplitude:
    dimension: StateDimension
    value: float
    confidence: float
    source: str = ""


class AmplitudeCalculator:
    def from_sensor_data(self, data: dict) -> dict[StateDimension, StateAmplitude]:
        return {dim: StateAmplitude(dim, 1.0, 0.9, "sensor") for dim in StateDimension}
