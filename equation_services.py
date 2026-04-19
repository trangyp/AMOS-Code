#!/usr/bin/env python3
"""AMOS Equation Services - Business Logic Layer.

Production-grade service layer implementing Clean Architecture patterns:
- Service layer between API and Repository layers
- Unit of Work pattern for transaction management
- Domain events for loose coupling
- Business rule validation
- Complex operation orchestration
- Integration with cache, queue, and external services

Architecture Pattern: Service Layer + Unit of Work + Domain Events
Clean Architecture: Business logic independent of framework/infrastructure

Service Categories:
    - EquationService: Equation CRUD, search, validation
    - ExecutionService: Execute equations, manage results, track history
    - UserService: User management, authentication workflows
    - AnalyticsService: Statistics, reporting, insights
    - DomainService: Domain/category management

Usage:
    # In FastAPI endpoint
    from equation_services import EquationService, ExecutionService

    @app.post("/equations/{id}/execute")
    async def execute(
        id: int,
        service: ExecutionService = Depends(get_execution_service)
    ):
        result = await service.execute_equation(id, inputs={"x": 5})
        return result

Integration:
    - equation_database: Repository pattern for data access
    - equation_cache: Redis caching for performance
    - equation_tasks: Celery for async execution
    - equation_notifications: WebSocket for real-time updates
"""

import hashlib
import logging
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

# Core dependencies
try:
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    AsyncSession = None

try:
    from equation_database import (
        ApiKey,
        ApiKeyRepository,
        DatabaseManager,
        Domain,
        Equation,
        EquationExecution,
        EquationRepository,
        ExecutionRepository,
        ExecutionStatus,
        User,
        UserRepository,
    )

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    Equation = None
    EquationExecution = None
    User = None
    ApiKey = None
    Domain = None

try:
    from equation_cache import EquationCache, get_cache

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    EquationCache = None

try:
    from equation_tasks import TaskManager

    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False
    TaskManager = None

try:
    from equation_notifications import NotificationManager

    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    NotificationManager = None

try:
    from equation_config import Settings, get_settings

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    Settings = None

# Logger
logger = logging.getLogger("amos_equation_services")

# Type variable for generic service
T = TypeVar("T")


# ============================================================================
# Domain Events (for loose coupling)
# ============================================================================


@dataclass
class DomainEvent:
    """Base domain event."""

    event_id: str = field(default_factory=lambda: hashlib.uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
        }


@dataclass
class EquationExecutedEvent(DomainEvent):
    """Event fired when equation is executed."""

    equation_id: int = 0
    execution_id: int = 0
    user_id: int = None
    success: bool = False
    execution_time_ms: float = 0.0

    def __post_init__(self):
        self.event_type = "equation.executed"


@dataclass
class EquationCreatedEvent(DomainEvent):
    """Event fired when equation is created."""

    equation_id: int = 0
    name: str = ""
    domain: str = ""

    def __post_init__(self):
        self.event_type = "equation.created"


@dataclass
class UserRegisteredEvent(DomainEvent):
    """Event fired when user registers."""

    user_id: int = 0
    username: str = ""
    email: str = ""

    def __post_init__(self):
        self.event_type = "user.registered"


# Event bus for publishing events
class EventBus:
    """Simple event bus for domain events."""

    def __init__(self):
        self._handlers: Dict[str, list] = {}

    def subscribe(self, event_type: str, handler):
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        """Publish an event to all subscribers."""
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")


# Global event bus
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus."""
    return _event_bus


# ============================================================================
# Unit of Work Pattern
# ============================================================================


class UnitOfWork:
    """Unit of Work pattern for transaction management.

    Manages database transactions and coordinates multiple repositories.
    Ensures atomic operations across multiple entities.

    Usage:
        async with UnitOfWork(session) as uow:
            equation = await uow.equations.create(...)
            execution = await uow.executions.create(...)
            await uow.commit()  # Both succeed or both fail
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.equations = EquationRepository(session)
        self.executions = ExecutionRepository(session)
        self.users = UserRepository(session)
        self.api_keys = ApiKeyRepository(session)
        self._committed = False

    async def commit(self):
        """Commit the transaction."""
        await self.session.commit()
        self._committed = True

    async def rollback(self):
        """Rollback the transaction."""
        await self.session.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        elif not self._committed:
            await self.commit()


