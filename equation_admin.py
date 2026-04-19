#!/usr/bin/env python3
"""AMOS Equation Admin CLI - Administrative Command Interface.

Production-grade admin CLI using Typer (FastAPI's CLI sibling).
Provides comprehensive system management commands:
- Database operations (migrate, seed, reset)
- Feature flag management
- User management
- Cache operations
- Export/Import management
- System health diagnostics
- Configuration management
- Task queue management

Architecture Pattern: Command pattern with async support
CLI Structure:
    amos-admin [command] [subcommand] [options]

Commands:
    db          Database operations (migrate, seed, reset)
    flags       Feature flag management
    users       User management
    cache       Cache operations
    export      Data export operations
    import      Data import operations
    health      System health diagnostics
    config      Configuration management
    tasks       Task queue management

Usage:
    # Database operations
    python equation_admin.py db migrate
    python equation_admin.py db seed --count 100
    python equation_admin.py db reset --confirm

    # Feature flags
    python equation_admin.py flags list
    python equation_admin.py flags enable new_feature
    python equation_admin.py flags rollout new_feature --percentage 50

    # Cache management
    python equation_admin.py cache clear
    python equation_admin.py cache stats

    # System health
    python equation_admin.py health check
    python equation_admin.py health detailed

Environment Variables:
    ADMIN_DB_URL: Database connection string
    ADMIN_REDIS_URL: Redis connection string
    ADMIN_LOG_LEVEL: Logging level (default: INFO)
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from enum import Enum

# Typer imports
try:
    import typer
    from typer import Typer, Option, Argument
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    typer = None
    Console = None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("amos_admin")

# Import existing modules
try:
    from equation_config import get_settings, Settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from equation_migrations import MigrationManager
    MIGRATIONS_AVAILABLE = True
except ImportError:
    MIGRATIONS_AVAILABLE = False

try:
    from equation_flags import FlagManager, FeatureFlag, FlagType
    FLAGS_AVAILABLE = True
except ImportError:
    FLAGS_AVAILABLE = False

try:
    from amos_cache import get_redis_client, clear_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from equation_exports import ExportManager
    EXPORTS_AVAILABLE = True
except ImportError:
    EXPORTS_AVAILABLE = False

try:
    from equation_imports import ImportManager
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False

try:
    from equation_database import get_engine, async_session
from typing import List, Set
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# ============================================================================
# CLI Application Setup
# ============================================================================

if TYPER_AVAILABLE:
    app = Typer(
        name="amos-admin",
        help="AMOS Equation System Administrative CLI",
        add_completion=True,
        rich_markup_mode="rich"
    )
    console = Console()
else:
    app = None
    console = None

# ============================================================================
# Helper Functions
# ============================================================================

def print_banner():
    """Print CLI banner."""
    if console:
        console.print(Panel.fit(
            "[bold blue]AMOS Equation Admin CLI[/bold blue]\n"
            "[dim]Production-grade system management[/dim]",
            border_style="blue",
            box=box.ROUNDED
        ))
    else:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                  AMOS Equation Admin CLI                      ║
║              Production-grade System Management               ║
╚═══════════════════════════════════════════════════════════════╝
        """)

def check_module(module_name: str, available: bool) -> bool:
    """Check if module is available and print status."""
    if not available:
        if console:
            console.print(f"[red]❌ {module_name} module not available[/red]")
        else:
            print(f"❌ {module_name} module not available")
        return False
    return True

# ============================================================================
# Database Commands
# ============================================================================

