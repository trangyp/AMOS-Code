"""AMOS Equation CLI - Command-line interface for equation library.

Usage:
    python amos_equation_cli.py list
    python amos_equation_cli.py compute softmax --params '{"x": [1.0, 2.0, 3.0]}'
    python amos_equation_cli.py patterns
    python amos_equation_cli.py explain littles_law
    python amos_equation_cli.py isomorphisms
    python amos_equation_cli.py test
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import numpy as np
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: Rich not available. Install with: pip install rich")

try:
    import typer

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    print("Error: Typer required. Install with: pip install typer")
    sys.exit(1)


from amos_equation_kernel import (
    EquationKernel,
    MathematicalPattern,
    get_equation_kernel,
)

# Initialize
console = Console() if RICH_AVAILABLE else None
app = typer.Typer(
    name="amos-equation",
    help="AMOS Equation Kernel CLI - Mathematical equation library",
    add_completion=False,
)


def get_kernel() -> EquationKernel:
    """Get or initialize the equation kernel."""
    return get_equation_kernel()


@app.command()
def list(
    pattern: str = typer.Option(
        None,
        "--pattern",
        "-p",
        help="Filter by pattern (convex_optimization, linear_systems, etc.)",
    ),
    domain: str = typer.Option(
        None, "--domain", "-d", help="Filter by domain (machine_learning, systems, etc.)"
    ),
) -> None:
    """List all available equations."""
    kernel = get_kernel()
    equations = kernel.get_all_equations()

    # Apply filters
    if pattern:
        try:
            p = MathematicalPattern(pattern)
            equations = [eq for eq in equations if eq.pattern == p]
        except ValueError:
            typer.echo(f"Invalid pattern: {pattern}", err=True)
            return

    if domain:
        equations = [eq for eq in equations if eq.domain == domain]

    if RICH_AVAILABLE and console:
        table = Table(
            title="AMOS Equation Library",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Domain", style="blue")
        table.add_column("Pattern", style="magenta")
        table.add_column("Formula", style="dim", max_width=40)

        for eq in equations:
            table.add_row(
                eq.name,
                eq.domain,
                eq.pattern.value,
                eq.formula[:40] + "..." if len(eq.formula) > 40 else eq.formula,
            )

        console.print(table)
        console.print(f"\n[dim]Showing {len(equations)} equations[/dim]")
    else:
        typer.echo(f"Available Equations ({len(equations)}):")
        typer.echo("-" * 80)
        for eq in equations:
            typer.echo(f"{eq.name:30} | {eq.domain:20} | {eq.pattern.value:20}")


@app.command()
def compute(
    equation: str = typer.Argument(..., help="Equation name"),
    params: str = typer.Option(
        ..., "--params", "-p", help="JSON parameters, e.g., '{\"x\": [1.0, 2.0]}'"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Compute an equation with given parameters."""
    kernel = get_kernel()

    # Parse JSON parameters
    try:
        parameters = json.loads(params)
        # Convert lists to numpy arrays where appropriate
        for key, value in parameters.items():
            if isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                parameters[key] = np.array(value)
    except json.JSONDecodeError as e:
        typer.echo(f"Invalid JSON parameters: {e}", err=True)
        raise typer.Exit(1)

    # Execute equation
    result = kernel.execute(equation, parameters)

    if result.value is None:
        typer.echo(f"Error: {result.errors[0] if result.errors else 'Unknown error'}", err=True)
        raise typer.Exit(1)

    # Output result
    if RICH_AVAILABLE and console:
        # Main result panel
        value_str = str(result.value)
        if hasattr(result.value, "tolist"):
            value_str = str(result.value.tolist())

        result_panel = Panel(
            f"[bold green]{value_str}[/bold green]",
            title=f"Result: {equation}",
            border_style="green",
        )
        console.print(result_panel)

        # Metadata
        if verbose:
            meta_table = Table(show_header=False, box=box.SIMPLE)
            meta_table.add_column("Property", style="cyan")
            meta_table.add_column("Value", style="white")

            meta_table.add_row("Domain", result.metadata.domain)
            meta_table.add_row("Pattern", result.metadata.pattern.value)
            meta_table.add_row("Formula", result.metadata.formula)
            meta_table.add_row("Invariants Valid", str(result.invariants_valid))

            if result.errors:
                meta_table.add_row("Errors", ", ".join(result.errors))

            console.print(meta_table)

        # Invariants check
        if result.invariants_valid:
            console.print("[green]✓ All invariants satisfied[/green]")
        else:
            console.print("[red]✗ Invariant violations detected[/red]")
            for error in result.errors:
                console.print(f"  [red]- {error}[/red]")
    else:
        # Plain output
        typer.echo(f"Result: {result.value}")
        typer.echo(f"Invariants valid: {result.invariants_valid}")
        if result.errors:
            for error in result.errors:
                typer.echo(f"Error: {error}")


