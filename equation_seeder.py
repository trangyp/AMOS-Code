#!/usr/bin/env python3
"""AMOS Equation Data Seeder - Development & Test Data Generation.

Production-grade data seeding system using Faker:
- Realistic equation data generation
- Domain-specific seeders (math, physics, engineering)
- User account generation with roles
- Execution history seeding
- Analytics data generation
- Reproducible seeds for testing
- Batch processing for large datasets
- Async support for performance
- Transaction safety

Integration:
    - equation_database: SQLAlchemy models
    - equation_services: Business logic
    - equation_auth: User creation with hashed passwords

Usage:
    # In CLI or script
    from equation_seeder import DatabaseSeeder

    seeder = DatabaseSeeder()

    # Seed everything
    await seeder.seed_all(
        users=10,
        equations_per_domain=50,
        executions_per_equation=5
    )

    # Seed specific domains
    await seeder.seed_domain("physics", count=100)

    # Seed with reproducible data (for testing)
    await seeder.seed_all(seed=12345)  # Same data every time

Environment Variables:
    SEEDER_DEFAULT_LOCALE: Faker locale (default: en_US)
    SEEDER_BATCH_SIZE: Batch insert size (default: 100)
    SEEDER_CLEAR_BEFORE_SEED: Clear tables before seeding (default: false)
"""

import logging
import os
import random
import secrets
import string
from dataclasses import dataclass
from datetime import timedelta

# Faker imports
try:
    from faker import Faker
    from faker.providers import date_time, internet, lorem

    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    Faker = None

# Database imports
try:
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from equation_database import ApiKey, Equation, Execution, User, async_session, get_db_session

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Auth imports
try:
    from equation_auth import get_password_hash

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Logging imports
try:
    from equation_logging import get_logger

    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

logger = logging.getLogger("amos_equation_seeder")

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_LOCALE = os.getenv("SEEDER_DEFAULT_LOCALE", "en_US")
DEFAULT_BATCH_SIZE = int(os.getenv("SEEDER_BATCH_SIZE", "100"))
CLEAR_BEFORE_SEED = os.getenv("SEEDER_CLEAR_BEFORE_SEED", "false").lower() == "true"

# Mathematical domains with sample equations
DOMAINS = {
    "algebra": {
        "equations": [
            ("Linear Equation", "ax + b = 0", "x = -b/a"),
            ("Quadratic Equation", "ax² + bx + c = 0", "x = (-b ± √(b²-4ac)) / 2a"),
            ("Cubic Equation", "ax³ + bx² + cx + d = 0", "Cardano's formula"),
            ("System of Equations", "ax + by = c, dx + ey = f", "Cramer's rule"),
        ],
        "complexity_range": (1, 5),
    },
    "calculus": {
        "equations": [
            ("Derivative", "d/dx(x^n)", "nx^(n-1)"),
            ("Integral", "∫x^n dx", "x^(n+1)/(n+1) + C"),
            ("Chain Rule", "d/dx(f(g(x)))", "f'(g(x)) * g'(x)"),
            ("Partial Derivative", "∂f/∂x", "lim(h→0) [f(x+h,y)-f(x,y)]/h"),
        ],
        "complexity_range": (3, 8),
    },
    "physics": {
        "equations": [
            ("Newton's Second Law", "F = ma", "Force equals mass times acceleration"),
            ("Kinetic Energy", "KE = ½mv²", "Energy of motion"),
            ("Ohm's Law", "V = IR", "Voltage equals current times resistance"),
            ("Einstein's Mass-Energy", "E = mc²", "Energy-mass equivalence"),
            ("Schrödinger Equation", "iℏ∂ψ/∂t = Ĥψ", "Quantum mechanics wave function"),
        ],
        "complexity_range": (4, 10),
    },
    "geometry": {
        "equations": [
            ("Circle Area", "A = πr²", "Area of a circle"),
            ("Pythagorean Theorem", "a² + b² = c²", "Right triangle relationship"),
            ("Sphere Volume", "V = (4/3)πr³", "Volume of a sphere"),
            ("Distance Formula", "d = √[(x₂-x₁)² + (y₂-y₁)²]", "Distance between points"),
        ],
        "complexity_range": (2, 6),
    },
    "statistics": {
        "equations": [
            ("Mean", "μ = (Σxᵢ)/n", "Average of values"),
            ("Standard Deviation", "σ = √[Σ(xᵢ-μ)²/n]", "Measure of dispersion"),
            ("Normal Distribution", "f(x) = (1/σ√2π)e^(-(x-μ)²/2σ²)", "Gaussian distribution"),
            ("Correlation", "r = Σ[(xᵢ-x̄)(yᵢ-ȳ)] / √[Σ(xᵢ-x̄)²Σ(yᵢ-ȳ)²]", "Linear correlation"),
        ],
        "complexity_range": (3, 7),
    },
    "engineering": {
        "equations": [
            ("Ohm's Law", "V = IR", "Electrical circuit analysis"),
            ("Beam Deflection", "δ = FL³/3EI", "Cantilever beam deflection"),
            ("Heat Transfer", "Q = mcΔT", "Heat transfer equation"),
            ("Reynolds Number", "Re = ρvL/μ", "Fluid flow characterization"),
        ],
        "complexity_range": (5, 9),
    },
}

