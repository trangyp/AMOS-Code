"""AMOS Brain Enhanced Debugging Utilities
========================================

Integrates state-of-the-art debugging tools:
- icecream: Beautiful print debugging
- rich: Rich terminal output with syntax highlighting
- built-in traceback enhancement

Usage:
    from amos_brain.debug_utils import debug, trace, pretty_print, ic

    # IceCream debugging
    ic(my_variable)  # Prints: my_variable: <value>

    # Rich pretty printing
    pretty_print(my_dict, title="My Data")

    # Function tracing
    @trace
    def my_function():
        pass
"""

import functools
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# Try to import optional debugging libraries
try:
    from icecream import ic as _ic

    ICECREAM_AVAILABLE = True
except ImportError:
    ICECREAM_AVAILABLE = False
    _ic = None

try:
    from rich import print as rich_print
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.traceback import install as install_rich_traceback

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    rich_print = print
    Console = None
    Panel = None
    Syntax = None
    Table = None

# Install rich traceback if available
if RICH_AVAILABLE:
    install_rich_traceback(show_locals=True)


def ic(*args) -> Any:
    """IceCream debugging - beautiful print debugging.

    Falls back to standard print if icecream not available.

    Usage:
        ic(my_variable)
        ic(a, b, c)
    """
    if ICECREAM_AVAILABLE and _ic:
        return _ic(*args)
    else:
        # Fallback: simple labeled print
        import inspect

        frame = inspect.currentframe().f_back
        call = inspect.getframeinfo(frame).code_context[0].strip()

        if len(args) == 1:
            print(f"DEBUG: {args[0]}")
            return args[0]
        else:
            for i, arg in enumerate(args):
                print(f"DEBUG [{i}]: {arg}")
            return args[-1] if args else None


def pretty_print(
    obj: Any, title: str = None, use_json: bool = False, theme: str = "monokai"
) -> None:
    """Pretty print any object with rich formatting.

    Args:
        obj: Object to print
        title: Optional title panel
        use_json: Format as JSON
        theme: Syntax highlighting theme
    """
    if use_json:
        import json

        obj = json.dumps(obj, indent=2, default=str, ensure_ascii=False)
        if RICH_AVAILABLE and Console:
            console = Console()
            syntax = Syntax(obj, "json", theme=theme)
            if title:
                console.print(Panel(syntax, title=title, border_style="blue"))
            else:
                console.print(syntax)
        else:
            print(f"=== {title} ===" if title else "")
            print(obj)
    else:
        if RICH_AVAILABLE and Console:
            console = Console()
            if title:
                console.print(Panel(str(obj), title=title, border_style="green"))
            else:
                console.print(obj)
        else:
            if title:
                print(f"=== {title} ===")
            print(obj)


def print_table(data: list[dict], columns: list[str] = None, title: str = None) -> None:
    """Print data as a rich table.

    Args:
        data: List of dictionaries
        columns: Column names to display (auto-detected if None)
        title: Optional table title
    """
    if not data:
        print("(No data)")
        return

    if columns is None:
        columns = list(data[0].keys())

    if RICH_AVAILABLE and Table:
        table = Table(title=title, show_header=True, header_style="bold magenta")

        for col in columns:
            table.add_column(col, style="cyan")

        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])

        if Console:
            console = Console()
            console.print(table)
    else:
        # Fallback to simple text table
        if title:
            print(f"=== {title} ===")

        # Print header
        print(" | ".join(columns))
        print("-" * (sum(len(c) for c in columns) + 3 * (len(columns) - 1)))

        # Print rows
        for row in data:
            print(" | ".join(str(row.get(col, "")) for col in columns))


def trace(func: Callable) -> Callable:
    """Decorator to trace function calls with entry/exit logging.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__

        # Log entry
        if RICH_AVAILABLE:
            rich_print(f"[green]→ ENTER:[/green] {func_name}()")
        else:
            print(f"→ ENTER: {func_name}()")

        try:
            result = func(*args, **kwargs)

            # Log exit
            if RICH_AVAILABLE:
                rich_print(f"[blue]← EXIT:[/blue] {func_name}() = {type(result).__name__}")
            else:
                print(f"← EXIT: {func_name}() = {type(result).__name__}")

            return result

        except Exception as e:
            # Log error
            if RICH_AVAILABLE:
                rich_print(f"[red]✗ ERROR:[/red] {func_name}() raised {type(e).__name__}: {e}")
            else:
                print(f"✗ ERROR: {func_name}() raised {type(e).__name__}: {e}")
            raise

    return wrapper


def debug_breakpoint(locals_dict: dict = None) -> None:
    """Enhanced breakpoint with context inspection.

    Args:
        locals_dict: Local variables to display
    """
    import inspect

    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    function = frame.f_code.co_name

    if RICH_AVAILABLE:
        console = Console()
        console.print(f"\n[red bold]BREAKPOINT[/red bold] in {filename}:{lineno} ({function})")

        if locals_dict:
            table = Table(title="Local Variables", show_header=True)
            table.add_column("Variable", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Type", style="magenta")

            for name, value in locals_dict.items():
                if not name.startswith("__"):
                    table.add_row(name, str(value)[:50], type(value).__name__)

            console.print(table)
    else:
        print(f"\n*** BREAKPOINT *** {filename}:{lineno} ({function})")

        if locals_dict:
            print("Local variables:")
            for name, value in locals_dict.items():
                if not name.startswith("__"):
                    print(f"  {name} = {value} ({type(value).__name__})")

    # Wait for user input
    try:
        input("\nPress Enter to continue...")
    except (KeyboardInterrupt, EOFError):
        pass


class DebugContext:
    """Context manager for debug profiling.

    Usage:
        with DebugContext("my_operation"):
            # code to profile
            pass
    """

    def __init__(self, name: str, verbose: bool = True):
        self.name = name
        self.verbose = verbose
        self.start_time = None

    def __enter__(self):
        import time

        self.start_time = time.time()

        if self.verbose:
            if RICH_AVAILABLE:
                rich_print(f"[yellow]▶ START:[/yellow] {self.name}")
            else:
                print(f"▶ START: {self.name}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time

        elapsed = time.time() - self.start_time

        if exc_type:
            if RICH_AVAILABLE:
                rich_print(f"[red]✗ FAILED:[/red] {self.name} ({elapsed:.3f}s)")
            else:
                print(f"✗ FAILED: {self.name} ({elapsed:.3f}s)")
                print(f"  Exception: {exc_type.__name__}: {exc_val}")
        else:
            if RICH_AVAILABLE:
                rich_print(f"[green]✓ COMPLETE:[/green] {self.name} ({elapsed:.3f}s)")
            else:
                print(f"✓ COMPLETE: {self.name} ({elapsed:.3f}s)")

        return False  # Don't suppress exceptions


def install_debug_hooks() -> None:
    """Install global debugging hooks:
    - Rich traceback handler
    - Warning filter
    - faulthandler for segfaults
    """
    import warnings

    # Configure warnings
    warnings.filterwarnings("default", category=DeprecationWarning)
    warnings.filterwarnings("default", category=ResourceWarning)

    # Enable faulthandler for segfault debugging
    try:
        import faulthandler

        faulthandler.enable()
    except ImportError:
        logger.debug("faulthandler not available")

    if RICH_AVAILABLE:
        print("[green]✓[/green] Rich traceback handler installed")

    if ICECREAM_AVAILABLE:
        print("[green]✓[/green] IceCream debugging available (use ic())")


# Initialize on import
install_debug_hooks()