# ============================================================================
# Service Base Class
# ============================================================================


class BaseService(ABC, Generic[T]):
    """Base service class with common functionality."""

    def __init__(
        self,
        uow: Optional[UnitOfWork] = None,
        cache: Optional[EquationCache] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.uow = uow
        self.cache = cache
        self.event_bus = event_bus or _event_bus

    async def _cache_get(self, key: str) -> Optional[Any]:
        """Get from cache if available."""
        if self.cache:
            return await self.cache.get(key)
        return None

    async def _cache_set(self, key: str, value: Any, ttl: int = 300):
        """Set in cache if available."""
        if self.cache:
            await self.cache.set(key, value, ttl)

    async def _cache_delete(self, key: str):
        """Delete from cache if available."""
        if self.cache:
            await self.cache.delete(key)

    async def _publish_event(self, event: DomainEvent):
        """Publish a domain event."""
        await self.event_bus.publish(event)

    def _generate_cache_key(self, prefix: str, *parts) -> str:
        """Generate a cache key."""
        key_parts = [prefix] + [str(p) for p in parts]
        return ":".join(key_parts)


# ============================================================================
# Equation Service
# ============================================================================


class EquationService(BaseService[Equation]):
    """Service for equation business logic.

    Handles:
    - Equation CRUD operations
    - Search and filtering
    - Validation
    - Domain management
    - Caching
    """

    async def create_equation(
        self,
        name: str,
        domain: str,
        formula: str = None,
        description: str = None,
        parameters: dict = None,
        constraints: dict = None,
        **kwargs,
    ) -> Equation:
        """Create a new equation with validation."""
        # Business validation
        if not name or len(name) < 2:
            raise ValueError("Equation name must be at least 2 characters")

        if not domain:
            raise ValueError("Domain is required")

        # Check for duplicates
        existing = await self.uow.equations.get_by_name(name)
        if existing:
            raise ValueError(f"Equation '{name}' already exists")

        # Create equation
        equation = await self.uow.equations.create(
            name=name,
            domain=domain,
            formula=formula,
            description=description,
            parameters=parameters or {},
            constraints=constraints or {},
            **kwargs,
        )

        # Publish event
        await self._publish_event(
            EquationCreatedEvent(
                equation_id=equation.id, name=equation.name, domain=equation.domain
            )
        )

        # Cache invalidation
        await self._cache_delete(f"equations:domain:{domain}")

        logger.info(f"Created equation: {name} (ID: {equation.id})")
        return equation

    async def get_equation(self, equation_id: int) -> Optional[Equation]:
        """Get equation by ID with caching."""
        cache_key = self._generate_cache_key("equation", equation_id)

        # Try cache first
        cached = await self._cache_get(cache_key)
        if cached:
            return Equation(**cached)

        # Get from database
        equation = await self.uow.equations.get_by_id(Equation, equation_id)

        if equation:
            # Cache result
            await self._cache_set(cache_key, equation.to_dict(), ttl=600)

        return equation

    async def get_equation_by_name(self, name: str) -> Optional[Equation]:
        """Get equation by name."""
        return await self.uow.equations.get_by_name(name)

    async def search_equations(
        self, query: str, domain: str = None, skip: int = 0, limit: int = 100
    ) -> List[Equation]:
        """Search equations with caching."""
        cache_key = self._generate_cache_key("search", query, domain, skip, limit)

        # Try cache
        cached = await self._cache_get(cache_key)
        if cached:
            return [Equation(**e) for e in cached]

        # Search in database
        results = await self.uow.equations.search(query, domain, skip, limit)

        # Cache results
        if results:
            await self._cache_set(cache_key, [e.to_dict() for e in results], ttl=300)

        return results

    async def list_by_domain(self, domain: str, skip: int = 0, limit: int = 100) -> List[Equation]:
        """List equations by domain with caching."""
        cache_key = self._generate_cache_key("equations", "domain", domain, skip, limit)

        cached = await self._cache_get(cache_key)
        if cached:
            return [Equation(**e) for e in cached]

        results = await self.uow.equations.get_by_domain(domain, skip, limit)

        if results:
            await self._cache_set(cache_key, [e.to_dict() for e in results], ttl=600)

        return results

    async def update_equation(self, equation_id: int, **updates) -> Equation:
        """Update equation with validation."""
        equation = await self.uow.equations.get_by_id(Equation, equation_id)
        if not equation:
            raise ValueError(f"Equation {equation_id} not found")

        # Update
        updated = await self.uow.equations.update(equation, **updates)

        # Invalidate cache
        await self._cache_delete(self._generate_cache_key("equation", equation_id))
        await self._cache_delete(f"equations:domain:{equation.domain}")

        return updated

    async def delete_equation(self, equation_id: int) -> None:
        """Soft delete equation."""
        equation = await self.uow.equations.get_by_id(Equation, equation_id)
        if not equation:
            raise ValueError(f"Equation {equation_id} not found")

        await self.uow.equations.soft_delete_equation(equation)
        await self.uow.commit()

        # Invalidate cache
        await self._cache_delete(self._generate_cache_key("equation", equation_id))
        await self._cache_delete(f"equations:domain:{equation.domain}")

        logger.info(f"Deleted equation: {equation_id}")


# ============================================================================
# Execution Service
# ============================================================================


class ExecutionService(BaseService[EquationExecution]):
    """Service for equation execution business logic.

    Handles:
    - Synchronous and asynchronous execution
    - Input validation
    - Result caching
    - Execution tracking and history
    - Error handling and retries
    - Notifications
    """

    def __init__(
        self,
        uow: Optional[UnitOfWork] = None,
        cache: Optional[EquationCache] = None,
        event_bus: Optional[EventBus] = None,
        task_manager: Optional[TaskManager] = None,
    ):
        super().__init__(uow, cache, event_bus)
        self.task_manager = task_manager

    async def execute_equation(
        self,
        equation_id: int,
        inputs: Dict[str, Any],
        user_id: int = None,
        request_id: str = None,
        async_execution: bool = False,
        **metadata,
    ) -> Dict[str, Any]:
        """Execute an equation.

        Args:
            equation_id: ID of equation to execute
            inputs: Input parameters
            user_id: Optional user ID for tracking
            request_id: Optional request ID for idempotency
            async_execution: Whether to execute asynchronously via Celery
            **metadata: Additional metadata (ip_address, user_agent, etc.)

        Returns:
            Execution result or task ID if async
        """
        # Get equation
        equation = await self.uow.equations.get_by_id(Equation, equation_id)
        if not equation:
            raise ValueError(f"Equation {equation_id} not found")

        if not equation.is_active:
            raise ValueError("Equation is not active")

        # Validate inputs
        self._validate_inputs(equation, inputs)

        # Check cache for identical execution (if idempotent)
        if request_id:
            cache_key = self._generate_cache_key("exec", equation_id, request_id)
            cached = await self._cache_get(cache_key)
            if cached:
                return cached

        # Create execution record
        execution = await self.uow.executions.create(
            equation_id=equation_id,
            inputs=inputs,
            status=ExecutionStatus.PENDING,
            user_id=user_id,
            request_id=request_id,
            **metadata,
        )

        if async_execution and self.task_manager:
            # Queue for async execution
            task = await self.task_manager.submit_equation_task(
                equation_id=equation_id, inputs=inputs, execution_id=execution.id
            )

            return {
                "execution_id": execution.id,
                "task_id": task.id,
                "status": "queued",
                "message": "Execution queued for async processing",
            }

        # Execute synchronously
        start_time = datetime.now(UTC)

        try:
            # Update status
            await self.uow.executions.update_status(execution, ExecutionStatus.RUNNING)

            # Perform calculation (this would call the actual equation engine)
            result = await self._perform_calculation(equation, inputs)

            # Calculate execution time
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Update execution record
            await self.uow.executions.update_status(
                execution,
                ExecutionStatus.COMPLETED,
                result=result,
                execution_time_ms=execution_time,
            )

            await self.uow.commit()

            # Publish event
            await self._publish_event(
                EquationExecutedEvent(
                    equation_id=equation_id,
                    execution_id=execution.id,
                    user_id=user_id,
                    success=True,
                    execution_time_ms=execution_time,
                )
            )

            response = {
                "execution_id": execution.id,
                "status": "completed",
                "result": result,
                "execution_time_ms": execution_time,
            }

            # Cache result if request_id provided
            if request_id:
                await self._cache_set(cache_key, response, ttl=300)

            return response

        except Exception as e:
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            await self.uow.executions.update_status(
                execution,
                ExecutionStatus.FAILED,
                error_message=str(e),
                error_details={"exception_type": type(e).__name__},
                execution_time_ms=execution_time,
            )
            await self.uow.commit()

            # Publish failure event
            await self._publish_event(
                EquationExecutedEvent(
                    equation_id=equation_id,
                    execution_id=execution.id,
                    user_id=user_id,
                    success=False,
                    execution_time_ms=execution_time,
                )
            )

            raise ExecutionError(f"Execution failed: {e}") from e

    def _validate_inputs(self, equation: Equation, inputs: dict) -> None:
        """Validate execution inputs against equation constraints."""
        constraints = equation.constraints or {}
        parameters = equation.parameters or {}

        # Check required parameters
        required = parameters.get("required", [])
        for param in required:
            if param not in inputs:
                raise ValueError(f"Missing required parameter: {param}")

        # Validate types and ranges
        for key, value in inputs.items():
            param_def = parameters.get(key, {})

            # Type validation
            expected_type = param_def.get("type")
            if expected_type == "number" and not isinstance(value, (int, float)):
                raise ValueError(f"Parameter {key} must be a number")

            # Range validation
            min_val = param_def.get("min")
            max_val = param_def.get("max")
            if min_val is not None and value < min_val:
                raise ValueError(f"Parameter {key} must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise ValueError(f"Parameter {key} must be <= {max_val}")

    async def _perform_calculation(
        self, equation: Equation, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform the actual calculation.

        This is a placeholder that would integrate with the actual
        equation computation engine.
        """
        # TODO: Integrate with equation computation engine
        # For now, return a mock result
        return {
            "equation_name": equation.name,
            "inputs": inputs,
            "output": 0.0,  # Placeholder
            "computed_at": datetime.now(UTC).isoformat(),
        }

    async def get_execution_status(self, execution_id: int) -> Dict[str, Any]:
        """Get execution status."""
        execution = await self.uow.executions.get_by_id(EquationExecution, execution_id)

        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        return {
            "execution_id": execution.id,
            "equation_id": execution.equation_id,
            "status": execution.status.value
            if isinstance(execution.status, ExecutionStatus)
            else execution.status,
            "result": execution.result,
            "error_message": execution.error_message,
            "execution_time_ms": execution.execution_time_ms,
            "created_at": execution.created_at.isoformat() if execution.created_at else None,
            "updated_at": execution.updated_at.isoformat() if execution.updated_at else None,
        }

    async def get_execution_history(
        self, equation_id: int = None, user_id: int = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get execution history."""
        if equation_id:
            executions = await self.uow.executions.get_recent_by_equation(equation_id, limit)
        else:
            # Get all recent executions
            executions = await self.uow.executions.get_all(EquationExecution, limit=limit)

        return [
            {
                "execution_id": e.id,
                "equation_id": e.equation_id,
                "status": e.status.value if isinstance(e.status, ExecutionStatus) else e.status,
                "execution_time_ms": e.execution_time_ms,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in executions
        ]


# ============================================================================
# User Service
# ============================================================================


class UserService(BaseService[User]):
    """Service for user management business logic."""

    async def register_user(
        self, username: str, email: str, password: str, full_name: str = None
    ) -> User:
        """Register a new user."""
        # Validate
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")

        if not email or "@" not in email:
            raise ValueError("Valid email required")

        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Check duplicates
        existing_user = await self.uow.users.get_by_username(username)
        if existing_user:
            raise ValueError("Username already taken")

        existing_email = await self.uow.users.get_by_email(email)
        if existing_email:
            raise ValueError("Email already registered")

        # Hash password (in production, use proper hashing)
        import hashlib

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Create user
        user = await self.uow.users.create(
            username=username, email=email, password_hash=password_hash, full_name=full_name
        )

        # Publish event
        await self._publish_event(
            UserRegisteredEvent(user_id=user.id, username=username, email=email)
        )

        logger.info(f"Registered user: {username} (ID: {user.id})")
        return user

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        user = await self.uow.users.get_by_username(username)
        if not user:
            return None

        # Verify password
        import hashlib

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user.password_hash:
            return None

        if not user.is_active:
            return None

        # Update last login
        await self.uow.users.update_last_login(user)
        await self.uow.commit()

        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.uow.users.get_by_id(User, user_id)


# ============================================================================
# Analytics Service
# ============================================================================


class AnalyticsService(BaseService):
    """Service for analytics and reporting."""

    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        # Equation counts
        total_equations = await self.uow.equations.count(Equation)
        active_equations = await self.uow.equations.count(Equation, is_active=True)

        # Execution statistics
        execution_stats = await self.uow.executions.get_statistics()

        # Domain distribution
        # This would need a custom query

        return {
            "equations": {
                "total": total_equations,
                "active": active_equations,
                "inactive": total_equations - active_equations,
            },
            "executions": execution_stats,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def get_equation_statistics(self, equation_id: int) -> Dict[str, Any]:
        """Get statistics for a specific equation."""
        stats = await self.uow.executions.get_statistics(equation_id=equation_id)

        return {"equation_id": equation_id, "executions": stats}


# ============================================================================
# Custom Exceptions
# ============================================================================


class ExecutionError(Exception):
    """Error during equation execution."""

    pass


class ValidationError(Exception):
    """Business validation error."""

    pass


# ============================================================================
# Dependency Injection Helpers
# ============================================================================


async def get_unit_of_work() -> UnitOfWork:
    """Factory for UnitOfWork (use with FastAPI Depends)."""
    if not DATABASE_AVAILABLE:
        raise ImportError("Database layer not available")

    # Get session from database manager
    from equation_database import _db_manager

    if not _db_manager.session_maker:
        await _db_manager.initialize()

    async with _db_manager.session_maker() as session:
        yield UnitOfWork(session)


async def get_equation_service(uow: UnitOfWork = None) -> EquationService:
    """Factory for EquationService."""
    if uow is None:
        async for uow in get_unit_of_work():
            pass

    cache = get_cache() if CACHE_AVAILABLE else None
    return EquationService(uow=uow, cache=cache)


async def get_execution_service(uow: UnitOfWork = None) -> ExecutionService:
    """Factory for ExecutionService."""
    if uow is None:
        async for uow in get_unit_of_work():
            pass

    cache = get_cache() if CACHE_AVAILABLE else None
    task_manager = TaskManager() if TASKS_AVAILABLE else None

    return ExecutionService(uow=uow, cache=cache, task_manager=task_manager)


async def get_user_service(uow: UnitOfWork = None) -> UserService:
    """Factory for UserService."""
    if uow is None:
        async for uow in get_unit_of_work():
            pass

    return UserService(uow=uow)


async def get_analytics_service(uow: UnitOfWork = None) -> AnalyticsService:
    """Factory for AnalyticsService."""
    if uow is None:
        async for uow in get_unit_of_work():
            pass

    return AnalyticsService(uow=uow)


# ============================================================================
# Example Usage
# ============================================================================


async def example_usage():
    """Example usage of services."""
    from equation_database import close_database, initialize_database

    # Initialize
    await initialize_database()

    # Create services
    async for uow in get_unit_of_work():
        equation_service = EquationService(uow)
        execution_service = ExecutionService(uow)

        # Create equation
        try:
            equation = await equation_service.create_equation(
                name="test_equation", domain="test", formula="x + y", description="Test equation"
            )
            print(f"Created: {equation}")

            # Execute
            result = await execution_service.execute_equation(equation.id, inputs={"x": 1, "y": 2})
            print(f"Result: {result}")

        except ValueError as e:
            print(f"Validation error: {e}")

    # Cleanup
    await close_database()


if __name__ == "__main__":
    import asyncio
    from typing import Generic, TypeVar

    asyncio.run(example_usage())
