"""Macroeconomic Scanner — Economic indicators and market monitoring

Tracks macroeconomic indicators, market conditions, and
financial signals relevant to AMOS operations.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class IndicatorType(Enum):
    """Types of economic indicators."""

    INFLATION = "inflation"
    GDP_GROWTH = "gdp_growth"
    INTEREST_RATE = "interest_rate"
    UNEMPLOYMENT = "unemployment"
    MARKET_INDEX = "market_index"
    CURRENCY = "currency"
    COMMODITY = "commodity"


@dataclass
class EconomicIndicator:
    """A single economic indicator reading."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    indicator_type: IndicatorType = IndicatorType.MARKET_INDEX
    name: str = ""
    value: float = 0.0
    unit: str = ""
    region: str = "global"  # global, US, EU, APAC, etc.
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    trend: str = "stable"  # rising, falling, stable
    volatility: float = 0.0  # 0-1 scale
    source: str = ""
    confidence: float = 0.8  # 0-1 scale

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "indicator_type": self.indicator_type.value,
        }


@dataclass
class MarketSignal:
    """A market signal or alert."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    signal_type: str = ""  # bullish, bearish, volatile, stable
    asset_class: str = ""  # equities, bonds, commodities, crypto
    description: str = ""
    severity: int = 5  # 1-10
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    related_indicators: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MacroeconomicScanner:
    """Scans and tracks macroeconomic conditions.

    Monitors economic indicators, market signals, and
    provides economic context for AMOS decisions.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.indicators: list[EconomicIndicator] = []
        self.signals: list[MarketSignal] = []

        self._load_data()

        # Initialize with sample data if empty
        if not self.indicators:
            self._init_sample_data()

    def _load_data(self):
        """Load economic data from disk."""
        data_file = self.data_dir / "macroeconomic_data.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for ind_data in data.get("indicators", []):
                    ind = EconomicIndicator(
                        id=ind_data["id"],
                        indicator_type=IndicatorType(ind_data["indicator_type"]),
                        name=ind_data["name"],
                        value=ind_data["value"],
                        unit=ind_data["unit"],
                        region=ind_data["region"],
                        timestamp=ind_data["timestamp"],
                        trend=ind_data["trend"],
                        volatility=ind_data["volatility"],
                        source=ind_data["source"],
                        confidence=ind_data["confidence"],
                    )
                    self.indicators.append(ind)

                for sig_data in data.get("signals", []):
                    sig = MarketSignal(**sig_data)
                    self.signals.append(sig)
            except Exception as e:
                print(f"[MACRO] Error loading data: {e}")

    def save(self):
        """Save economic data to disk."""
        data_file = self.data_dir / "macroeconomic_data.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "indicators": [i.to_dict() for i in self.indicators],
            "signals": [s.to_dict() for s in self.signals],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def _init_sample_data(self):
        """Initialize with sample economic indicators."""
        samples = [
            EconomicIndicator(
                indicator_type=IndicatorType.INFLATION,
                name="CPI Inflation Rate",
                value=3.2,
                unit="percent",
                region="US",
                trend="stable",
                source="BLS",
            ),
            EconomicIndicator(
                indicator_type=IndicatorType.INTEREST_RATE,
                name="Federal Funds Rate",
                value=5.25,
                unit="percent",
                region="US",
                trend="stable",
                source="FED",
            ),
            EconomicIndicator(
                indicator_type=IndicatorType.MARKET_INDEX,
                name="S&P 500",
                value=4200.0,
                unit="points",
                region="US",
                trend="rising",
                volatility=0.15,
                source="Yahoo Finance",
            ),
            EconomicIndicator(
                indicator_type=IndicatorType.CURRENCY,
                name="USD/EUR",
                value=0.92,
                unit="EUR",
                region="global",
                trend="stable",
                source="Forex",
            ),
        ]

        self.indicators.extend(samples)
        self.save()

    def add_indicator(self, indicator: EconomicIndicator) -> EconomicIndicator:
        """Add a new economic indicator reading."""
        self.indicators.append(indicator)
        self.save()
        return indicator

    def scan(self) -> dict[str, Any]:
        """Scan current economic conditions and generate signals."""
        # Analyze trends
        self._analyze_trends()

        # Generate signals based on conditions
        signals = self._generate_signals()

        return {
            "scan_time": datetime.now(UTC).isoformat(),
            "indicators_tracked": len(self.indicators),
            "signals_generated": len(signals),
            "signals": [s.to_dict() for s in signals],
            "summary": self._get_summary(),
        }

    def _analyze_trends(self):
        """Analyze trends in recent indicators."""
        # Group by name and region
        by_key = {}
        for ind in self.indicators:
            key = (ind.name, ind.region)
            if key not in by_key:
                by_key[key] = []
            by_key[key].append(ind)

        # Analyze each group
        for key, inds in by_key.items():
            if len(inds) >= 2:
                # Sort by timestamp
                inds.sort(key=lambda x: x.timestamp)
                recent = inds[-2:]

                if recent[1].value > recent[0].value * 1.02:
                    recent[1].trend = "rising"
                elif recent[1].value < recent[0].value * 0.98:
                    recent[1].trend = "falling"
                else:
                    recent[1].trend = "stable"

    def _generate_signals(self) -> list[MarketSignal]:
        """Generate market signals based on conditions."""
        new_signals = []

        # Check for high volatility
        high_vol = [i for i in self.indicators if i.volatility > 0.2]
        if high_vol:
            sig = MarketSignal(
                signal_type="volatile",
                asset_class="multi-asset",
                description=f"High volatility detected in {len(high_vol)} indicators",
                severity=6,
                related_indicators=[i.id for i in high_vol],
            )
            new_signals.append(sig)
            self.signals.append(sig)

        # Check for inflation concerns
        inflation = [
            i
            for i in self.indicators
            if i.indicator_type == IndicatorType.INFLATION and i.value > 4.0
        ]
        if inflation:
            sig = MarketSignal(
                signal_type="bearish",
                asset_class="bonds",
                description=f"Elevated inflation: {inflation[0].value}%",
                severity=7,
                related_indicators=[i.id for i in inflation],
            )
            new_signals.append(sig)
            self.signals.append(sig)

        self.save()
        return new_signals

    def _get_summary(self) -> dict[str, Any]:
        """Get summary of current economic conditions."""
        by_type = {}
        for ind in self.indicators:
            t = ind.indicator_type.value
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(ind.to_dict())

        recent_signals = sorted(
            self.signals,
            key=lambda x: x.timestamp,
            reverse=True,
        )[:5]

        return {
            "by_indicator_type": by_type,
            "recent_signals": [s.to_dict() for s in recent_signals],
            "overall_stability": self._calculate_stability(),
        }

    def _calculate_stability(self) -> str:
        """Calculate overall market stability."""
        if not self.indicators:
            return "unknown"

        volatilities = [i.volatility for i in self.indicators if i.volatility > 0]
        if not volatilities:
            return "stable"

        avg_vol = sum(volatilities) / len(volatilities)
        if avg_vol > 0.3:
            return "unstable"
        elif avg_vol > 0.15:
            return "moderate"
        return "stable"

    def get_indicator_history(
        self,
        name: str,
        region: str,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """Get historical data for an indicator."""
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()

        matching = [
            i.to_dict()
            for i in self.indicators
            if i.name == name and i.region == region and i.timestamp > cutoff
        ]

        return sorted(matching, key=lambda x: x["timestamp"])

    def get_economic_context(self) -> dict[str, Any]:
        """Get current economic context for decision making."""
        return {
            "scan_time": datetime.now(UTC).isoformat(),
            "stability": self._calculate_stability(),
            "indicator_count": len(self.indicators),
            "active_signals": len(
                [s for s in self.signals if not s.description.startswith("Resolved")]
            ),
            "key_metrics": self._get_key_metrics(),
        }

    def _get_key_metrics(self) -> dict[str, float]:
        """Get key economic metrics."""
        metrics = {}

        # Latest values for key indicators
        for ind in sorted(self.indicators, key=lambda x: x.timestamp, reverse=True):
            if ind.name not in metrics:
                metrics[ind.name] = ind.value

        return metrics


# Global instance
_SCANNER: Optional[MacroeconomicScanner] = None


def get_macro_scanner(data_dir: Optional[Path] = None) -> MacroeconomicScanner:
    """Get or create global macroeconomic scanner."""
    global _SCANNER
    if _SCANNER is None:
        _SCANNER = MacroeconomicScanner(data_dir)
    return _SCANNER


if __name__ == "__main__":
    print("Macroeconomic Scanner (08_WORLD_MODEL)")
    print("=" * 40)

    scanner = get_macro_scanner()

    print("\nEconomic Indicators:")
    for ind in scanner.indicators:
        print(f"  {ind.name} ({ind.region}): {ind.value} {ind.unit}")
        print(f"    Trend: {ind.trend}, Volatility: {ind.volatility:.2f}")

    print("\nScanning...")
    result = scanner.scan()
    print(f"Signals generated: {result['signals_generated']}")
    print(f"Overall stability: {result['summary']['overall_stability']}")