@app.command()
def patterns() -> None:
    """Show mathematical patterns and their equations."""
    kernel = get_kernel()

    if RICH_AVAILABLE and console:
        for pattern in MathematicalPattern:
            equations = kernel.get_by_pattern(pattern)

            panel = Panel(
                "\n".join([f"• {eq.name} [{eq.domain}]" for eq in equations]) or "No equations",
                title=f"[cyan]{pattern.value}[/cyan]",
                border_style="cyan",
            )
            console.print(panel)
    else:
        for pattern in MathematicalPattern:
            equations = kernel.get_by_pattern(pattern)
            typer.echo(f"\n{pattern.value}:")
            for eq in equations:
                typer.echo(f"  - {eq.name}")


@app.command()
def explain(
    equation: str = typer.Argument(..., help="Equation name"),
    show_formula: bool = typer.Option(True, "--formula/--no-formula", help="Show formula"),
    show_invariants: bool = typer.Option(
        True, "--invariants/--no-invariants", help="Show invariants"
    ),
) -> None:
    """Show detailed explanation of an equation."""
    kernel = get_kernel()

    # Find equation metadata
    all_eqs = kernel.get_all_equations()
    eq = next((e for e in all_eqs if e.name == equation), None)

    if not eq:
        typer.echo(f"Equation not found: {equation}", err=True)
        raise typer.Exit(1)

    if RICH_AVAILABLE and console:
        # Title
        console.print(f"\n[bold cyan]{eq.name}[/bold cyan]")
        console.print(f"[dim]{eq.description}[/dim]\n")

        # Formula
        if show_formula:
            formula_syntax = Syntax(eq.formula, "latex", theme="monokai", word_wrap=True)
            formula_panel = Panel(formula_syntax, title="Formula", border_style="blue")
            console.print(formula_panel)

        # Metadata table
        meta_table = Table(show_header=False, box=box.SIMPLE)
        meta_table.add_column("Key", style="cyan")
        meta_table.add_column("Value", style="white")

        meta_table.add_row("Domain", eq.domain)
        meta_table.add_row("Pattern", eq.pattern.value)

        # Parameters
        if eq.parameters:
            params_str = ", ".join([f"{k}: {v}" for k, v in eq.parameters.items()])
            meta_table.add_row("Parameters", params_str)

        console.print(meta_table)

        # Invariants
        if show_invariants and eq.invariants:
            invariants_panel = Panel(
                "\n".join([f"• {inv}" for inv in eq.invariants]),
                title="Invariants",
                border_style="green",
            )
            console.print(invariants_panel)

        # Related equations
        pattern_eqs = kernel.get_by_pattern(eq.pattern)
        related = [e.name for e in pattern_eqs if e.name != equation][:5]
        if related:
            related_panel = Panel(
                ", ".join(related), title="Related Equations (Same Pattern)", border_style="magenta"
            )
            console.print(related_panel)
    else:
        typer.echo(f"\n{equation}")
        typer.echo(eq.description)
        typer.echo(f"\nFormula: {eq.formula}")
        typer.echo(f"Domain: {eq.domain}")
        typer.echo(f"Pattern: {eq.pattern.value}")
        if eq.invariants:
            typer.echo("\nInvariants:")
            for inv in eq.invariants:
                typer.echo(f"  - {inv}")


@app.command()
def isomorphisms() -> None:
    """Show cross-domain equation isomorphisms."""
    kernel = get_kernel()
    isos = kernel.find_isomorphisms()

    if RICH_AVAILABLE and console:
        console.print("\n[bold cyan]Cross-Domain Isomorphisms[/bold cyan]\n")

        for iso in isos:
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column(style="green")
            table.add_column(style="white")

            table.add_row("Equation 1", iso["equation1"])
            table.add_row("Equation 2", iso["equation2"])
            table.add_row("Similarity", iso["similarity"])
            table.add_row("Description", iso["description"])

            console.print(table)
            console.print()
    else:
        typer.echo("\nCross-Domain Isomorphisms:")
        for iso in isos:
            typer.echo(f"\n{iso['equation1']} ↔ {iso['equation2']}")
            typer.echo(f"  Similarity: {iso['similarity']}")
            typer.echo(f"  {iso['description']}")