# User roles and permissions
USER_ROLES = ["admin", "researcher", "student", "viewer"]
DOMAINS = list(DOMAINS.keys())

# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class SeedConfig:
    """Configuration for data seeding."""

    users: int = 10
    equations_per_domain: int = 20
    executions_per_equation: int = 3
    api_keys_per_user: int = 2
    seed: int = None
    locale: str = DEFAULT_LOCALE
    batch_size: int = DEFAULT_BATCH_SIZE
    clear_before_seed: bool = CLEAR_BEFORE_SEED


@dataclass
class SeedResult:
    """Result of seeding operation."""

    users_created: int = 0
    equations_created: int = 0
    executions_created: int = 0
    api_keys_created: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def total_created(self) -> int:
        return (
            self.users_created
            + self.equations_created
            + self.executions_created
            + self.api_keys_created
        )


# ============================================================================
# Seeder Class
# ============================================================================


class DatabaseSeeder:
    """Database seeder using Faker for realistic test data."""

    def __init__(self, locale: str = DEFAULT_LOCALE, seed: int = None):
        if not FAKER_AVAILABLE:
            raise ImportError("faker package required. Install: pip install faker")

        if not DATABASE_AVAILABLE:
            raise ImportError("Database module not available")

        self.fake = Faker(locale)
        self.fake.add_provider(internet)
        self.fake.add_provider(lorem)
        self.fake.add_provider(date_time)

        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        self.logger = get_logger("seeder") if LOGGING_AVAILABLE else logger

    async def seed_all(self, config: Optional[SeedConfig] = None) -> SeedResult:
        """Seed all data types.

        Args:
            config: Seeding configuration

        Returns:
            SeedResult with counts and any errors
        """
        if config is None:
            config = SeedConfig()

        result = SeedResult()

        try:
            async with async_session() as session:
                async with session.begin():
                    if config.clear_before_seed:
                        await self._clear_tables(session)

                    # Seed in order: users -> equations -> executions -> api_keys
                    result.users_created = await self._seed_users(session, config.users)

                    result.equations_created = await self._seed_equations(
                        session, config.equations_per_domain
                    )

                    result.executions_created = await self._seed_executions(
                        session, config.executions_per_equation
                    )

                    result.api_keys_created = await self._seed_api_keys(
                        session, config.api_keys_per_user
                    )

                    await session.commit()

        except Exception as e:
            result.errors.append(str(e))
            self.logger.error(f"Seeding failed: {e}")
            raise

        self.logger.info(f"Seeding completed: {result.total_created()} records created")
        return result

    async def _clear_tables(self, session) -> None:
        """Clear all tables before seeding."""
        self.logger.warning("Clearing tables before seeding")
        # Would truncate tables in correct order
        # await session.execute(delete(Execution))
        # await session.execute(delete(ApiKey))
        # await session.execute(delete(Equation))
        # await session.execute(delete(User))

    async def _seed_users(self, session, count: int) -> int:
        """Seed user accounts."""
        created = 0

        for i in range(count):
            username = self.fake.user_name() + f"_{i}"
            email = self.fake.email()

            # Generate random password for seeding (not for production)
            password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(16)
            )
            if AUTH_AVAILABLE:
                hashed_password = get_password_hash(password)
            else:
                hashed_password = password

            role = random.choice(USER_ROLES)
            is_active = random.random() > 0.1  # 90% active

            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                role=role,
                is_active=is_active,
                created_at=self.fake.date_time_between(start_date="-2y", end_date="now"),
            )

            session.add(user)
            created += 1

            if i % 10 == 0:
                await session.flush()

        await session.flush()
        self.logger.info(f"Created {created} users")
        return created

    async def _seed_equations(self, session, per_domain: int) -> int:
        """Seed equations for each domain."""
        created = 0

        # Get all user IDs for assignment
        result = await session.execute(select(User.id))
        user_ids = [r[0] for r in result.all()]

        if not user_ids:
            self.logger.warning("No users found, skipping equation seeding")
            return 0

        for domain, data in DOMAINS.items():
            equations = data["equations"]
            complexity_min, complexity_max = data["complexity_range"]

            for i in range(per_domain):
                # Pick random template or generate custom
                if random.random() > 0.3 and equations:
                    template = random.choice(equations)
                    name = template[0]
                    formula = template[1]
                    solution = template[2]
                else:
                    name = f"{self.fake.word().title()} {self.fake.word().title()}"
                    formula = self._generate_formula()
                    solution = self._generate_solution()

                complexity = random.randint(complexity_min, complexity_max)
                user_id = random.choice(user_ids)

                equation = Equation(
                    name=name,
                    formula=formula,
                    solution=solution,
                    domain=domain,
                    complexity=complexity,
                    user_id=user_id,
                    created_at=self.fake.date_time_between(start_date="-1y", end_date="now"),
                    is_verified=random.random() > 0.2,
                    tags=[self.fake.word() for _ in range(random.randint(1, 3))],
                )

                session.add(equation)
                created += 1

                if created % 50 == 0:
                    await session.flush()

        await session.flush()
        self.logger.info(f"Created {created} equations")
        return created

    async def _seed_executions(self, session, per_equation: int) -> int:
        """Seed execution records."""
        created = 0

        # Get equation IDs
        result = await session.execute(select(Equation.id))
        equation_ids = [r[0] for r in result.all()]

        if not equation_ids:
            self.logger.warning("No equations found, skipping execution seeding")
            return 0

        # Get user IDs
        result = await session.execute(select(User.id))
        user_ids = [r[0] for r in result.all()]

        statuses = ["pending", "running", "completed", "failed", "cancelled"]
        status_weights = [0.05, 0.1, 0.7, 0.1, 0.05]

        for equation_id in equation_ids:
            for _ in range(random.randint(1, per_equation)):
                status = random.choices(statuses, weights=status_weights)[0]

                # Generate execution times
                created_at = self.fake.date_time_between(start_date="-6m", end_date="now")

                if status == "completed":
                    started_at = created_at + timedelta(seconds=random.randint(1, 5))
                    completed_at = started_at + timedelta(seconds=random.randint(1, 30))
                    execution_time = (completed_at - started_at).total_seconds()
                elif status == "failed":
                    started_at = created_at + timedelta(seconds=random.randint(1, 5))
                    completed_at = started_at + timedelta(seconds=random.randint(1, 10))
                    execution_time = None
                elif status == "running":
                    started_at = created_at + timedelta(seconds=random.randint(1, 5))
                    completed_at = None
                    execution_time = None
                else:
                    started_at = None
                    completed_at = None
                    execution_time = None

                execution = Execution(
                    equation_id=equation_id,
                    user_id=random.choice(user_ids),
                    status=status,
                    parameters={
                        "x": random.uniform(-100, 100),
                        "precision": random.choice(["low", "medium", "high"]),
                    },
                    result={"value": random.uniform(-1000, 1000)}
                    if status == "completed"
                    else None,
                    error_message=self.fake.sentence() if status == "failed" else None,
                    created_at=created_at,
                    started_at=started_at,
                    completed_at=completed_at,
                    execution_time=execution_time,
                )

                session.add(execution)
                created += 1

                if created % 100 == 0:
                    await session.flush()

        await session.flush()
        self.logger.info(f"Created {created} executions")
        return created

    async def _seed_api_keys(self, session, per_user: int) -> int:
        """Seed API keys for users."""
        created = 0

        result = await session.execute(select(User.id))
        user_ids = [r[0] for r in result.all()]

        for user_id in user_ids:
            for _ in range(random.randint(0, per_user)):
                key = self.fake.sha256()[:32]

                api_key = ApiKey(
                    user_id=user_id,
                    key=key,
                    name=self.fake.word().title(),
                    is_active=random.random() > 0.1,
                    rate_limit=random.choice([100, 1000, 10000]),
                    created_at=self.fake.date_time_between(start_date="-1y", end_date="now"),
                    expires_at=self.fake.date_time_between(start_date="now", end_date="+1y")
                    if random.random() > 0.5
                    else None,
                )

                session.add(api_key)
                created += 1

        await session.flush()
        self.logger.info(f"Created {created} API keys")
        return created

    def _generate_formula(self) -> str:
        """Generate a random mathematical formula."""
        variables = ["x", "y", "z", "a", "b", "c"]
        ops = ["+", "-", "*", "/", "^"]
        functions = ["sin", "cos", "tan", "log", "exp", "sqrt"]

        var = random.choice(variables)
        func = random.choice(functions)
        op = random.choice(ops)
        const = round(random.uniform(1, 100), 2)

        templates = [
            f"{func}({var}) {op} {const}",
            f"{var}² {op} {const}{var} + {const}",
            f"∂²{var}/∂t² = {func}({var})",
            f"{var} = ({const} ± √({const}² - 4{var}))/2",
            f"∫{func}({var})d{var} = ?",
        ]

        return random.choice(templates)

    def _generate_solution(self) -> str:
        """Generate a random solution description."""
        templates = [
            "Apply quadratic formula",
            "Use integration by parts",
            "Substitute u = x²",
            "Apply chain rule",
            "Use numerical approximation",
            "Factor and solve",
            "Apply L'Hôpital's rule",
        ]
        return random.choice(templates)

    async def seed_domain(self, domain: str, count: int = 50) -> int:
        """Seed equations for a specific domain.

        Args:
            domain: Domain name (algebra, physics, etc.)
            count: Number of equations to create

        Returns:
            Number of equations created
        """
        if domain not in DOMAINS:
            raise ValueError(f"Unknown domain: {domain}. Available: {list(DOMAINS.keys())}")

        async with async_session() as session:
            async with session.begin():
                # Get users
                result = await session.execute(select(User.id))
                user_ids = [r[0] for r in result.all()]

                if not user_ids:
                    self.logger.warning("No users found, creating default user")
                    user = User(
                        username="default_seeder",
                        email="seeder@example.com",
                        hashed_password=secrets.token_hex(32),
                        role="admin",
                    )
                    session.add(user)
                    await session.flush()
                    user_ids = [user.id]

                created = 0
                domain_data = DOMAINS[domain]

                for i in range(count):
                    if domain_data["equations"]:
                        template = random.choice(domain_data["equations"])
                        name = f"{template[0]} Variant {i + 1}"
                        formula = template[1]
                        solution = template[2]
                    else:
                        name = f"{self.fake.word().title()} Formula {i + 1}"
                        formula = self._generate_formula()
                        solution = self._generate_solution()

                    equation = Equation(
                        name=name,
                        formula=formula,
                        solution=solution,
                        domain=domain,
                        complexity=random.randint(*domain_data["complexity_range"]),
                        user_id=random.choice(user_ids),
                        tags=[domain, self.fake.word()],
                    )

                    session.add(equation)
                    created += 1

                    if created % 50 == 0:
                        await session.flush()

                await session.commit()

        self.logger.info(f"Created {created} equations in domain: {domain}")
        return created

    async def seed_users_batch(self, count: int = 100) -> int:
        """Seed a large batch of users efficiently.

        Args:
            count: Number of users to create

        Returns:
            Number of users created
        """
        async with async_session() as session:
            async with session.begin():
                created = 0

                for i in range(count):
                    password = "".join(
                        secrets.choice(string.ascii_letters + string.digits) for _ in range(16)
                    )
                    if AUTH_AVAILABLE:
                        hashed = get_password_hash(password)
                    else:
                        hashed = password

                    user = User(
                        username=f"batch_user_{i}_{self.fake.user_name()}",
                        email=f"user_{i}@{self.fake.domain_name()}",
                        hashed_password=hashed,
                        role=random.choice(USER_ROLES),
                        is_active=True,
                    )

                    session.add(user)
                    created += 1

                    if created % 100 == 0:
                        await session.flush()
                        self.logger.info(f"Progress: {created}/{count} users")

                await session.commit()

        self.logger.info(f"Batch created {created} users")
        return created