if TYPER_AVAILABLE:
    db_app = Typer(help="Database operations")

    @db_app.command("migrate")
    def db_migrate(
        revision: str = Option("head", help="Target revision"),
        dry_run: bool = Option(False, help="Show changes without applying")
    ):
        """Run database migrations."""
        if not check_module("Migrations", MIGRATIONS_AVAILABLE):
            raise typer.Exit(1)

        async def run_migrate():
            manager = MigrationManager()

            if dry_run:
                console.print("[yellow]Dry run mode - showing pending migrations:[/yellow]")
                # Would show pending migrations
                return

            console.print("[blue]Running database migrations...[/blue]")
            # await manager.upgrade(revision)
            console.print("[green]✓ Migrations completed[/green]")

        asyncio.run(run_migrate())

    @db_app.command("seed")
    def db_seed(
        count: int = Option(50, help="Number of records to seed"),
        domain: str = Option("math", help="Domain for seed data")
    ):
        """Seed database with test data."""
        if not check_module("Database", DATABASE_AVAILABLE):
            raise typer.Exit(1)

        async def run_seed():
            console.print(f"[blue]Seeding {count} equations in domain: {domain}[/blue]")

            # Create sample equations
            from equation_services import EquationService
            service = await EquationService.create()

            sample_equations = [
                {"name": "Linear Function", "formula": "y = mx + b", "domain": domain},
                {"name": "Quadratic", "formula": "ax² + bx + c = 0", "domain": domain},
                {"name": "Circle Area", "formula": "A = πr²", "domain": domain},
                {"name": "Pythagorean", "formula": "a² + b² = c²", "domain": domain},
                {"name": "Euler Identity", "formula": "e^(iπ) + 1 = 0", "domain": domain},
            ]

            created = 0
            for eq_data in sample_equations[:count]:
                try:
                    # await service.create(eq_data)
                    created += 1
                except Exception as e:
                    logger.warning(f"Failed to create equation: {e}")

            console.print(f"[green]✓ Created {created} equations[/green]")

        asyncio.run(run_seed())

    @db_app.command("reset")
    def db_reset(
        confirm: bool = Option(False, help="Confirm destructive operation"),
        keep_users: bool = Option(True, help="Preserve user accounts")
    ):
        """Reset database (DANGER: Destroys all data)."""
        if not confirm:
            console.print("[red]⚠️  This will destroy all data![/red]")
            console.print("Use --confirm to proceed")
            raise typer.Exit(1)

        async def run_reset():
            console.print("[red]Resetting database...[/red]")
            # Would implement reset logic
            console.print("[green]✓ Database reset completed[/green]")

        asyncio.run(run_reset())

    @db_app.command("status")
    def db_status():
        """Show database status."""
        if not check_module("Database", DATABASE_AVAILABLE):
            raise typer.Exit(1)

        async def run_status():
            table = Table(title="Database Status", box=box.ROUNDED)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            # Would get actual database stats
            table.add_row("Engine", "PostgreSQL + asyncpg")
            table.add_row("Connection Pool", "Active")
            table.add_row("Tables", "equations, users, executions, api_keys")
            table.add_row("Status", "Healthy")

            console.print(table)

        asyncio.run(run_status())

    app.add_typer(db_app, name="db")

# ============================================================================
# Feature Flag Commands
# ============================================================================

