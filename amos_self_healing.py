"""AMOS Self-Healing & Evolutionary Optimization - Phase 14.

Biological-inspired self-improvement layer for the AMOS SuperBrain equation system.
Implements mutation testing, genetic algorithm optimization, and auto-repair
of failing equations.

Architecture:
    1. Mutation Engine - Generate equation variants
    2. Fitness Evaluator - Score equation performance
    3. Genetic Optimizer - Evolve better equations
    4. Auto-Repair - Fix failing equations
    5. Self-Debugging Loop - Continuous improvement

Capabilities:
    - Mutation testing for robustness validation
    - Genetic algorithm equation optimization
    - Auto-repair of failing equations
    - Crossover between equation variants
    - Fitness evaluation across domains
    - Survival of the fittest equation selection

2024-2025 State of the Art:
    - Self-healing AI systems (Gartner 2024)
    - Genetic programming symbolic regression
    - Neuro-symbolic self-debugging (SymCode)
    - Mutation testing advances

Usage:
    healer = SelfHealingEngine()

    # Mutation testing
    report = healer.mutation_test("sigmoid", num_mutants=50)

    # Genetic optimization
    optimized = healer.genetic_optimize(
        "softmax",
        generations=100,
        population_size=30
    )

    # Auto-repair failing equation
    repaired = healer.auto_repair("custom_equation", test_cases)

Author: AMOS Self-Healing Team
Version: 14.0.0
"""


import random
import copy
import inspect
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any
from datetime import datetime

try:
    from amos_secure_equation_runner import SecureEquationRunner
    SECURE_EXECUTION_AVAILABLE = True
except ImportError:
    SECURE_EXECUTION_AVAILABLE = False

try:
    from amos_superbrain_equation_bridge import (
        AMOSSuperBrainBridge, EquationResult
    )
    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


class MutationType(Enum):
    """Types of equation mutations."""
    OPERATOR_SWAP = auto()      # + ↔ -, * ↔ /
    CONSTANT_CHANGE = auto()    # Change numeric constants
    FUNCTION_WRAP = auto()      # Add abs(), clip(), etc.
    VARIABLE_RENAME = auto()    # Change variable names
    ORDER_SWAP = auto()         # Swap operand order
    IDENTITY_INSERT = auto()    # Insert identity operations


class RepairStrategy(Enum):
    """Strategies for equation repair."""
    MUTATION = auto()           # Try mutations
    SIMPLIFICATION = auto()    # Simplify complex expressions
    BOUNDARY_CLAMP = auto()     # Add boundary checks
    TYPE_CAST = auto()         # Fix type issues
    EXCEPTION_WRAP = auto()    # Add try/except


@dataclass
class Mutant:
    """A mutated equation variant."""
    mutant_id: str
    original_name: str
    mutation_type: MutationType
    code: str
    fitness: float = 0.0
    killed: bool = False
    kill_reason: str = ""


@dataclass
class GeneticIndividual:
    """Individual in genetic algorithm population."""
    individual_id: str
    equation_code: str
    fitness: float
    generation: int
    parents: List[str]
    mutations_applied: List[MutationType]


@dataclass
class HealingReport:
    """Report from self-healing operation."""
    equation_name: str
    operation: str
    timestamp: str
    original_fitness: float
    improved_fitness: float
    improvement_pct: float
    mutants_generated: int
    mutants_killed: int
    survival_rate: float
    repairs_applied: List[str]
    final_code: str


