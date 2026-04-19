"""AMOS Signal Processing Engine - Multi-domain signal analysis."""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SignalDomain(Enum):
    """Signal processing domain classifications."""
    TIME_FREQUENCY = "time_frequency"
    BIOLOGICAL = "biological"
    CONTROL = "control"
    COMMUNICATION = "communication"


@dataclass
class Signal:
    """Signal representation."""

    name: str
    signal_type: str
    domain: SignalDomain
    sampling_rate_hz: float = 1.0
    parameters: dict = field(default_factory=dict)


class TimeFrequencyKernel:
    """Kernel for time and frequency domain analysis."""

    def __init__(self):
        self.signals: List[dict] = []
        self.filters: List[dict] = []

    def add_signal(
        self, name: str, samples: List[float], sampling_rate_hz: float
    ) -> dict:
        """Add time-domain signal."""
        signal = {
            "name": name,
            "samples": len(samples),
            "sampling_rate_hz": sampling_rate_hz,
            "duration_s": len(samples) / sampling_rate_hz if sampling_rate_hz > 0 else 0,
        }
        self.signals.append(signal)
        return signal

    def add_filter(self, name: str, filter_type: str, cutoff_hz: float) -> dict:
        """Add filter specification."""
        filt = {
            "name": name,
            "type": filter_type,
            "cutoff_hz": cutoff_hz,
        }
        self.filters.append(filt)
        return filt

    def calculate_fft_bin_resolution(
        self, sampling_rate_hz: float, n_samples: int
    ) -> dict:
        """Calculate FFT frequency resolution."""
        if n_samples == 0:
            return {"error": "Zero samples"}
        resolution = sampling_rate_hz / n_samples
        return {
            "sampling_rate_hz": sampling_rate_hz,
            "n_samples": n_samples,
            "resolution_hz": resolution,
            "nyquist_hz": sampling_rate_hz / 2,
        }

    def compute_rms(self, samples: List[float]) -> dict:
        """Compute RMS of signal."""
        if not samples:
            return {"error": "Empty samples"}
        mean_square = sum(s**2 for s in samples) / len(samples)
        rms = math.sqrt(mean_square)
        return {
            "n_samples": len(samples),
            "rms": rms,
            "mean_square": mean_square,
        }

    def get_principles(self) -> List[str]:
        return [
            "FFT and spectral analysis",
            "Time-domain statistics",
            "Filtering (LP, HP, BP)",
            "Sampling and Nyquist theorem",
        ]


class BiologicalSignalKernel:
    """Kernel for biological signal analysis (non-clinical)."""

    def __init__(self):
        self.bio_signals: List[dict] = []
        self.hrv_metrics: List[dict] = []

    def add_ecg_signal(self, name: str, sampling_rate_hz: float) -> dict:
        """Add ECG signal reference."""
        signal = {
            "name": name,
            "type": "ECG",
            "sampling_rate_hz": sampling_rate_hz,
        }
        self.bio_signals.append(signal)
        return signal

    def add_eeg_signal(self, name: str, sampling_rate_hz: float) -> dict:
        """Add EEG signal reference."""
        signal = {
            "name": name,
            "type": "EEG",
            "sampling_rate_hz": sampling_rate_hz,
        }
        self.bio_signals.append(signal)
        return signal

    def calculate_hrv_simple(self, rr_intervals_ms: List[float]) -> dict:
        """Calculate simple HRV metrics from RR intervals."""
        if len(rr_intervals_ms) < 2:
            return {"error": "Need at least 2 RR intervals"}
        mean_rr = sum(rr_intervals_ms) / len(rr_intervals_ms)
        # Simple SDNN calculation
        variance = sum((rr - mean_rr)**2 for rr in rr_intervals_ms) / len(rr_intervals_ms)
        sdnn = math.sqrt(variance)
        return {
            "n_intervals": len(rr_intervals_ms),
            "mean_rr_ms": mean_rr,
            "sdnn_ms": sdnn,
            "note": "Non-clinical supportive use only",
        }

    def get_principles(self) -> List[str]:
        return [
            "ECG morphology and intervals",
            "EEG frequency bands (delta, theta, alpha, beta)",
            "HRV time-domain metrics",
            "Non-clinical advisory only",
        ]


class ControlSystemsKernel:
    """Kernel for control system signal analysis."""

    def __init__(self):
        self.actuators: List[dict] = []
        self.sensors: List[dict] = []

    def add_actuator(
        self, name: str, actuator_type: str, input_range: Tuple[float, float]
    ) -> dict:
        """Add actuator."""
        actuator = {
            "name": name,
            "type": actuator_type,
            "input_min": input_range[0],
            "input_max": input_range[1],
        }
        self.actuators.append(actuator)
        return actuator

    def add_sensor(
        self, name: str, sensor_type: str, output_range: Tuple[float, float]
    ) -> dict:
        """Add sensor."""
        sensor = {
            "name": name,
            "type": sensor_type,
            "output_min": output_range[0],
            "output_max": output_range[1],
        }
        self.sensors.append(sensor)
        return sensor

    def compute_pid_output(
        self, error: float, kp: float, ki: float, kd: float, dt: float
    ) -> dict:
        """Compute simple PID output (one step)."""
        # Simplified PID calculation
        p_term = kp * error
        i_term = ki * error * dt  # Simplified integral
        d_term = kd * error / dt if dt > 0 else 0  # Simplified derivative
        output = p_term + i_term + d_term
        return {
            "error": error,
            "p_term": p_term,
            "i_term": i_term,
            "d_term": d_term,
            "output": output,
            "dt": dt,
        }

    def get_principles(self) -> List[str]:
        return [
            "PID control fundamentals",
            "Sensor/actuator signal conditioning",
            "Feedback loop analysis",
            "Control system stability",
        ]