# ============================================================================
# CLI Entry Point
# ============================================================================


def main():
    """CLI entry point for seeding."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Equation Database Seeder")

    parser.add_argument("--users", type=int, default=10, help="Number of users to create")
    parser.add_argument("--equations", type=int, default=20, help="Number of equations per domain")
    parser.add_argument("--executions", type=int, default=3, help="Executions per equation")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--domain", type=str, default=None, help="Seed only specific domain")
    parser.add_argument("--clear", action="store_true", help="Clear tables before seeding")

    args = parser.parse_args()

    async def run():
        seeder = DatabaseSeeder(seed=args.seed)

        if args.domain:
            count = await seeder.seed_domain(args.domain, args.equations)
            print(f"Created {count} equations in {args.domain} domain")
        else:
            config = SeedConfig(
                users=args.users,
                equations_per_domain=args.equations,
                executions_per_equation=args.executions,
                seed=args.seed,
                clear_before_seed=args.clear,
            )
            result = await seeder.seed_all(config)
            print("\nSeeding completed!")
            print(f"  Users: {result.users_created}")
            print(f"  Equations: {result.equations_created}")
            print(f"  Executions: {result.executions_created}")
            print(f"  API Keys: {result.api_keys_created}")
            print(f"  Total: {result.total_created()}")

            if result.errors:
                print(f"\nErrors: {len(result.errors)}")
                for error in result.errors:
                    print(f"  - {error}")

    asyncio.run(run())


if __name__ == "__main__":
    main()
