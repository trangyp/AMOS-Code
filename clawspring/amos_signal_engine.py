"""AMOS Signal Processing Engine - Multi-domain signal analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from amos_runtime import get_runtime


@dataclass
class SignalAnalysis:
    """Result from signal processing domain analysis."""

    domain: str
    input_data: str
    findings: list[dict]
    confidence: float
    limitations: list[str]
    law_compliance: dict
    gap_acknowledgment: str


class TimeFrequencyKernel:
    """Time and frequency domain signal analysis."""

    def analyze(self, input_data: str) -> SignalAnalysis:
        """Analyze time/frequency domain aspects."""
        findings = []

        tf_indicators = {
            "time_domain": ["time domain", "temporal", "waveform", "sample", "timestamp"],
            "frequency_domain": ["frequency", "spectrum", "fft", "fourier", "harmonic"],
            "time_frequency": ["wavelet", "stft", "spectrogram", "time-frequency"],
            "sampling": ["sampling", "nyquist", "aliasing", "rate", "resolution"],
        }

        for category, terms in tf_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append({
                    "category": category,
                    "detected_terms": matches,
                    "signal_principles": self._get_principles(category),
                })

        return SignalAnalysis(
            domain="time_frequency",
            input_data=input_data,
            findings=findings,
            confidence=0.75 if findings else 0.3,
            limitations=[
                "No actual signal processing",
                "No FFT or spectral analysis",
                "Conceptual framework only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Signal analysis is conceptual pattern matching. "
                "No DSP algorithms. No spectral computation. Not signal processing."
            ),
        )

    def _get_principles(self, category: str) -> list[str]:
        """Get signal principles for category."""
        principles = {
            "time_domain": ["Sampling theorem", "Convolution", "Impulse response"],
            "frequency_domain": ["Fourier transform", "Spectral analysis", "Bandwidth"],
            "time_frequency": ["Uncertainty principle", "Windowing", "Resolution tradeoffs"],
            "sampling": ["Nyquist criterion", "Aliasing", "Quantization"],
        }
        return principles.get(category, [])


class BiologicalSignalsKernel:
    """Biomedical signal analysis - ECG, EEG, EMG, etc."""

    SAFETY_WARNINGS = [
        "Supportive analysis only - non-clinical",
        "Not for diagnostic use",
        "Require expert medical review for health decisions",
    ]

    def analyze(self, input_data: str) -> SignalAnalysis:
        """Analyze biological signal aspects."""
        findings = []

        bio_indicators = {
            "ecg": ["ecg", "ekg", "cardiac", "heart", "electrocardiogram"],
            "eeg": ["eeg", "brain", "neural", "electroencephalogram", "cortical"],
            "emg": ["emg", "muscle", "electromyogram", "motor unit"],
            "physiological": ["respiration", "hrv", "blood pressure", "temperature"],
            "imaging": ["mri", "fmri", "pet", "ct", "ultrasound", "eit"],
        }

        for category, terms in bio_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append({
                    "category": category,
                    "detected_terms": matches,
                    "biomedical_principles": self._get_primitives(category),
                })

        # Safety warnings for biomedical content
        warnings = []
        if any(t in input_data.lower() for t in ["diagnosis", "treatment", "patient", "clinical"]):
            warnings.extend(self.SAFETY_WARNINGS)
            warnings.append("SAFETY: For medical decisions, consult qualified healthcare professionals")

        return SignalAnalysis(
            domain="biological_signals",
            input_data=input_data,
            findings=findings + [{"type": "safety_warnings", "warnings": warnings}] if warnings else findings,
            confidence=0.7 if findings else 0.25,
            limitations=[
                "No biomedical signal processing",
                "No clinical validation",
                "Non-clinical analysis only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Biomedical analysis is structural pattern matching. "
                "No clinical validation. Not medical analysis. "
                "SUPPORTIVE ONLY - NOT FOR DIAGNOSIS."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get biomedical primitives for category."""
        primitives = {
            "ecg": ["P-QRS-T", "Rhythm analysis", "HRV metrics"],
            "eeg": ["Band power", "Event-related potentials", "Connectivity"],
            "emg": ["Motor unit recruitment", "Fatigue detection", "Force estimation"],
            "physiological": ["Autonomic balance", "Homeostasis", "Adaptation"],
            "imaging": ["Contrast mechanisms", "Resolution", "Artifacts"],
        }
        return primitives.get(category, [])


