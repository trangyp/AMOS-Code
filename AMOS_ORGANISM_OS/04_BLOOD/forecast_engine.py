"""Forecast Engine — Resource and financial forecasting

Predicts future resource needs, cashflow trends, and
provides planning scenarios.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

UTC = timezone.utc


class ForecastModel(Enum):
    """Available forecasting models."""

    LINEAR = "linear"  # Simple linear extrapolation
    AVERAGE = "average"  # Moving average
    TREND = "trend"  # Trend-based with seasonality
    CONSERVATIVE = "conservative"  # Conservative estimates


@dataclass
class Forecast:
    """A forecast result."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    metric: str = ""  # What is being forecasted
    model: ForecastModel = ForecastModel.AVERAGE
    horizon_days: int = 30
    predictions: list[dict[str, Any]] = field(default_factory=list)
    confidence_interval: float = 0.8  # 80% confidence
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    based_on_data_points: int = 0
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "model": self.model.value,
        }


class ForecastEngine:
    """Forecasting engine for resources and finances.

    Provides projections based on historical data using
    multiple forecasting models.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.forecasts: list[Forecast] = []
        self._load_forecasts()

    def _load_forecasts(self):
        """Load saved forecasts."""
        forecasts_file = self.data_dir / "forecasts.json"
        if forecasts_file.exists():
            try:
                data = json.loads(forecasts_file.read_text())
                for fc_data in data.get("forecasts", []):
                    forecast = Forecast(
                        id=fc_data["id"],
                        name=fc_data["name"],
                        metric=fc_data["metric"],
                        model=ForecastModel(fc_data["model"]),
                        horizon_days=fc_data["horizon_days"],
                        predictions=fc_data["predictions"],
                        confidence_interval=fc_data["confidence_interval"],
                        created_at=fc_data["created_at"],
                        based_on_data_points=fc_data["based_on_data_points"],
                        notes=fc_data["notes"],
                    )
                    self.forecasts.append(forecast)
            except Exception as e:
                print(f"[FORECAST] Error loading forecasts: {e}")

    def save(self):
        """Save forecasts to disk."""
        forecasts_file = self.data_dir / "forecasts.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "forecasts": [f.to_dict() for f in self.forecasts],
        }
        forecasts_file.write_text(json.dumps(data, indent=2))

    def forecast_cashflow(
        self,
        historical_data: list[dict[str, Any]],
        horizon_days: int = 30,
        model: ForecastModel = ForecastModel.AVERAGE,
    ) -> Forecast:
        """Forecast future cashflow based on historical data."""
        if not historical_data:
            return self._empty_forecast("cashflow", horizon_days)

        # Extract daily net flows
        daily_flows = []
        for entry in historical_data:
            net = entry.get("income", 0) - entry.get("expense", 0)
            daily_flows.append(net)

        predictions = self._generate_predictions(daily_flows, horizon_days, model)

        forecast = Forecast(
            name="Cashflow Forecast",
            metric="daily_net_flow",
            model=model,
            horizon_days=horizon_days,
            predictions=predictions,
            based_on_data_points=len(historical_data),
        )

        self.forecasts.append(forecast)
        self.save()
        return forecast

    def forecast_resource_usage(
        self,
        utilization_history: list[float],
        capacity: float,
        horizon_days: int = 30,
        model: ForecastModel = ForecastModel.TREND,
    ) -> Forecast:
        """Forecast resource utilization."""
        if not utilization_history:
            return self._empty_forecast("resource_utilization", horizon_days)

        predictions = self._generate_predictions(utilization_history, horizon_days, model)

        # Convert to capacity percentages
        for p in predictions:
            p["value"] = (p["value"] / capacity) * 100 if capacity > 0 else 0
            p["unit"] = "percent"

        forecast = Forecast(
            name="Resource Utilization Forecast",
            metric="utilization_percent",
            model=model,
            horizon_days=horizon_days,
            predictions=predictions,
            based_on_data_points=len(utilization_history),
        )

        self.forecasts.append(forecast)
        self.save()
        return forecast

    def forecast_budget_depletion(
        self,
        current_balance: float,
        avg_daily_spend: float,
        horizon_days: int = 90,
    ) -> Forecast:
        """Forecast when budget will be depleted."""
        if avg_daily_spend <= 0:
            return self._empty_forecast("budget_depletion", horizon_days)

        days_remaining = current_balance / avg_daily_spend

        predictions = []
        for day in range(0, horizon_days, 7):  # Weekly predictions
            projected_balance = current_balance - (avg_daily_spend * day)
            predictions.append(
                {
                    "day": day,
                    "date": (datetime.now(UTC) + timedelta(days=day)).strftime("%Y-%m-%d"),
                    "value": max(0, projected_balance),
                    "unit": "currency",
                }
            )

        forecast = Forecast(
            name="Budget Depletion Forecast",
            metric="remaining_balance",
            model=ForecastModel.LINEAR,
            horizon_days=horizon_days,
            predictions=predictions,
            based_on_data_points=1,
            notes=f"Estimated depletion in {days_remaining:.1f} days at current spend rate",
        )

        self.forecasts.append(forecast)
        self.save()
        return forecast

    def _generate_predictions(
        self,
        historical: list[float],
        horizon: int,
        model: ForecastModel,
    ) -> list[dict[str, Any]]:
        """Generate predictions based on model."""
        if not historical:
            return []

        predictions = []
        now = datetime.now(UTC)

        if model == ForecastModel.LINEAR:
            # Simple linear trend
            if len(historical) >= 2:
                trend = (historical[-1] - historical[0]) / len(historical)
            else:
                trend = 0
            base = historical[-1] if historical else 0

            for day in range(1, horizon + 1):
                value = base + (trend * day)
                predictions.append(
                    {
                        "day": day,
                        "date": (now + timedelta(days=day)).strftime("%Y-%m-%d"),
                        "value": value,
                        "confidence_low": value * 0.9,
                        "confidence_high": value * 1.1,
                    }
                )

        elif model == ForecastModel.AVERAGE:
            # Moving average
            window = min(7, len(historical))
            avg = sum(historical[-window:]) / window if window > 0 else 0

            for day in range(1, horizon + 1):
                predictions.append(
                    {
                        "day": day,
                        "date": (now + timedelta(days=day)).strftime("%Y-%m-%d"),
                        "value": avg,
                        "confidence_low": avg * 0.8,
                        "confidence_high": avg * 1.2,
                    }
                )

        elif model == ForecastModel.CONSERVATIVE:
            # Conservative: use minimum of recent values
            window = min(14, len(historical))
            conservative_val = min(historical[-window:]) if window > 0 else 0

            for day in range(1, horizon + 1):
                predictions.append(
                    {
                        "day": day,
                        "date": (now + timedelta(days=day)).strftime("%Y-%m-%d"),
                        "value": conservative_val,
                        "confidence_low": conservative_val * 0.95,
                        "confidence_high": conservative_val * 1.05,
                    }
                )

        else:  # TREND
            # Trend with slight decay/growth
            recent_avg = sum(historical[-7:]) / min(7, len(historical)) if historical else 0
            trend_factor = 1.0

            for day in range(1, horizon + 1):
                # Gradual 1% daily adjustment based on recent trend
                if len(historical) >= 2:
                    daily_change = (
                        (historical[-1] - historical[-2]) / historical[-2]
                        if historical[-2] != 0
                        else 0
                    )
                    trend_factor *= 1 + daily_change * 0.1

                value = recent_avg * trend_factor
                predictions.append(
                    {
                        "day": day,
                        "date": (now + timedelta(days=day)).strftime("%Y-%m-%d"),
                        "value": value,
                        "confidence_low": value * 0.85,
                        "confidence_high": value * 1.15,
                    }
                )

        return predictions

    def _empty_forecast(self, metric: str, horizon: int) -> Forecast:
        """Create empty forecast when no data available."""
        return Forecast(
            name=f"{metric.title()} Forecast (No Data)",
            metric=metric,
            model=ForecastModel.AVERAGE,
            horizon_days=horizon,
            predictions=[],
            notes="No historical data available for forecasting",
        )

    def get_forecast_summary(self, forecast_id: str) -> dict[str, Any]:
        """Get summary of a specific forecast."""
        for fc in self.forecasts:
            if fc.id == forecast_id:
                if not fc.predictions:
                    return {"error": "No predictions available"}

                values = [p["value"] for p in fc.predictions]
                return {
                    "forecast": fc.to_dict(),
                    "avg_predicted": sum(values) / len(values) if values else 0,
                    "min_predicted": min(values) if values else 0,
                    "max_predicted": max(values) if values else 0,
                    "prediction_count": len(fc.predictions),
                }
        return None

    def list_forecasts(self) -> list[dict[str, Any]]:
        """List all forecasts."""
        return [
            {
                "id": f.id,
                "name": f.name,
                "metric": f.metric,
                "model": f.model.value,
                "created_at": f.created_at,
            }
            for f in self.forecasts
        ]


# Global instance
_ENGINE: Optional[ForecastEngine] = None


def get_forecast_engine(data_dir: Optional[Path] = None) -> ForecastEngine:
    """Get or create global forecast engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = ForecastEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Forecast Engine (04_BLOOD)")
    print("=" * 40)

    engine = get_forecast_engine()

    # Test budget depletion forecast
    print("\nBudget Depletion Forecast:")
    fc = engine.forecast_budget_depletion(
        current_balance=500.0,
        avg_daily_spend=15.0,
        horizon_days=60,
    )
    print(f"  Forecast: {fc.name}")
    print(f"  Depletion warning: {fc.notes}")
    print(f"  Predictions: {len(fc.predictions)} weeks")