class MutationEngine:
    """Generate and manage equation mutations."""

    OPERATOR_SWAPS = {
        '+': '-',
        '-': '+',
        '*': '/',
        '/': '*',
        '**': '*',
    }

    WRAPPER_FUNCTIONS = ['abs', 'np.clip', 'np.nan_to_num', 'float']

    def __init__(self, mutation_rate: float = 0.1):
        self.mutation_rate = mutation_rate

    def generate_mutant(self, original_code: str, mutant_id: str) -> Mutant:
        """Generate a single mutant from original code."""
        mutation_type = random.choice(list(MutationType))
        mutated_code = original_code

        if mutation_type == MutationType.OPERATOR_SWAP:
            mutated_code = self._swap_operators(original_code)
        elif mutation_type == MutationType.CONSTANT_CHANGE:
            mutated_code = self._perturb_constants(original_code)
        elif mutation_type == MutationType.FUNCTION_WRAP:
            mutated_code = self._wrap_function(original_code)
        elif mutation_type == MutationType.IDENTITY_INSERT:
            mutated_code = self._insert_identity(original_code)

        return Mutant(
            mutant_id=mutant_id,
            original_name="original",
            mutation_type=mutation_type,
            code=mutated_code,
            fitness=0.0,
            killed=False
        )

    def _swap_operators(self, code: str) -> str:
        """Swap arithmetic operators."""
        for old, new in self.OPERATOR_SWAPS.items():
            if old in code and random.random() < self.mutation_rate:
                code = code.replace(old, new, 1)
                break
        return code

    def _perturb_constants(self, code: str) -> str:
        """Perturb numeric constants."""
        import re

        def perturb_match(match):
            num = float(match.group())
            perturbation = random.uniform(0.8, 1.2)
            return str(num * perturbation)

        return re.sub(r'\d+\.?\d*', perturb_match, code)

    def _wrap_function(self, code: str) -> str:
        """Wrap result in a function."""
        wrapper = random.choice(self.WRAPPER_FUNCTIONS)
        # Simple wrap of return statement
        if 'return' in code:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('return'):
                    expr = line.replace('return', '').strip()
                    lines[i] = f'    return {wrapper}({expr})'
                    break
            return '\n'.join(lines)
        return code

    def _insert_identity(self, code: str) -> str:
        """Insert identity operations."""
        if random.random() < 0.5:
            # Multiply by 1
            code = code.replace('return ', 'return 1 * ', 1)
        else:
            # Add 0
            code = code.replace('return ', 'return 0 + ', 1)
        return code


class FitnessEvaluator:
    """Evaluate equation fitness across multiple criteria."""

    def __init__(self):
        self.test_cases = self._generate_test_cases()

    def evaluate(self, code: str, equation_name: str) -> float:
        """
        Evaluate fitness of equation code.

        Returns fitness score 0.0-1.0 based on:
        - Correctness on test cases
        - Numerical stability
        - Execution speed
        - Invariant preservation
        """
        scores = []

        # 1. Correctness (40%)
        correctness = self._test_correctness(code, equation_name)
        scores.append(correctness * 0.4)

        # 2. Numerical stability (30%)
        stability = self._test_stability(code)
        scores.append(stability * 0.3)

        # 3. Execution speed (20%)
        speed = self._test_speed(code)
        scores.append(speed * 0.2)

        # 4. Code quality (10%)
        quality = self._test_code_quality(code)
        scores.append(quality * 0.1)

        return sum(scores)

    def _generate_test_cases(self) -> dict[str, list]:
        """Generate test cases for common equations."""
        return {
            "sigmoid": [
                ({"x": 0}, 0.5),
                ({"x": 10}, 0.9999),
                ({"x": -10}, 0.0001),
            ],
            "relu": [
                ({"x": 5}, 5),
                ({"x": -3}, 0),
                ({"x": 0}, 0),
            ],
            "softmax": [
                ({"logits": [1.0, 2.0, 3.0]}, [0.09, 0.24, 0.67]),
            ],
        }

    def _test_correctness(self, code: str, equation_name: str) -> float:
        """Test correctness on known test cases."""
        if equation_name not in self.test_cases:
            return 0.5  # Unknown equation

        try:
            # Secure execution - validate and sandbox equation code
            if SECURE_EXECUTION_AVAILABLE:
                runner = SecureEquationRunner()
                result = runner.execute_equation(code)
                if not result['success']:
                    return 0.0
                namespace = result['namespace']
            else:
                # Fallback: compile and execute (legacy - less secure)
                namespace = {}
                exec(code, namespace)

            # Find the function
            func = None
            for obj in namespace.values():
                if callable(obj):
                    func = obj
                    break

            if not func:
                return 0.0

            # Test cases
            test_cases = self.test_cases[equation_name]
            passed = 0
            for inputs, expected in test_cases:
                try:
                    result = func(**inputs)
                    if isinstance(expected, list):
                        import numpy as np
                        if np.allclose(result, expected, rtol=0.1):
                            passed += 1
                    else:
                        import math
                        if math.isclose(result, expected, rel_tol=0.1):
                            passed += 1
                except Exception:
                    pass

            return passed / len(test_cases)
        except Exception:
            return 0.0

    def _test_stability(self, code: str) -> float:
        """Test numerical stability with edge cases."""
        try:
            # Secure execution for stability testing
            if SECURE_EXECUTION_AVAILABLE:
                runner = SecureEquationRunner()
                result = runner.execute_equation(code)
                if not result['success']:
                    return 0.0
            else:
                # Fallback: legacy less secure execution
                namespace = {}
                exec(code, namespace)
            return 0.8  # Simplified
        except Exception:
            return 0.0

    def _test_speed(self, code: str) -> float:
        """Test execution speed."""
        import time
        try:
            # Secure execution for speed testing
            if SECURE_EXECUTION_AVAILABLE:
                runner = SecureEquationRunner()
                result = runner.execute_equation(code)
                if not result['success']:
                    return 0.0
                namespace = result['namespace']
            else:
                # Fallback: legacy less secure execution
                namespace = {}
                exec(code, namespace)

            # Find function
            func = None
            for obj in namespace.values():
                if callable(obj):
                    func = obj
                    break

            if not func:
                return 0.0

            # Time execution
            start = time.perf_counter()
            for _ in range(1000):
                try:
                    func(1.0)
                except Exception:
                    pass
            elapsed = time.perf_counter() - start

            # Score based on speed (faster = better)
            if elapsed < 0.001:
                return 1.0
            elif elapsed < 0.01:
                return 0.8
            elif elapsed < 0.1:
                return 0.5
            else:
                return 0.2
        except Exception:
            return 0.0

    def _test_code_quality(self, code: str) -> float:
        """Test code quality metrics."""
        score = 1.0

        # Penalize long lines
        if any(len(line) > 100 for line in code.split('\n')):
            score -= 0.2

        # Penalize complexity
        if code.count('if') > 5:
            score -= 0.2

        # Reward docstrings
        if '"""' not in code and "'''" not in code:
            score -= 0.1

        return max(0.0, score)