@app.command()
def test(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    equation: str = typer.Option(None, "--equation", "-e", help="Test specific equation"),
) -> None:
    """Run tests on equation implementations."""
    kernel = get_kernel()

    typer.echo("Running equation tests...\n")

    # Test specific equation or all
    if equation:
        equations = [e for e in kernel.get_all_equations() if e.name == equation]
        if not equations:
            typer.echo(f"Equation not found: {equation}", err=True)
            raise typer.Exit(1)
    else:
        equations = kernel.get_all_equations()

    results = {"passed": 0, "failed": 0, "errors": []}

    # Simple smoke tests
    test_cases = {
        "softmax": {"x": np.array([1.0, 2.0, 3.0])},
        "scaled_dot_product_attention": {
            "Q": np.array([[1.0, 0.0]]),
            "K": np.array([[1.0, 0.0]]),
            "V": np.array([[1.0]]),
        },
        "littles_law": {"arrival_rate": 10.0, "avg_time": 5.0},
        "shannon_entropy": {"probabilities": np.array([0.5, 0.5])},
        "basic_reproduction_number": {"beta": 0.5, "gamma": 0.1},
        "bloom_filter_fp_rate": {"m": 1000, "n": 100, "k": 3},
        "pid_controller": {
            "error": 1.0,
            "integral_error": 0.5,
            "derivative_error": 0.1,
            "Kp": 1.0,
            "Ki": 0.5,
            "Kd": 0.1,
        },
        "rate_monotonic_schedulability": {"tasks": [(1, 10), (2, 20)]},
    }

    for eq in equations:
        if eq.name in test_cases:
            try:
                result = kernel.execute(eq.name, test_cases[eq.name])
                if result.value is not None and result.invariants_valid:
                    results["passed"] += 1
                    if verbose:
                        typer.echo(f"  ✓ {eq.name}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{eq.name}: {result.errors}")
                    if verbose:
                        typer.echo(f"  ✗ {eq.name} - Invariant violations")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{eq.name}: {str(e)}")
                if verbose:
                    typer.echo(f"  ✗ {eq.name} - Exception: {e}")
        else:
            if verbose:
                typer.echo(f"  - {eq.name} - No test case")

    # Summary
    if RICH_AVAILABLE and console:
        console.print(f"\n[green]Passed: {results['passed']}[/green]")
        if results["failed"] > 0:
            console.print(f"[red]Failed: {results['failed']}[/red]")
            for error in results["errors"]:
                console.print(f"  [red]• {error}[/red]")
    else:
        typer.echo(f"\nPassed: {results['passed']}")
        typer.echo(f"Failed: {results['failed']}")
        if results["errors"]:
            for error in results["errors"]:
                typer.echo(f"  • {error}")

    if results["failed"] > 0:
        raise typer.Exit(1)


@app.command()
def summary() -> None:
    """Show framework summary statistics."""
    kernel = get_kernel()

    # Count equations by domain and pattern
    all_eqs = kernel.get_all_equations()
    domains: dict[str, int] = {}
    patterns: dict[str, int] = {}

    for eq in all_eqs:
        domains[eq.domain] = domains.get(eq.domain, 0) + 1
        patterns[eq.pattern.value] = patterns.get(eq.pattern.value, 0) + 1

    if RICH_AVAILABLE and console:
        console.print("\n[bold cyan]AMOS Equation Framework Summary[/bold cyan]\n")

        # Main stats
        stats_table = Table(show_header=False, box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Total Equations", str(len(all_eqs)))
        stats_table.add_row("Domains Covered", str(len(domains)))
        stats_table.add_row("Patterns Identified", str(len(patterns)))
        stats_table.add_row("Isomorphisms Found", str(len(kernel.find_isomorphisms())))

        console.print(stats_table)
        console.print()

        # Domain distribution
        domain_table = Table(title="Domain Distribution", box=box.SIMPLE)
        domain_table.add_column("Domain", style="green")
        domain_table.add_column("Count", style="white", justify="right")

        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
            domain_table.add_row(domain, str(count))

        console.print(domain_table)
        console.print()

        # Pattern distribution
        pattern_table = Table(title="Pattern Distribution", box=box.SIMPLE)
        pattern_table.add_column("Pattern", style="magenta")
        pattern_table.add_column("Count", style="white", justify="right")

        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            pattern_table.add_row(pattern, str(count))

        console.print(pattern_table)
    else:
        typer.echo("\nAMOS Equation Framework Summary")
        typer.echo("=" * 40)
        typer.echo(f"Total Equations: {len(all_eqs)}")
        typer.echo(f"Domains Covered: {len(domains)}")
        typer.echo(f"Patterns Identified: {len(patterns)}")
        typer.echo(f"Isomorphisms Found: {len(kernel.find_isomorphisms())}")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    """AMOS Equation Kernel CLI - Mathematical equation library."""
    if version:
        typer.echo("AMOS Equation CLI v6.0.0")
        raise typer.Exit()


if __name__ == "__main__":
    app()
