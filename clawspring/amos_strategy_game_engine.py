"""AMOS Strategy & Game Engine - Game theory and strategic analysis."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StrategyDomain(Enum):
    """Strategy and game theory domain classifications."""
    NORMAL_FORM = "normal_form"
    DYNAMICAL = "dynamical"
    NEGOTIATION = "negotiation"


@dataclass
class Game:
    """Game representation."""

    name: str
    game_type: str
    domain: StrategyDomain
    players: List[str] = field(default_factory=list)
    parameters: dict = field(default_factory=dict)


class NormalFormKernel:
    """Kernel for normal-form game analysis."""

    def __init__(self):
        self.games: List[dict] = []
        self.players: List[dict] = []

    def add_game(self, name: str, players: int, strategies_per_player: int) -> dict:
        """Add normal-form game."""
        game = {
            "name": name,
            "players": players,
            "strategies_per_player": strategies_per_player,
        }
        self.games.append(game)
        return game

    def add_player(self, name: str, rational: bool = True) -> dict:
        """Add player."""
        player = {"name": name, "rational": rational}
        self.players.append(player)
        return player

    def nash_equilibrium_check_2x2(
        self, payoff_matrix_a: list[list[float]], payoff_matrix_b: list[list[float]]
    ) -> dict:
        """Check for pure strategy Nash equilibrium in 2x2 game."""
        # Simplified check: find best responses
        nash_found = False
        equilibria = []
        for i in range(2):
            for j in range(2):
                # Check if (i,j) is Nash
                a_payoff = payoff_matrix_a[i][j]
                b_payoff = payoff_matrix_b[i][j]
                # Player A best response to j
                a_best = a_payoff >= payoff_matrix_a[1-i][j]
                # Player B best response to i
                b_best = b_payoff >= payoff_matrix_b[i][1-j]
                if a_best and b_best:
                    equilibria.append({"strategy_a": i, "strategy_b": j})
                    nash_found = True
        return {
            "payoff_matrix_a": payoff_matrix_a,
            "payoff_matrix_b": payoff_matrix_b,
            "pure_strategy_nash": nash_found,
            "equilibria": equilibria,
        }

    def dominant_strategy_check(self, payoffs: list[list[float]]) -> dict:
        """Check for dominant strategy."""
        if len(payoffs) < 2:
            return {"error": "Need at least 2 strategies"}
        # Check if strategy 0 dominates strategy 1
        dominates = all(payoffs[0][j] >= payoffs[1][j] for j in range(len(payoffs[0])))
        strictly_dominates = all(payoffs[0][j] > payoffs[1][j] for j in range(len(payoffs[0])))
        return {
            "strategy_0_dominates": dominates,
            "strictly_dominates": strictly_dominates,
        }

    def get_principles(self) -> List[str]:
        return [
            "Normal-form games",
            "Nash equilibrium",
            "Dominant strategies",
            "Mixed strategies",
        ]


class DynamicalKernel:
    """Kernel for repeated and evolutionary games."""

    def __init__(self):
        self.repeated_games: List[dict] = []
        self.strategies: List[dict] = []

    def add_repeated_game(
        self, name: str, stage_game: str, repetitions: int, discount: float
    ) -> dict:
        """Add repeated game."""
        game = {
            "name": name,
            "stage_game": stage_game,
            "repetitions": repetitions,
            "discount_factor": discount,
        }
        self.repeated_games.append(game)
        return game

    def add_strategy(self, name: str, strategy_type: str) -> dict:
        """Add strategy (e.g., Tit-for-Tat, Grim Trigger)."""
        strategy = {"name": name, "type": strategy_type}
        self.strategies.append(strategy)
        return strategy

    def folk_theorem_viability(
        self, min_payoff: float, max_payoff: float, discount: float
    ) -> dict:
        """Check if cooperation can be sustained via Folk Theorem."""
        # Cooperation viable if discount is high enough
        viable = discount > 0.5  # Simplified threshold
        return {
            "min_payoff": min_payoff,
            "max_payoff": max_payoff,
            "discount_factor": discount,
            "cooperation_viable": viable,
            "folk_theorem_applies": viable,
        }

    def evolutionary_stable_strategy(
        self, payoff_against_itself: float, payoff_mutant: float
    ) -> dict:
        """Check if strategy is Evolutionarily Stable."""
        # ESS if payoff(against itself) > payoff(mutant against itself)
        ess = payoff_against_itself > payoff_mutant
        return {
            "payoff_against_itself": payoff_against_itself,
            "payoff_mutant": payoff_mutant,
            "is_ess": ess,
        }

    def get_principles(self) -> List[str]:
        return [
            "Repeated games",
            "Folk theorem",
            "Evolutionary game theory",
            "Learning in games",
        ]


class NegotiationKernel:
    """Kernel for bargaining and negotiation analysis."""

    def __init__(self):
        self.negotiations: List[dict] = []
        self.coalitions: List[dict] = []

    def add_negotiation(
        self, name: str, parties: int, reservation_values: List[float]
    ) -> dict:
        """Add negotiation scenario."""
        negotiation = {
            "name": name,
            "parties": parties,
            "reservation_values": reservation_values,
        }
        self.negotiations.append(negotiation)
        return negotiation

    def add_coalition(self, name: str, members: List[str], value: float) -> dict:
        """Add coalition."""
        coalition = {"name": name, "members": members, "value": value}
        self.coalitions.append(coalition)
        return coalition

    def nash_bargaining_solution(
        self, utility_a: float, utility_b: float, threat_a: float, threat_b: float
    ) -> dict:
        """Calculate Nash bargaining solution."""
        # Maximize (u_a - t_a) * (u_b - t_b) subject to u_a + u_b = 1 (normalized)
        surplus = (utility_a - threat_a) + (utility_b - threat_b)
        optimal_a = threat_a + surplus / 2
        optimal_b = threat_b + surplus / 2
        product = (optimal_a - threat_a) * (optimal_b - threat_b)
        return {
            "threat_point_a": threat_a,
            "threat_point_b": threat_b,
            "optimal_a": optimal_a,
            "optimal_b": optimal_b,
            "nash_product": product,
        }

    def shapley_value_simple(
        self, player: str, marginal_contributions: List[float]
    ) -> dict:
        """Calculate simple Shapley value (average of marginal contributions)."""
        if not marginal_contributions:
            return {"error": "No marginal contributions provided"}
        value = sum(marginal_contributions) / len(marginal_contributions)
        return {
            "player": player,
            "marginal_contributions": marginal_contributions,
            "shapley_value": value,
        }

    def get_principles(self) -> List[str]:
        return [
            "Nash bargaining",
            "Coalition formation",
            "Shapley value",
            "Reservation values",
        ]


class StrategyGameEngine:
    """AMOS Strategy & Game Engine - Game theory and strategic analysis."""

    VERSION = "vInfinity_MAX"
    NAME = "AMOS_Strategy_Game_OMEGA"

    def __init__(self):
        self.normal_form_kernel = NormalFormKernel()
        self.dynamical_kernel = DynamicalKernel()
        self.negotiation_kernel = NegotiationKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run strategic analysis across specified domains."""
        domains = domains or ["normal_form", "dynamical", "negotiation"]
        results: Dict[str, Any] = {}
        if "normal_form" in domains:
            results["normal_form"] = self._analyze_normal_form(description)
        if "dynamical" in domains:
            results["dynamical"] = self._analyze_dynamical(description)
        if "negotiation" in domains:
            results["negotiation"] = self._analyze_negotiation(description)
        return results

    def _analyze_normal_form(self, description: str) -> dict:
        return {
            "query": description[:100],
            "games": len(self.normal_form_kernel.games),
            "players": len(self.normal_form_kernel.players),
            "principles": self.normal_form_kernel.get_principles(),
        }

    def _analyze_dynamical(self, description: str) -> dict:
        return {
            "query": description[:100],
            "repeated_games": len(self.dynamical_kernel.repeated_games),
            "strategies": len(self.dynamical_kernel.strategies),
            "principles": self.dynamical_kernel.get_principles(),
        }

    def _analyze_negotiation(self, description: str) -> dict:
        return {
            "query": description[:100],
            "negotiations": len(self.negotiation_kernel.negotiations),
            "coalitions": len(self.negotiation_kernel.coalitions),
            "principles": self.negotiation_kernel.get_principles(),
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
            "normal_form": "Normal-Form Games (Nash Equilibrium, Dominance)",
            "dynamical": "Dynamical Games (Repeated, Evolutionary)",
            "negotiation": "Negotiation & Bargaining (Coalitions, Fair Division)",
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
            "- Complex multi-player games require simplification",
            "- Real-world strategy involves tacit knowledge not captured",
            "- Behavioral game theory (irrationality) not fully modeled",
            "- Computational complexity limits large-scale analysis",
            "",
            "## Safety Disclaimer",
            "Does not design strategies for physical harm or illegal activities. "
            "Does not support illegal market collusion. "
            "Strategic analysis is for educational and decision-support purposes only.",
        ])
        return "\n".join(lines)


# Singleton instance
_strategy_game_engine: Optional[StrategyGameEngine] = None


def get_strategy_game_engine() -> StrategyGameEngine:
    """Get or create the Strategy Game Engine singleton."""
from __future__ import annotations

    global _strategy_game_engine
    if _strategy_game_engine is None:
        _strategy_game_engine = StrategyGameEngine()
    return _strategy_game_engine