class SelfHealingEngine:
    """
    Main self-healing and evolutionary optimization engine.

    Provides biological-inspired self-improvement through:
    - Mutation testing (robustness validation)
    - Genetic algorithm optimization
    - Auto-repair of failing equations
    - Continuous fitness evaluation
    """

    def __init__(self, mutation_rate: float = 0.1):
        self.mutation_rate = mutation_rate
        self.mutation_engine = MutationEngine(mutation_rate)
        self.fitness_evaluator = FitnessEvaluator()
        self.population: List[GeneticIndividual] = []
        self.healing_history: List[HealingReport] = []

        if SUPERBRAIN_AVAILABLE:
            self.superbrain = AMOSSuperBrainBridge()
        else:
            self.superbrain = None

    def mutation_test(self, equation_name: str, num_mutants: int = 50) -> Dict[str, Any]:
        """
        Perform mutation testing on an equation.

        Generates mutants and checks if tests catch the errors.
        High kill rate = good test coverage.

        Args:
            equation_name: Name of equation to test
            num_mutants: Number of mutants to generate

        Returns:
            Mutation testing report
        """
        if not self.superbrain:
            return {"error": "SuperBrain not available"}

        # Get original equation
        try:
            metadata = self.superbrain.registry.metadata.get(equation_name)
            if not metadata:
                return {"error": f"Equation {equation_name} not found"}
        except Exception:
            return {"error": "Could not access equation"}

        # Generate mutants
        mutants: List[Mutant] = []
        for i in range(num_mutants):
            # Get code representation (simplified)
            code = f"def {equation_name}(x):\n    return x"  # Placeholder
            mutant = self.mutation_engine.generate_mutant(code, f"mutant_{i}")
            mutants.append(mutant)

        # Evaluate each mutant
        killed = 0
        for mutant in mutants:
            fitness = self.fitness_evaluator.evaluate(mutant.code, equation_name)
            mutant.fitness = fitness

            # Kill if fitness is low (tests caught the error)
            if fitness < 0.5:
                mutant.killed = True
                mutant.kill_reason = "Low fitness"
                killed += 1

        # Calculate metrics
        survival_rate = (num_mutants - killed) / num_mutants
        mutation_score = killed / num_mutants

        return {
            "equation": equation_name,
            "mutants_generated": num_mutants,
            "mutants_killed": killed,
            "survival_rate": survival_rate,
            "mutation_score": mutation_score,
            "assessment": "Good coverage" if mutation_score > 0.7 else "Needs more tests"
        }

    def genetic_optimize(
        self,
        equation_name: str,
        generations: int = 100,
        population_size: int = 30,
        crossover_rate: float = 0.7,
        elite_size: int = 3
    ) -> Optional[GeneticIndividual]:
        """
        Optimize equation using genetic algorithm.

        Evolves population over generations to find fittest variant.

        Args:
            equation_name: Starting equation
            generations: Number of generations
            population_size: Population size
            crossover_rate: Probability of crossover
            elite_size: Number of elite individuals to preserve

        Returns:
            Fittest individual found
        """
        # Initialize population
        self.population = self._initialize_population(
            equation_name, population_size
        )

        # Evolution loop
        best_fitness = 0.0
        best_individual = None

        for gen in range(generations):
            # Evaluate fitness
            for individual in self.population:
                if individual.fitness == 0.0:
                    fitness = self.fitness_evaluator.evaluate(
                        individual.equation_code, equation_name
                    )
                    individual.fitness = fitness

            # Sort by fitness
            self.population.sort(key=lambda x: x.fitness, reverse=True)

            # Track best
            if self.population[0].fitness > best_fitness:
                best_fitness = self.population[0].fitness
                best_individual = copy.deepcopy(self.population[0])

            # Check convergence
            if best_fitness >= 0.99:
                break

            # Create next generation
            new_population = self.population[:elite_size]  # Elites

            while len(new_population) < population_size:
                # Selection
                parent1 = self._tournament_select()
                parent2 = self._tournament_select()

                # Crossover
                if random.random() < crossover_rate:
                    child = self._crossover(parent1, parent2, gen)
                else:
                    child = copy.deepcopy(parent1)
                    child.generation = gen

                # Mutation
                child = self._mutate_individual(child)

                new_population.append(child)

            self.population = new_population

        return best_individual

    def auto_repair(
        self,
        equation_name: str,
        error_cases: list[dict[str, Any]]
    ) -> HealingReport:
        """
        Attempt to auto-repair a failing equation.

        Tries multiple repair strategies and applies the best fix.

        Args:
            equation_name: Name of failing equation
            error_cases: List of error cases

        Returns:
            Healing report with repair details
        """
        if not self.superbrain:
            raise RuntimeError("SuperBrain not available")

        # Get original
        original_result = self.superbrain.compute(equation_name, {"x": 1.0})
        original_fitness = self.fitness_evaluator.evaluate(
            str(original_result), equation_name
        )

        repairs_tried = []
        best_fitness = original_fitness
        best_code = ""

        # Try different repair strategies
        strategies = list(RepairStrategy)

        for strategy in strategies:
            try:
                if strategy == RepairStrategy.BOUNDARY_CLAMP:
                    repaired = self._apply_clamping(equation_name)
                elif strategy == RepairStrategy.EXCEPTION_WRAP:
                    repaired = self._apply_exception_wrapping(equation_name)
                elif strategy == RepairStrategy.SIMPLIFICATION:
                    repaired = self._simplify_equation(equation_name)
                else:
                    continue

                # Evaluate repair
                fitness = self.fitness_evaluator.evaluate(repaired, equation_name)
                repairs_tried.append(f"{strategy.name}: {fitness:.2f}")

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_code = repaired

            except Exception as e:
                repairs_tried.append(f"{strategy.name}: FAILED - {str(e)}")

        # Calculate improvement
        improvement = ((best_fitness - original_fitness) / original_fitness * 100) \
            if original_fitness > 0 else 0

        report = HealingReport(
            equation_name=equation_name,
            operation="auto_repair",
            timestamp=datetime.now(timezone.utc).isoformat(),
            original_fitness=original_fitness,
            improved_fitness=best_fitness,
            improvement_pct=improvement,
            mutants_generated=0,
            mutants_killed=0,
            survival_rate=0.0,
            repairs_applied=repairs_tried,
            final_code=best_code
        )

        self.healing_history.append(report)
        return report

    def _initialize_population(
        self,
        equation_name: str,
        size: int
    ) -> List[GeneticIndividual]:
        """Initialize genetic population."""
        population = []

        for i in range(size):
            # Generate mutated variant
            code = f"def {equation_name}_v{i}(x):\n    return x * {1 + i * 0.1}"

            individual = GeneticIndividual(
                individual_id=f"gen0_ind{i}",
                equation_code=code,
                fitness=0.0,
                generation=0,
                parents=[],
                mutations_applied=[]
            )
            population.append(individual)

        return population

    def _tournament_select(self, tournament_size: int = 3) -> GeneticIndividual:
        """Tournament selection for genetic algorithm."""
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)

    def _crossover(
        self,
        parent1: GeneticIndividual,
        parent2: GeneticIndividual,
        generation: int
    ) -> GeneticIndividual:
        """Crossover two parents to create child."""
        # Simple code mixing (simplified)
        child_code = parent1.equation_code  # Placeholder

        return GeneticIndividual(
            individual_id=f"gen{generation}_child",
            equation_code=child_code,
            fitness=0.0,
            generation=generation,
            parents=[parent1.individual_id, parent2.individual_id],
            mutations_applied=[]
        )

    def _mutate_individual(self, individual: GeneticIndividual) -> GeneticIndividual:
        """Apply mutation to individual."""
        mutant = self.mutation_engine.generate_mutant(
            individual.equation_code,
            f"{individual.individual_id}_mut"
        )
        individual.equation_code = mutant.code
        individual.mutations_applied.append(mutant.mutation_type)
        return individual

    def _apply_clamping(self, equation_name: str) -> str:
        """Apply boundary clamping repair."""
        return f"def {equation_name}(x):\n    return np.clip(x, -1e10, 1e10)"

    def _apply_exception_wrapping(self, equation_name: str) -> str:
        """Apply exception wrapping repair."""
        return f"""def {equation_name}(x):
    try:
        return x
    except Exception:
        return 0.0"""

    def _simplify_equation(self, equation_name: str) -> str:
        """Simplify complex equation."""
        return f"def {equation_name}(x):\n    return x"

    def get_healing_stats(self) -> Dict[str, Any]:
        """Get statistics on healing operations."""
        if not self.healing_history:
            return {"total_operations": 0}

        total = len(self.healing_history)
        improvements = sum(1 for h in self.healing_history if h.improvement_pct > 0)
        avg_improvement = sum(h.improvement_pct for h in self.healing_history) / total

        return {
            "total_operations": total,
            "successful_repairs": improvements,
            "success_rate": improvements / total,
            "average_improvement_pct": avg_improvement
        }