class CommunicationKernel:
    """Kernel for communication signal analysis."""

    def __init__(self):
        self.channels: List[dict] = []
        self.modulations: List[dict] = []

    def add_channel(
        self, name: str, bandwidth_hz: float, noise_level_db: float
    ) -> dict:
        """Add communication channel."""
        channel = {
            "name": name,
            "bandwidth_hz": bandwidth_hz,
            "noise_level_db": noise_level_db,
        }
        self.channels.append(channel)
        return channel

    def add_modulation(self, name: str, scheme: str, bit_rate_bps: float) -> dict:
        """Add modulation scheme."""
        modulation = {
            "name": name,
            "scheme": scheme,
            "bit_rate_bps": bit_rate_bps,
        }
        self.modulations.append(modulation)
        return modulation

    def calculate_shannon_capacity(
        self, bandwidth_hz: float, snr_db: float
    ) -> dict:
        """Calculate Shannon channel capacity."""
        snr_linear = 10**(snr_db / 10)
        capacity = bandwidth_hz * math.log2(1 + snr_linear)
        return {
            "bandwidth_hz": bandwidth_hz,
            "snr_db": snr_db,
            "capacity_bps": capacity,
            "capacity_kbps": capacity / 1000,
        }

    def get_principles(self) -> List[str]:
        return [
            "Modulation schemes (AM, FM, digital)",
            "Channel capacity (Shannon limit)",
            "Signal-to-noise ratio",
            "Bandwidth constraints",
        ]


class SignalProcessingEngine:
    """AMOS Signal Processing Engine - Multi-domain signals."""

    VERSION = "vInfinity_MAX"
    NAME = "AMOS_Signal_Processing_OMEGA"

    def __init__(self):
        self.time_freq_kernel = TimeFrequencyKernel()
        self.bio_kernel = BiologicalSignalKernel()
        self.control_kernel = ControlSystemsKernel()
        self.comm_kernel = CommunicationKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run signal processing analysis across specified domains."""
        domains = domains or [
            "time_frequency", "biological", "control", "communication"
        ]
        results: Dict[str, Any] = {}
        if "time_frequency" in domains:
            results["time_frequency"] = self._analyze_time_frequency(description)
        if "biological" in domains:
            results["biological"] = self._analyze_biological(description)
        if "control" in domains:
            results["control"] = self._analyze_control(description)
        if "communication" in domains:
            results["communication"] = self._analyze_communication(description)
        return results

    def _analyze_time_frequency(self, description: str) -> dict:
        return {
            "query": description[:100],
            "signals": len(self.time_freq_kernel.signals),
            "filters": len(self.time_freq_kernel.filters),
            "principles": self.time_freq_kernel.get_principles(),
        }

    def _analyze_biological(self, description: str) -> dict:
        return {
            "query": description[:100],
            "bio_signals": len(self.bio_kernel.bio_signals),
            "hrv_metrics": len(self.bio_kernel.hrv_metrics),
            "principles": self.bio_kernel.get_principles(),
        }

    def _analyze_control(self, description: str) -> dict:
        return {
            "query": description[:100],
            "actuators": len(self.control_kernel.actuators),
            "sensors": len(self.control_kernel.sensors),
            "principles": self.control_kernel.get_principles(),
        }

    def _analyze_communication(self, description: str) -> dict:
        return {
            "query": description[:100],
            "channels": len(self.comm_kernel.channels),
            "modulations": len(self.comm_kernel.modulations),
            "principles": self.comm_kernel.get_principles(),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with gap acknowledgment."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "",
            "## Domain Coverage",
        ]
        domain_names = {
            "time_frequency": "Time/Frequency Analysis",
            "biological": "Biological Signals (Non-clinical)",
            "control": "Control Systems",
            "communication": "Communication Signals",
        }
        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(["", f"### {display_name}"])
            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in ("principles", "query"):
                        lines.append(f"- **{key}**: {value}")
                if "principles" in data:
                    lines.append(
                        f"- **Principles**: {', '.join(data['principles'][:2])}..."
                    )
        lines.extend([
            "",
            "## Gaps and Limitations",
            "- Real-time signal acquisition not included",
            "- Biological analysis is non-clinical only",
            "- Hardware-level implementation not provided",
            "- Machine learning classification simplified",
            "",
            "## Safety Disclaimer",
            "Biomedical analysis is for informational purposes only. "
            "Never diagnose diseases. Always consult licensed professionals "
            "for medical decisions. For safety-critical engineering, "
            "require expert review.",
        ])
        return "\n".join(lines)


# Singleton instance
_signal_processing_engine: Optional[SignalProcessingEngine] = None


def get_signal_processing_engine() -> SignalProcessingEngine:
    """Get or create the Signal Processing Engine singleton."""
from __future__ import annotations

    global _signal_processing_engine
    if _signal_processing_engine is None:
        _signal_processing_engine = SignalProcessingEngine()
    return _signal_processing_engine
