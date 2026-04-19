"""Causal Architecture Intelligence Bridge.

Integrates causal reasoning with AMOS Brain cognition.

Provides API for:
- Causal graph construction
- True root cause analysis
- Spurious correlation detection
- Counterfactual reasoning
- Intervention analysis
"""


from pathlib import Path
from typing import Any, Dict, Optional

# Import causal engine
try:
    from repo_doctor.causal_architecture_engine import (
        CausalAnalysis,
        CausalArchitectureEngine,
        Intervention,
    )

    CAUSAL_AVAILABLE = True
except ImportError:
    CAUSAL_AVAILABLE = False


class CausalBridge:
    """Bridge between causal engine and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: Optional[CausalArchitectureEngine] = None

    @property
    def engine(self) -> Optional[CausalArchitectureEngine]:
        """Lazy initialization of causal engine."""
        if self._engine is None and CAUSAL_AVAILABLE:
            self._engine = CausalArchitectureEngine()
        return self._engine

    def build_causal_graph(self, metric_data: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Build causal graph for target metric."""
        if not CAUSAL_AVAILABLE or self.engine is None:
            return {"error": "causal_engine not available"}

        return self.engine.build_causal_graph([metric_data], target)

    def find_root_causes(self, symptom: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find true root causes (not just correlations)."""
        if not CAUSAL_AVAILABLE or self.engine is None:
            return {"error": "causal_engine not available"}

        causes = self.engine.find_true_root_causes(symptom, [data])
        return {
            "symptom": symptom,
            "root_causes": causes,
            "count": len(causes),
        }

    def check_spurious_correlation(self, var1: str, var2: str) -> Dict[str, Any]:
        """Check if correlation is causal or spurious."""
        if not CAUSAL_AVAILABLE or self.engine is None:
            return {"error": "causal_engine not available"}

        return self.engine.identify_spurious_correlations(var1, var2)

    def analyze_intervention(
        self, target: str, new_value: Any, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze effects of an intervention."""
        if not CAUSAL_AVAILABLE or self.engine is None:
            return {"error": "causal_engine not available"}

        intervention = Intervention(
            target_node=target,
            new_value=new_value,
            context=context,
        )
        return self.engine.analyze_intervention(intervention)

    def counterfactual(
        self,
        observation: Dict[str, Any],
        target: str,
        new_value: Any,
    ) -> Dict[str, Any]:
        """Perform counterfactual reasoning."""
        if not CAUSAL_AVAILABLE or self.engine is None:
            return {"error": "causal_engine not available"}

        intervention = Intervention(
            target_node=target,
            new_value=new_value,
            context=observation,
        )
        result = self.engine.counterfactual_analysis(observation, intervention)
        return {
            "query_id": result.query_id,
            "actual": result.actual_observation,
            "intervention": target,
            "predicted": result.predicted_outcome,
            "confidence": result.confidence,
            "assumptions": result.assumptions,
        }

    def analyze_architecture(self, metrics: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Comprehensive causal analysis."""
        if not CAUSAL_AVAILABLE or self.engine is None:
            return {"error": "causal_engine not available"}

        analysis = self.engine.analyze_architecture_causality(metrics, target)
        return {
            "analysis_id": analysis.analysis_id,
            "target": target,
            "nodes": len(analysis.causal_graph.get("nodes", [])),
            "edges": len(analysis.causal_graph.get("edges", [])),
            "root_causes": analysis.root_causes,
            "spurious": analysis.spurious_correlations,
            "interventions": analysis.interventions,
            "counterfactuals": analysis.counterfactuals,
        }

    def get_insights(self) -> Dict[str, Any]:
        """Get general causal insights."""
        if not CAUSAL_AVAILABLE or self.engine is None:
            return {"error": "causal_engine not available"}

        return {"insights": self.engine.get_causal_insights()}


def get_causal_bridge(repo_path: str | Path) -> CausalBridge:
    """Factory function to get causal bridge."""
    return CausalBridge(repo_path)