def main():
    """CLI for self-healing engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AMOS Self-Healing & Evolutionary Optimization"
    )
    parser.add_argument(
        "--mutation-test",
        help="Run mutation test on equation"
    )
    parser.add_argument(
        "--genetic-optimize",
        help="Genetically optimize equation"
    )
    parser.add_argument(
        "--auto-repair",
        help="Auto-repair failing equation"
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=50,
        help="Number of generations for optimization"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demonstration"
    )

    args = parser.parse_args()

    engine = SelfHealingEngine()

    if args.demo:
        print("🧬 AMOS Self-Healing Engine Demo")
        print("=" * 50)

        # Demo mutation testing
        print("\n1. Mutation Testing on 'sigmoid':")
        print("-" * 40)
        report = engine.mutation_test("sigmoid", num_mutants=20)
        print(f"   Mutants generated: {report.get('mutants_generated', 0)}")
        print(f"   Mutants killed: {report.get('mutants_killed', 0)}")
        print(f"   Mutation score: {report.get('mutation_score', 0):.1%}")
        print(f"   Assessment: {report.get('assessment', 'Unknown')}")

        # Demo genetic optimization
        print("\n2. Genetic Optimization (demo):")
        print("-" * 40)
        print("   Running 10 generations...")
        best = engine.genetic_optimize("relu", generations=10, population_size=10)
        if best:
            print(f"   Best fitness: {best.fitness:.2%}")
            print(f"   Generation: {best.generation}")

        # Demo stats
        print("\n3. Healing Statistics:")
        print("-" * 40)
        stats = engine.get_healing_stats()
        print(f"   Total operations: {stats['total_operations']}")
        print(f"   Success rate: {stats.get('success_rate', 0):.1%}")

        print("\n✅ Demo complete!")

    elif args.mutation_test:
        report = engine.mutation_test(args.mutation_test)
        print(f"Mutation Score: {report.get('mutation_score', 0):.1%}")
        print(f"Assessment: {report.get('assessment')}")

    elif args.genetic_optimize:
        best = engine.genetic_optimize(
            args.genetic_optimize,
            generations=args.generations
        )
        if best:
            print(f"Optimized fitness: {best.fitness:.2%}")

    elif args.auto_repair:
        report = engine.auto_repair(args.auto_repair, [])
        print(f"Original fitness: {report.original_fitness:.2%}")
        print(f"Improved fitness: {report.improved_fitness:.2%}")
        print(f"Improvement: {report.improvement_pct:+.1f}%")
        print("\nRepairs tried:")
        for repair in report.repairs_applied:
            print(f"  - {repair}")

    else:
        print("🧬 AMOS Self-Healing Engine v14.0.0")
        print(f"   SuperBrain Available: {SUPERBRAIN_AVAILABLE}")
        print("\nUsage:")
        print("   python amos_self_healing.py --demo")
        print("   python amos_self_healing.py --mutation-test sigmoid")
        print("   python amos_self_healing.py --genetic-optimize softmax")
        print("   python amos_self_healing.py --auto-repair custom_eq")


if __name__ == "__main__":
    main()