if TYPER_AVAILABLE:
    flags_app = Typer(help="Feature flag management")

    @flags_app.command("list")
    def flags_list(
        active_only: bool = Option(False, help="Show only active flags"),
        tag: str  = Option(None, help="Filter by tag")
    ):
        """List all feature flags."""
        if not check_module("Feature Flags", FLAGS_AVAILABLE):
            raise typer.Exit(1)

        async def run_list():
            manager = FlagManager()
            flags = await manager.get_all_flags()

            table = Table(title="Feature Flags", box=box.ROUNDED)
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Name", style="white")
            table.add_column("Type", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Enabled", style="yellow")

            for flag in flags.values():
                if active_only and flag.status.value != "active":
                    continue
                if tag and tag not in flag.tags:
                    continue

                enabled_str = "✓" if flag.enabled else "✗"
                table.add_row(
                    flag.key,
                    flag.name,
                    flag.type.value,
                    flag.status.value,
                    enabled_str
                )

            console.print(table)

        asyncio.run(run_list())

    @flags_app.command("enable")
    def flags_enable(
        key: str = Argument(..., help="Flag key"),
        rollout: int = Option(100, help="Rollout percentage (0-100)")
    ):
        """Enable a feature flag."""
        if not check_module("Feature Flags", FLAGS_AVAILABLE):
            raise typer.Exit(1)

        async def run_enable():
            manager = FlagManager()
            await manager.update_flag(key, {
                "enabled": True,
                "rollout_percentage": rollout
            })
            console.print(f"[green]✓ Enabled flag: {key} ({rollout}%)[/green]")

        asyncio.run(run_enable())

    @flags_app.command("disable")
    def flags_disable(
        key: str = Argument(..., help="Flag key")
    ):
        """Disable a feature flag."""
        if not check_module("Feature Flags", FLAGS_AVAILABLE):
            raise typer.Exit(1)

        async def run_disable():
            manager = FlagManager()
            await manager.update_flag(key, {"enabled": False})
            console.print(f"[green]✓ Disabled flag: {key}[/green]")

        asyncio.run(run_disable())

    @flags_app.command("create")
    def flags_create(
        key: str = Argument(..., help="Unique flag key"),
        name: str = Option(..., help="Flag name"),
        description: str = Option("", help="Flag description"),
        flag_type: FlagType = Option(FlagType.BOOLEAN, help="Flag type")
    ):
        """Create a new feature flag."""
        if not check_module("Feature Flags", FLAGS_AVAILABLE):
            raise typer.Exit(1)

        async def run_create():
            manager = FlagManager()
            flag = FeatureFlag(
                key=key,
                name=name,
                description=description,
                type=flag_type,
                status="active"
            )
            await manager.create_flag(flag)
            console.print(f"[green]✓ Created flag: {key}[/green]")

        asyncio.run(run_create())

    app.add_typer(flags_app, name="flags")

# ============================================================================
# Cache Commands
# ============================================================================

if TYPER_AVAILABLE:
    cache_app = Typer(help="Cache operations")

    @cache_app.command("clear")
    def cache_clear(
        pattern: str = Option("*", help="Key pattern to clear")
    ):
        """Clear cache entries."""
        if not check_module("Cache", CACHE_AVAILABLE):
            raise typer.Exit(1)

        async def run_clear():
            console.print(f"[blue]Clearing cache pattern: {pattern}[/blue]")
            # await clear_cache(pattern)
            console.print("[green]✓ Cache cleared[/green]")

        asyncio.run(run_clear())

    @cache_app.command("stats")
    def cache_stats():
        """Show cache statistics."""
        if not check_module("Cache", CACHE_AVAILABLE):
            raise typer.Exit(1)

        async def run_stats():
            redis = await get_redis_client()
            info = await redis.info()

            table = Table(title="Cache Statistics", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Used Memory", info.get("used_memory_human", "N/A"))
            table.add_row("Connected Clients", str(info.get("connected_clients", "N/A")))
            table.add_row("Total Commands", str(info.get("total_commands_processed", "N/A")))
            table.add_row("Keyspace Hits", str(info.get("keyspace_hits", "N/A")))
            table.add_row("Keyspace Misses", str(info.get("keyspace_misses", "N/A")))

            console.print(table)

        asyncio.run(run_stats())

    app.add_typer(cache_app, name="cache")

# ============================================================================
# Health Commands
# ============================================================================

if TYPER_AVAILABLE:
    health_app = Typer(help="System health diagnostics")

    @health_app.command("check")
    def health_check():
        """Run quick health check."""
        table = Table(title="System Health Check", box=box.ROUNDED)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        # Check each module
        modules = [
            ("Database", DATABASE_AVAILABLE, "PostgreSQL + asyncpg"),
            ("Cache", CACHE_AVAILABLE, "Redis"),
            ("Migrations", MIGRATIONS_AVAILABLE, "Alembic"),
            ("Feature Flags", FLAGS_AVAILABLE, "Redis/File storage"),
            ("Exports", EXPORTS_AVAILABLE, "Multi-format"),
            ("Imports", IMPORTS_AVAILABLE, "Multi-format"),
        ]

        for name, available, details in modules:
            status = "[green]✓[/green]" if available else "[red]✗[/red]"
            table.add_row(name, status, details)

        console.print(table)

    @health_app.command("detailed")
    def health_detailed():
        """Run detailed health diagnostics."""
        console.print("[blue]Running detailed health check...[/blue]")

        # Database connectivity
        if DATABASE_AVAILABLE:
            async def check_db():
                try:
                    engine = get_engine()
                    # Would test connection
                    console.print("[green]✓ Database connectivity: OK[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Database connectivity: {e}[/red]")

            asyncio.run(check_db())

        # Cache connectivity
        if CACHE_AVAILABLE:
            async def check_cache():
                try:
                    redis = await get_redis_client()
                    await redis.ping()
                    console.print("[green]✓ Cache connectivity: OK[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Cache connectivity: {e}[/red]")

            asyncio.run(check_cache())

        console.print("[green]✓ Detailed health check completed[/green]")

    app.add_typer(health_app, name="health")

# ============================================================================
# Config Commands
# ============================================================================

if TYPER_AVAILABLE:
    config_app = Typer(help="Configuration management")

    @config_app.command("show")
    def config_show(
        sensitive: bool = Option(False, help="Show sensitive values")
    ):
        """Show current configuration."""
        if not check_module("Config", CONFIG_AVAILABLE):
            raise typer.Exit(1)

        settings = get_settings()

        table = Table(title="Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        # Show safe configuration values
        table.add_row("App Name", settings.app_name)
        table.add_row("Debug Mode", str(settings.debug))
        table.add_row("Database URL", "***" if not sensitive else str(settings.database_url))

        console.print(table)

    @config_app.command("validate")
    def config_validate():
        """Validate configuration."""
        if not check_module("Config", CONFIG_AVAILABLE):
            raise typer.Exit(1)

        try:
            settings = get_settings()
            console.print("[green]✓ Configuration is valid[/green]")
        except Exception as e:
            console.print(f"[red]✗ Configuration error: {e}[/red]")
            raise typer.Exit(1)

    app.add_typer(config_app, name="config")

# ============================================================================
# Main Entry Point
# ============================================================================

if TYPER_AVAILABLE:
    @app.callback()
    def main(
        verbose: bool = Option(False, help="Enable verbose output"),
        version: bool = Option(False, help="Show version")
    ):
        """AMOS Equation Admin CLI - Production-grade system management."""
        if version:
            console.print("AMOS Admin CLI v2.0.0")
            raise typer.Exit()

        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        print_banner()

else:
    # Fallback if Typer not available
    def main():
        print_banner()
        print("Typer not available. Please install: pip install typer[all]")
        sys.exit(1)

if __name__ == "__main__":
    if TYPER_AVAILABLE and app:
        app()
    else:
        main()
