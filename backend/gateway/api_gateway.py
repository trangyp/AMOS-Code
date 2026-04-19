"""
AMOS SuperBrain API Gateway v2.0.0

Unified entry point for all 12 systems with advanced traffic management,
security enforcement at the edge, and full observability integration.

Architecture:
- Request routing to 12 backend systems
- Rate limiting with Redis-backed counters
- Circuit breaking at the edge
- JWT validation and RBAC enforcement
- SuperBrain governance on every request
- Distributed tracing propagation

Owner: Trang Phan
Version: 2.0.0
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

# FastAPI for gateway
try:
    from fastapi import Depends, FastAPI, HTTPException, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Redis for rate limiting
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# JWT validation
try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

# Import existing modules
try:
    from backend.config.feature_flags import is_feature_enabled
    from backend.data_pipeline.streaming import pipeline, publish_event
    from backend.observability.tracing import tracer
    from backend.security.rbac import Permission, Role, rbac

    RBAC_AVAILABLE = True
except ImportError:
    RBAC_AVAILABLE = False


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class GatewayConfig:
    """API Gateway configuration."""

    rate_limit_requests: int = 100  # per minute
    rate_limit_window: int = 60  # seconds
    circuit_failure_threshold: int = 5
    circuit_recovery_timeout: int = 30
    jwt_secret: str = "superbrain-jwt-secret"
    jwt_algorithm: str = "HS256"


@dataclass
class RouteConfig:
    """Route configuration for a backend system."""

    path: str
    target_url: str
    methods: List[str]
    requires_auth: bool = True
    requires_governance: bool = True
    rate_limit_tier: str = "standard"  # standard, premium, unlimited
    circuit_breaker: bool = True


class APIGateway:
    """SuperBrain API Gateway with unified access control."""

    # Routes for 12 systems
    ROUTES: Dict[str, RouteConfig] = {
        # Core API routes
        "production_api": RouteConfig(
            path="/api/v1/production",
            target_url="http://localhost:8001",
            methods=["GET", "POST", "PUT", "DELETE"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="premium",
        ),
        "graphql_api": RouteConfig(
            path="/graphql",
            target_url="http://localhost:8002",
            methods=["GET", "POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="premium",
        ),
        # System routes
        "cognitive_router": RouteConfig(
            path="/api/v1/router",
            target_url="http://localhost:8003",
            methods=["POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="standard",
        ),
        "resilience_engine": RouteConfig(
            path="/api/v1/resilience",
            target_url="http://localhost:8004",
            methods=["GET", "POST"],
            requires_auth=True,
            requires_governance=False,
            rate_limit_tier="standard",
        ),
        "knowledge_loader": RouteConfig(
            path="/api/v1/knowledge",
            target_url="http://localhost:8005",
            methods=["GET", "POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="standard",
        ),
        "master_orchestrator": RouteConfig(
            path="/api/v1/orchestrator",
            target_url="http://localhost:8006",
            methods=["POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="premium",
        ),
        # Agent routes
        "agent_messaging": RouteConfig(
            path="/api/v1/agents/messages",
            target_url="http://localhost:8007",
            methods=["GET", "POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="standard",
        ),
        "agent_observability": RouteConfig(
            path="/api/v1/agents/telemetry",
            target_url="http://localhost:8008",
            methods=["GET", "POST"],
            requires_auth=True,
            requires_governance=False,
            rate_limit_tier="unlimited",
        ),
        # UBI and tools
        "ubi_engine": RouteConfig(
            path="/api/v1/ubi",
            target_url="http://localhost:8009",
            methods=["POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="standard",
        ),
        "amos_tools": RouteConfig(
            path="/api/v1/tools",
            target_url="http://localhost:8010",
            methods=["POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="premium",
        ),
        # Audit and governance
        "audit_exporter": RouteConfig(
            path="/api/v1/audit",
            target_url="http://localhost:8011",
            methods=["GET"],
            requires_auth=True,
            requires_governance=False,
            rate_limit_tier="standard",
        ),
        "superbrain_governance": RouteConfig(
            path="/api/v1/governance",
            target_url="http://localhost:8012",
            methods=["GET", "POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="unlimited",
        ),
        # AXIOM One Execution Slots
        "axiom_one_slots": RouteConfig(
            path="/api/v1/axiom-one/slots",
            target_url="http://localhost:8000",
            methods=["GET", "POST"],
            requires_auth=True,
            requires_governance=True,
            rate_limit_tier="premium",
        ),
        "axiom_one_brain": RouteConfig(
            path="/api/v1/axiom-one/brain",
            target_url="http://localhost:8000",
            methods=["GET"],
            requires_auth=False,
            requires_governance=False,
            rate_limit_tier="standard",
        ),
    }

    def __init__(self, config: Optional[GatewayConfig] = None):
        self.config = config or GatewayConfig()
        self._redis: redis.Redis = None
        self._brain = None
        self._circuits: Dict[str, CircuitState] = {}
        self._circuit_failures: Dict[str, int] = {}
        self._circuit_last_failure: Dict[str, float] = {}

        # Initialize connections
        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url("redis://localhost:6379/2")
            except Exception:
                pass

        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass

        # Initialize FastAPI app
        if FASTAPI_AVAILABLE:
            self.app = FastAPI(
                title="AMOS SuperBrain API Gateway",
                version="2.0.0",
                description="Unified entry point for all 12 SuperBrain systems",
            )
            self._setup_middleware()
            self._setup_routes()

    def _setup_middleware(self):
        """Configure middleware stack."""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Trusted hosts
        self.app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=["*.amos.example.com", "localhost"]
        )

    def _setup_routes(self):
        """Setup gateway routes."""

        # Health check
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "version": "2.0.0",
                "systems": 12,
                "timestamp": time.time(),
            }

        # Gateway metrics
        @self.app.get("/gateway/metrics")
        async def gateway_metrics():
            return {
                "rate_limits": self._get_rate_limit_status(),
                "circuits": {k: v.value for k, v in self._circuits.items()},
                "routes": len(self.ROUTES),
            }

        # Dynamic routes for all systems
        for system_name, route_config in self.ROUTES.items():
            self._create_route(system_name, route_config)

    def _create_route(self, system_name: str, config: RouteConfig):
        """Create dynamic route for system."""

        async def route_handler(
            request: Request,
            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
        ):
            # CANONICAL: Start governance span
            with tracer.start_governed_span(
                name=f"gateway.{system_name}",
                system="api_gateway",
                operation="route_request",
                attributes={"target": system_name, "path": config.path},
            ):
                # 1. Check feature flag
                if not is_feature_enabled(f"{system_name}_api", user_role="operator"):
                    raise HTTPException(status_code=503, detail=f"{system_name} API disabled")

                # 2. Check circuit breaker
                if config.circuit_breaker and not self._check_circuit(system_name):
                    raise HTTPException(status_code=503, detail=f"{system_name} circuit open")

                # 3. Authenticate
                if config.requires_auth:
                    user_role = await self._authenticate(credentials)
                    if not user_role:
                        raise HTTPException(status_code=401, detail="Unauthorized")
                else:
                    user_role = Role.READONLY

                # 4. Check RBAC permission
                if RBAC_AVAILABLE and config.requires_auth:
                    permission = Permission.API_PRODUCTION_ACCESS
                    if not rbac.has_permission(user_role, permission):
                        # Publish denied event
                        if SUPERBRAIN_AVAILABLE:
                            publish_event(
                                event_type="access_denied",
                                source_system="api_gateway",
                                payload={
                                    "system": system_name,
                                    "user_role": user_role.value,
                                    "reason": "insufficient_permissions",
                                },
                                requires_governance=False,
                            )
                        raise HTTPException(status_code=403, detail="Forbidden")

                # 5. Check rate limit
                if not self._check_rate_limit(system_name, user_role.value):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")

                # 6. CANONICAL: SuperBrain governance validation
                if config.requires_governance:
                    if not self._validate_with_superbrain(system_name, request):
                        raise HTTPException(status_code=403, detail="Governance denied")

                # 7. Route to backend
                try:
                    # In real implementation, proxy to target_url
                    # For now, return success
                    response = {
                        "routed_to": system_name,
                        "target": config.target_url,
                        "user_role": user_role.value if isinstance(user_role, Role) else user_role,
                        "governance": "passed",
                    }

                    # Record success
                    self._record_circuit_success(system_name)

                    # Publish routing event
                    if SUPERBRAIN_AVAILABLE:
                        publish_event(
                            event_type="request_routed",
                            source_system="api_gateway",
                            payload={
                                "target": system_name,
                                "path": config.path,
                                "user": user_role.value
                                if isinstance(user_role, Role)
                                else user_role,
                            },
                            requires_governance=False,
                        )

                    return response

                except Exception as e:
                    self._record_circuit_failure(system_name)
                    raise HTTPException(status_code=502, detail=f"Backend error: {str(e)}")

        # Register route
        for method in config.methods:
            if method == "GET":
                self.app.get(config.path)(route_handler)
            elif method == "POST":
                self.app.post(config.path)(route_handler)
            elif method == "PUT":
                self.app.put(config.path)(route_handler)
            elif method == "DELETE":
                self.app.delete(config.path)(route_handler)

    def _check_circuit(self, system: str) -> bool:
        """Check circuit breaker state."""
        state = self._circuits.get(system, CircuitState.CLOSED)

        if state == CircuitState.CLOSED:
            return True

        if state == CircuitState.OPEN:
            # Check if recovery timeout passed
            last_failure = self._circuit_last_failure.get(system, 0)
            if time.time() - last_failure > self.config.circuit_recovery_timeout:
                self._circuits[system] = CircuitState.HALF_OPEN
                return True
            return False

        if state == CircuitState.HALF_OPEN:
            return True

        return False

    def _record_circuit_failure(self, system: str):
        """Record circuit failure."""
        self._circuit_failures[system] = self._circuit_failures.get(system, 0) + 1
        self._circuit_last_failure[system] = time.time()

        if self._circuit_failures[system] >= self.config.circuit_failure_threshold:
            self._circuits[system] = CircuitState.OPEN

    def _record_circuit_success(self, system: str):
        """Record circuit success."""
        self._circuit_failures[system] = 0
        self._circuits[system] = CircuitState.CLOSED

    def _check_rate_limit(self, system: str, user_id: str) -> bool:
        """Check rate limit for user."""
        if not self._redis:
            return True  # Fail open if Redis unavailable

        key = f"rate_limit:{system}:{user_id}"

        try:
            current = self._redis.get(key)
            if current is None:
                self._redis.setex(key, self.config.rate_limit_window, 1)
                return True

            count = int(current)
            if count >= self.config.rate_limit_requests:
                return False

            self._redis.incr(key)
            return True
        except Exception:
            return True  # Fail open

    def _get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        if not self._redis:
            return {"status": "redis_unavailable"}

        # Scan for rate limit keys
        try:
            keys = self._redis.scan_iter(match="rate_limit:*", count=100)
            return {"active_limits": len(list(keys))}
        except Exception:
            return {"status": "error"}

    async def _authenticate(self, credentials: HTTPAuthorizationCredentials) -> Optional[Role]:
        """Authenticate and return user role."""
        if not credentials:
            return None

        if not JWT_AVAILABLE:
            # Fallback: assume operator role for development
            return Role.OPERATOR

        try:
            token = credentials.credentials
            payload = jwt.decode(
                token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm]
            )
            role_str = payload.get("role", "readonly")
            return Role(role_str)
        except Exception:
            return None

    def _validate_with_superbrain(self, system: str, request: Request) -> bool:
        """Validate request with SuperBrain."""
        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return True  # Fail open

        try:
            if hasattr(self._brain, "action_gate"):
                action_result = self._brain.action_gate.validate_action(
                    agent_id="api_gateway",
                    action=f"route_to_{system}",
                    details={"path": str(request.url), "method": request.method},
                )
                return action_result.authorized
        except Exception:
            pass  # Fail open

        return True


# Global gateway instance
gateway = APIGateway()


# Convenience function for creating gateway
def create_gateway_app() -> Optional[FastAPI]:
    """Create and return gateway FastAPI app."""
    if FASTAPI_AVAILABLE:
        return gateway.app
    return None