class ControlSystemsKernel:
    """Control signals and automation analysis."""

    def analyze(self, input_data: str) -> SignalAnalysis:
        """Analyze control system aspects."""
        findings = []

        control_indicators = {
            "feedback": ["feedback", "control loop", "pid", "regulator", "setpoint"],
            "actuation": ["actuator", "motor", "servo", "pneumatic", "hydraulic"],
            "sensing": ["sensor", "transducer", "encoder", "imu", "gyroscope"],
            "state_space": ["state space", "observability", "controllability", "kalman"],
            "stability": ["stability", "bode", "nyquist", "root locus", "margin"],
        }

        for category, terms in control_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append({
                    "category": category,
                    "detected_terms": matches,
                    "control_principles": self._get_primitives(category),
                })

        return SignalAnalysis(
            domain="control_systems",
            input_data=input_data,
            findings=findings,
            confidence=0.75 if findings else 0.3,
            limitations=[
                "No control system simulation",
                "No stability analysis",
                "Framework guidance only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Control analysis is conceptual pattern matching. "
                "No simulations. No stability analysis. Not control engineering."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get control primitives for category."""
        primitives = {
            "feedback": ["Negative feedback", "Loop gain", "Bandwidth"],
            "actuation": ["Actuator dynamics", "Saturation", "Response time"],
            "sensing": ["Sensor fusion", "Noise characteristics", "Calibration"],
            "state_space": ["State estimation", "Observer design", "Pole placement"],
            "stability": ["Phase margin", "Gain margin", "BIBO stability"],
        }
        return primitives.get(category, [])


class CommunicationSignalsKernel:
    """Communication and networking signal analysis."""

    def analyze(self, input_data: str) -> SignalAnalysis:
        """Analyze communication signal aspects."""
        findings = []

        comm_indicators = {
            "modulation": ["modulation", "demodulation", "am", "fm", "pm", "qam"],
            "coding": ["encoding", "compression", "channel coding", "error correction"],
            "wireless": ["rf", "wireless", "antenna", "propagation", "fading"],
            "optical": ["optical", "fiber", "laser", "photonic", "coherent"],
            "networking": ["network", "protocol", "packet", "latency", "throughput"],
        }

        for category, terms in comm_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append({
                    "category": category,
                    "detected_terms": matches,
                    "communication_primitives": self._get_primitives(category),
                })

        return SignalAnalysis(
            domain="communication_signals",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.25,
            limitations=[
                "No signal simulation",
                "No channel modeling",
                "Conceptual guidance only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Communication analysis is pattern matching. "
                "No channel models. No BER calculations. Not communications engineering."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get communication primitives for category."""
        primitives = {
            "modulation": ["Constellation", "Symbol rate", "Spectral efficiency"],
            "coding": ["Shannon limit", "Code rate", "Hamming distance"],
            "wireless": ["Path loss", "Multipath", "Diversity"],
            "optical": ["Dispersion", "Attenuation", "Coherent detection"],
            "networking": ["Protocol stack", "QoS", "Congestion control"],
        }
        return primitives.get(category, [])


class AMOSSignalEngine:
    """Unified signal processing engine for multi-domain signal analysis."""

    DOMAINS = {
        "time_frequency": TimeFrequencyKernel,
        "biological": BiologicalSignalsKernel,
        "control": ControlSystemsKernel,
        "communication": CommunicationSignalsKernel,
    }

    def __init__(self):
        self.runtime = get_runtime()
        self.kernels: dict[str, Any] = {}
        self._init_kernels()

    def _init_kernels(self):
        """Initialize all signal processing kernels."""
        for domain, kernel_class in self.DOMAINS.items():
            self.kernels[domain] = kernel_class()

    def analyze(
        self,
        description: str,
        domains: list[str] | None = None,
    ) -> dict[str, SignalAnalysis]:
        """Run signal processing analysis across specified domains."""
        domains = domains or list(self.DOMAINS.keys())
        results = {}

        for domain in domains:
            if domain in self.kernels:
                kernel = self.kernels[domain]
                results[domain] = kernel.analyze(description)

        return results

    def get_findings_summary(self, results: dict[str, SignalAnalysis]) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Signal Processing Analysis Summary",
            "",
            f"Domains analyzed: {len(results)}",
            f"Overall confidence: {sum(r.confidence for r in results.values())/len(results):.2f}",
            "",
            "⚠️ SAFETY NOTICE:",
            "⚠️ No actual signal processing - conceptual analysis only",
            "⚠️ Biomedical signals: SUPPORTIVE ONLY - NOT FOR DIAGNOSIS",
            "⚠️ Control systems: Framework guidance only - no simulations",
            "⚠️ For safety-critical decisions, consult domain experts",
            "",
            "## Findings by Domain",
            "",
        ]

        for domain, analysis in results.items():
            lines.extend([
                f"### {domain.upper().replace('_', ' ')}",
                f"Confidence: {analysis.confidence:.2f}",
                f"Findings: {len([f for f in analysis.findings if f.get('type') != 'safety_warnings'])}",
                "",
            ])

            for finding in analysis.findings:
                if finding.get("type") == "safety_warnings":
                    for warning in finding.get("warnings", []):
                        lines.append(f"⚠️ {warning}")
                else:
                    cat = finding.get("category", "general")
                    lines.append(f"- **{cat}**: {finding.get('detected_terms', [])}")
                    principles = finding.get("signal_principles") or finding.get("biomedical_principles") or finding.get("control_principles") or finding.get("communication_principles")
                    if principles:
                        lines.append(f"  Principles: {', '.join(principles[:3])}")
            lines.append("")

        # Limitations section
        lines.extend([
            "## Limitations",
            "",
        ])
        all_limitations = set()
        for analysis in results.values():
            all_limitations.update(analysis.limitations)
        for limitation in all_limitations:
            lines.append(f"- {limitation}")

        # Law compliance
        lines.extend([
            "",
            "## Law Compliance",
            "",
        ])
        for domain, analysis in results.items():
            compliant = sum(1 for v in analysis.law_compliance.values() if v)
            total = len(analysis.law_compliance)
            lines.append(f"- {domain}: {compliant}/{total} laws")

        # Gap acknowledgment
        lines.extend([
            "",
            "## Gap Acknowledgment",
            "GAP: Signal analysis is structural pattern matching, not signal processing.",
            "No DSP. No simulations. No spectral analysis. No clinical validation.",
            "SUPPORTIVE ANALYSIS ONLY - NOT FOR ENGINEERING OR MEDICAL DECISIONS.",
            "Domain experts required for all technical implementations.",
        ])

        return "\n".join(lines)


# Singleton
_signal_engine: AMOSSignalEngine | None = None


def get_signal_engine() -> AMOSSignalEngine:
    """Get singleton signal processing engine."""
    global _signal_engine
    if _signal_engine is None:
        _signal_engine = AMOSSignalEngine()
    return _signal_engine


def analyze_signals(
    description: str,
    domains: list[str] | None = None,
) -> dict[str, SignalAnalysis]:
    """Quick helper for signal processing analysis."""
    return get_signal_engine().analyze(description, domains)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS SIGNAL PROCESSING ENGINE TEST")
    print("=" * 60)

    engine = get_signal_engine()

    # Test multi-domain analysis
    test_input = (
        "Design a system for processing ECG signals with real-time "
        "QRS detection and wireless transmission using RF modulation. "
        "Include feedback control for adaptive filtering."
    )

    print(f"\nInput: {test_input[:70]}...")

    results = engine.analyze(test_input)

    print(f"\nAnalyzed {len(results)} signal domains:")
    for domain, analysis in results.items():
        findings_count = len([f for f in analysis.findings if f.get("type") != "safety_warnings"])
        print(f"  - {domain}: {findings_count} findings, confidence={analysis.confidence:.2f}")

    # Full summary
    print("\n" + "=" * 60)
    print(engine.get_findings_summary(results))

    print("\n" + "=" * 60)
    print("Signal Processing Engine: OPERATIONAL")
    print("=" * 60)
    print("\nAll 4 signal domains active: Time/Freq, Biological, Control, Communication")
    print("SAFETY: Biomedical is supportive only. No diagnosis. Engineering consult required.")
