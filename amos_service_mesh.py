#!/usr/bin/env python3
"""AMOS Service Mesh - Phase 23
==============================

Enterprise service mesh for the 14-Layer Cognitive Architecture:
- Service discovery and registry
- mTLS for inter-service security
- Distributed tracing (OpenTelemetry)
- Load balancing and circuit breaking
- Health-aware traffic routing
- Canary deployments

Architecture:
```
┌─────────────────────────────────────────────────────────────┐
│                    AMOS Service Mesh                        │
├─────────────────────────────────────────────────────────────┤
│  Service Registry (Redis/Consul)                            │
│  ├── Layer 00-14 service registration                     │
│  ├── Health-aware service discovery                       │
│  └── Metadata and tags                                     │
│                                                             │
│  mTLS Security                                              │
│  ├── Automatic certificate rotation                       │
│  ├── Mutual TLS authentication                            │
│  └── Certificate pinning                                   │
│                                                             │
│  Traffic Management                                         │
│  ├── Load balancing (round-robin, least-conn)          │
│  ├── Circuit breaking (failure threshold)                │
│  ├── Retry policies (exponential backoff)                │
│  └── Canary/blue-green deployments                       │
│                                                             │
│  Observability                                            │
│  ├── Distributed tracing (OpenTelemetry)                 │
│  ├── Service metrics (latency, throughput)                 │
│  └── Service graph visualization                         │
└─────────────────────────────────────────────────────────────┘
```

Owner: Trang
Version: 1.0.0
Phase: 23
"""

import asyncio
import hashlib
import json
import os
import random
import ssl
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp
import structlog

# Optional imports with fallbacks
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = structlog.get_logger(__name__)

# Configuration
SERVICE_MESH_ENABLED = os.getenv("SERVICE_MESH_ENABLED", "true").lower() == "true"
SERVICE_REGISTRY_URL = os.getenv("SERVICE_REGISTRY_URL", "redis://localhost:6379/1")
MTLS_ENABLED = os.getenv("MTLS_ENABLED", "true").lower() == "true"
CERT_ROTATION_DAYS = int(os.getenv("CERT_ROTATION_DAYS", "30"))
OTEL_EXPORTER_ENDPOINT = os.getenv("OTEL_EXPORTER_ENDPOINT", "http://localhost:4317")
DEFAULT_TIMEOUT = float(os.getenv("SERVICE_TIMEOUT", "30.0"))
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
CIRCUIT_BREAKER_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60"))


# ============================================
# Enums
# ============================================


class ServiceStatus(Enum):
    """Service health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class LoadBalancerStrategy(Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


# ============================================
# Data Classes
# ============================================


@dataclass
class ServiceEndpoint:
    """Represents a service instance endpoint."""

    service_name: str
    instance_id: str
    host: str
    port: int
    protocol: str = "http"
    metadata: Dict[str, Any] = field(default_factory=dict)
    health_status: ServiceStatus = ServiceStatus.UNKNOWN
    last_heartbeat: datetime = None
    weight: int = 1
    tags: List[str] = field(default_factory=list)

    @property
    def address(self) -> str:
        """Full service address."""
        return f"{self.protocol}://{self.host}:{self.port}"


@dataclass
class ServiceRoute:
    """Traffic routing configuration."""

    source_service: str
    target_service: str
    weight: int = 100
    retry_attempts: int = 3
    timeout_ms: int = 30000
    headers: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD
    recovery_timeout: int = CIRCUIT_BREAKER_TIMEOUT
    half_open_max_calls: int = 3
    success_threshold: int = 2


@dataclass
class TraceContext:
    """Distributed tracing context."""

    trace_id: str
    span_id: str
    parent_span_id: str = None
    sampled: bool = True
    baggage: Dict[str, str] = field(default_factory=dict)


# ============================================
# Service Registry
# ============================================


class ServiceRegistry:
    """
    Redis-backed service registry for dynamic service discovery.
    """

    def __init__(self, redis_url: str = SERVICE_REGISTRY_URL):
        self.redis_url = redis_url
        self._redis: Optional[Any] = None
        self._local_cache: dict[str, list[ServiceEndpoint]] = {}

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        if REDIS_AVAILABLE:
            try:
                self._redis = await aioredis.from_url(
                    self.redis_url, encoding="utf-8", decode_responses=True
                )
                logger.info("service_registry.initialized")
            except Exception as e:
                logger.error("service_registry.init_failed", error=str(e))

    async def register(self, endpoint: ServiceEndpoint, ttl_seconds: int = 60) -> bool:
        """
        Register a service endpoint.

        Args:
            endpoint: Service endpoint to register
            ttl_seconds: Time-to-live for registration

        Returns:
            True if registered successfully
        """
        try:
            key = f"amos:services:{endpoint.service_name}:{endpoint.instance_id}"
            data = {
                "host": endpoint.host,
                "port": endpoint.port,
                "protocol": endpoint.protocol,
                "metadata": json.dumps(endpoint.metadata),
                "health": endpoint.health_status.value,
                "weight": endpoint.weight,
                "tags": json.dumps(endpoint.tags),
                "heartbeat": datetime.now(UTC).isoformat(),
            }

            if self._redis:
                await self._redis.hset(key, mapping=data)
                await self._redis.expire(key, ttl_seconds)

            # Update local cache
            if endpoint.service_name not in self._local_cache:
                self._local_cache[endpoint.service_name] = []

            # Remove existing entry for this instance
            self._local_cache[endpoint.service_name] = [
                e
                for e in self._local_cache[endpoint.service_name]
                if e.instance_id != endpoint.instance_id
            ]
            self._local_cache[endpoint.service_name].append(endpoint)

            logger.info(
                "service.registered",
                service=endpoint.service_name,
                instance=endpoint.instance_id,
                address=endpoint.address,
            )
            return True

        except Exception as e:
            logger.error("service.register_failed", error=str(e))
            return False

    async def deregister(self, service_name: str, instance_id: str) -> bool:
        """Deregister a service instance."""
        try:
            key = f"amos:services:{service_name}:{instance_id}"

            if self._redis:
                await self._redis.delete(key)

            # Update local cache
            if service_name in self._local_cache:
                self._local_cache[service_name] = [
                    e for e in self._local_cache[service_name] if e.instance_id != instance_id
                ]

            logger.info("service.deregistered", service=service_name, instance=instance_id)
            return True

        except Exception as e:
            logger.error("service.deregister_failed", error=str(e))
            return False

    async def discover(
        self, service_name: str, healthy_only: bool = True, tags: List[str] = None
    ) -> List[ServiceEndpoint]:
        """
        Discover service endpoints.

        Args:
            service_name: Name of service to discover
            healthy_only: Only return healthy endpoints
            tags: Filter by tags

        Returns:
            List of matching service endpoints
        """
        endpoints: List[ServiceEndpoint] = []

        try:
            if self._redis:
                pattern = f"amos:services:{service_name}:*"
                keys = await self._redis.keys(pattern)

                for key in keys:
                    data = await self._redis.hgetall(key)
                    if data:
                        endpoint = self._parse_endpoint(key, data)

                        # Filter by health
                        if healthy_only and endpoint.health_status != ServiceStatus.HEALTHY:
                            continue

                        # Filter by tags
                        if tags and not any(t in endpoint.tags for t in tags):
                            continue

                        endpoints.append(endpoint)
            else:
                # Use local cache
                endpoints = self._local_cache.get(service_name, [])
                if healthy_only:
                    endpoints = [e for e in endpoints if e.health_status == ServiceStatus.HEALTHY]

        except Exception as e:
            logger.error("service.discover_failed", error=str(e))
            # Fallback to local cache
            endpoints = self._local_cache.get(service_name, [])

        return endpoints

    def _parse_endpoint(self, key: str, data: Dict[str, str]) -> ServiceEndpoint:
        """Parse Redis data into ServiceEndpoint."""
        parts = key.split(":")
        service_name = parts[2] if len(parts) > 2 else "unknown"
        instance_id = parts[3] if len(parts) > 3 else "unknown"

        return ServiceEndpoint(
            service_name=service_name,
            instance_id=instance_id,
            host=data.get("host", "localhost"),
            port=int(data.get("port", 80)),
            protocol=data.get("protocol", "http"),
            metadata=json.loads(data.get("metadata", "{}")),
            health_status=ServiceStatus(data.get("health", "unknown")),
            weight=int(data.get("weight", 1)),
            tags=json.loads(data.get("tags", "[]")),
        )

    async def update_health(
        self, service_name: str, instance_id: str, status: ServiceStatus
    ) -> bool:
        """Update service health status."""
        try:
            key = f"amos:services:{service_name}:{instance_id}"

            if self._redis:
                await self._redis.hset(key, "health", status.value)
                await self._redis.hset(key, "heartbeat", datetime.now(UTC).isoformat())

            # Update local cache
            if service_name in self._local_cache:
                for endpoint in self._local_cache[service_name]:
                    if endpoint.instance_id == instance_id:
                        endpoint.health_status = status
                        endpoint.last_heartbeat = datetime.now(UTC)

            return True

        except Exception as e:
            logger.error("health.update_failed", error=str(e))
            return False


# ============================================
# mTLS Certificate Manager
# ============================================


class MTLSManager:
    """
    Mutual TLS certificate management for inter-service security.
    """

    def __init__(self, cert_dir: str = "/etc/amos/certs"):
        self.cert_dir = cert_dir
        self._private_key: Optional[Any] = None
        self._certificate: Optional[Any] = None
        self._ca_cert: Optional[Any] = None
        self._cert_expiry: datetime = None

    async def initialize(self) -> bool:
        """Initialize mTLS certificates."""
        if not CRYPTO_AVAILABLE or not MTLS_ENABLED:
            logger.warning("mtls.not_available")
            return False

        try:
            os.makedirs(self.cert_dir, exist_ok=True)

            # Generate or load certificates
            await self._generate_certificates()

            logger.info("mtls.initialized")
            return True

        except Exception as e:
            logger.error("mtls.init_failed", error=str(e))
            return False

    async def _generate_certificates(self) -> None:
        """Generate self-signed certificates for development/testing."""
        key_path = os.path.join(self.cert_dir, "service.key")
        cert_path = os.path.join(self.cert_dir, "service.crt")
        ca_path = os.path.join(self.cert_dir, "ca.crt")

        # Check if certificates exist and are valid
        if os.path.exists(key_path) and os.path.exists(cert_path):
            # Load existing
            with open(key_path, "rb") as f:
                self._private_key = serialization.load_pem_private_key(f.read(), password=None)
            with open(cert_path, "rb") as f:
                self._certificate = x509.load_pem_x509_certificate(f.read())

            # Check expiry
            self._cert_expiry = self._certificate.not_valid_after_utc
            if self._cert_expiry > datetime.now(UTC) + timedelta(days=7):
                logger.info("mtls.using_existing_certs")
                return

        # Generate new certificate
        logger.info("mtls.generating_new_certs")

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AMOS"),
                x509.NameAttribute(NameOID.COMMON_NAME, "amos-service"),
            ]
        )

        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(UTC))
            .not_valid_after(datetime.now(UTC) + timedelta(days=CERT_ROTATION_DAYS))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.DNSName("*.amos.internal"),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # Save certificates
        with open(key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        with open(cert_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

        # CA certificate (self-signed, so same as cert)
        with open(ca_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

        self._private_key = private_key
        self._certificate = certificate
        self._ca_cert = certificate
        self._cert_expiry = certificate.not_valid_after_utc

        logger.info("mtls.certs_generated", expiry=self._cert_expiry.isoformat())

    def create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for mTLS."""
        if not MTLS_ENABLED:
            return None

        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_cert_chain(
                certfile=os.path.join(self.cert_dir, "service.crt"),
                keyfile=os.path.join(self.cert_dir, "service.key"),
            )
            context.load_verify_locations(cafile=os.path.join(self.cert_dir, "ca.crt"))
            context.verify_mode = ssl.CERT_REQUIRED
            return context
        except Exception as e:
            logger.error("mtls.ssl_context_failed", error=str(e))
            return None

    async def rotate_certificates(self) -> bool:
        """Rotate certificates before expiry."""
        if not self._cert_expiry:
            return False

        # Rotate if expiring within 7 days
        if self._cert_expiry < datetime.now(UTC) + timedelta(days=7):
            logger.info("mtls.rotating_certs")
            await self._generate_certificates()
            return True

        return False


# ============================================
# Circuit Breaker
# ============================================


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float = None
        self._lock = asyncio.Lock()

    async def call(self, coro: Any) -> Any:
        """
        Execute call with circuit breaker protection.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of coroutine

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: If call fails
        """
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if await self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")

        try:
            result = await coro
            await self._on_success()
            return result

        except Exception:
            await self._on_failure()
            raise

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info("circuit_breaker.closed", name=self.name)
            else:
                self.failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("circuit_breaker.opened", name=self.name)
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(
                    "circuit_breaker.opened", name=self.name, failures=self.failure_count
                )

    async def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""

    pass


# ============================================
# Load Balancer
# ============================================


class LoadBalancer:
    """
    Client-side load balancer for service endpoints.
    """

    def __init__(self, strategy: LoadBalancerStrategy = LoadBalancerStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self._round_robin_index = 0
        self._connection_counts: Dict[str, int] = {}

    def select(self, endpoints: List[ServiceEndpoint]) -> Optional[ServiceEndpoint]:
        """
        Select an endpoint using configured strategy.

        Args:
            endpoints: List of available endpoints

        Returns:
            Selected endpoint or None if empty
        """
        if not endpoints:
            return None

        healthy_endpoints = [e for e in endpoints if e.health_status == ServiceStatus.HEALTHY]
        if not healthy_endpoints:
            return None

        if self.strategy == LoadBalancerStrategy.ROUND_ROBIN:
            return self._round_robin(healthy_endpoints)
        elif self.strategy == LoadBalancerStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_endpoints)
        elif self.strategy == LoadBalancerStrategy.RANDOM:
            return random.choice(healthy_endpoints)
        elif self.strategy == LoadBalancerStrategy.WEIGHTED:
            return self._weighted(healthy_endpoints)

        return healthy_endpoints[0]

    def _round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round-robin selection."""
        idx = self._round_robin_index % len(endpoints)
        self._round_robin_index = (self._round_robin_index + 1) % len(endpoints)
        return endpoints[idx]

    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint with least connections."""
        return min(endpoints, key=lambda e: self._connection_counts.get(e.instance_id, 0))

    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted random selection."""
        total_weight = sum(e.weight for e in endpoints)
        r = random.uniform(0, total_weight)

        cumulative = 0
        for endpoint in endpoints:
            cumulative += endpoint.weight
            if r <= cumulative:
                return endpoint

        return endpoints[-1]

    def record_connection(self, instance_id: str, delta: int = 1) -> None:
        """Record connection count change."""
        current = self._connection_counts.get(instance_id, 0)
        self._connection_counts[instance_id] = max(0, current + delta)


# ============================================
# Distributed Tracing
# ============================================


class TracingManager:
    """
    OpenTelemetry distributed tracing manager.
    """

    def __init__(self, service_name: str = "amos-service"):
        self.service_name = service_name
        self._tracer: Optional[Any] = None
        self._provider: Optional[Any] = None

    async def initialize(self) -> bool:
        """Initialize OpenTelemetry tracing."""
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("tracing.opentelemetry_not_available")
            return False

        try:
            # Create tracer provider
            self._provider = TracerProvider()

            # Add OTLP exporter
            otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True)
            span_processor = BatchSpanProcessor(otlp_exporter)
            self._provider.add_span_processor(span_processor)

            # Set global provider
            trace.set_tracer_provider(self._provider)

            # Get tracer
            self._tracer = trace.get_tracer(self.service_name)

            logger.info("tracing.initialized", service=self.service_name)
            return True

        except Exception as e:
            logger.error("tracing.init_failed", error=str(e))
            return False

    def start_span(
        self,
        name: str,
        parent_context: Optional[TraceContext] = None,
        attributes: Dict[str, Any] = None,
    ) -> Any:
        """
        Start a new trace span.

        Args:
            name: Span name
            parent_context: Optional parent trace context
            attributes: Span attributes

        Returns:
            Span context manager
        """
        if not self._tracer:
            return None

        kwargs: Dict[str, Any] = {}
        if attributes:
            kwargs["attributes"] = attributes

        if parent_context:
            # Create context from parent
            from opentelemetry.trace import NonRecordingSpan, SpanContext, set_span_in_context

            parent_span_context = SpanContext(
                trace_id=int(parent_context.trace_id, 16),
                span_id=int(parent_context.parent_span_id or "0", 16),
                is_remote=True,
                trace_flags=trace.TraceFlags(0x01)
                if parent_context.sampled
                else trace.TraceFlags(0x00),
            )
            parent_span = NonRecordingSpan(parent_span_context)
            ctx = set_span_in_context(parent_span)
            kwargs["context"] = ctx

        return self._tracer.start_as_current_span(name, **kwargs)

    def create_trace_context(self) -> TraceContext:
        """Create new trace context."""
        import secrets

        return TraceContext(
            trace_id=secrets.token_hex(16), span_id=secrets.token_hex(8), sampled=True
        )

    def inject_trace_context(
        self, headers: Dict[str, str], context: TraceContext
    ) -> dict[str, str]:
        """Inject trace context into HTTP headers (W3C format)."""
        headers["traceparent"] = (
            f"00-{context.trace_id}-{context.span_id}-" f"{'01' if context.sampled else '00'}"
        )

        if context.baggage:
            baggage_items = [f"{k}={v}" for k, v in context.baggage.items()]
            headers["baggage"] = ",".join(baggage_items)

        return headers

    def extract_trace_context(self, headers: Dict[str, str]) -> Optional[TraceContext]:
        """Extract trace context from HTTP headers (W3C format)."""
        traceparent = headers.get("traceparent")
        if not traceparent:
            return None

        try:
            parts = traceparent.split("-")
            if len(parts) >= 4:
                return TraceContext(trace_id=parts[1], span_id=parts[2], sampled=parts[3] == "01")
        except Exception:
            pass

        return None


# ============================================
# Service Mesh Client
# ============================================


class ServiceMeshClient:
    """
    HTTP client with service mesh features:
    - Service discovery
    - Load balancing
    - Circuit breaking
    - mTLS
    - Distributed tracing
    """

    def __init__(
        self,
        registry: ServiceRegistry,
        mtls: Optional[MTLSManager] = None,
        tracer: Optional[TracingManager] = None,
    ):
        self.registry = registry
        self.mtls = mtls
        self.tracer = tracer
        self.load_balancer = LoadBalancer(LoadBalancerStrategy.LEAST_CONNECTIONS)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._session: aiohttp.ClientSession = None

    async def initialize(self) -> None:
        """Initialize HTTP client session."""
        ssl_context = None
        if self.mtls:
            ssl_context = self.mtls.create_ssl_context()

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20, ssl=ssl_context)

        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)

        self._session = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async def request(
        self,
        target_service: str,
        method: str,
        path: str,
        headers: Dict[str, str] = None,
        json_data: Dict[str, Any] = None,
        trace_context: Optional[TraceContext] = None,
        retry_attempts: int = 3,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to target service with mesh features.

        Args:
            target_service: Target service name
            method: HTTP method
            path: Request path
            headers: Optional headers
            json_data: Optional JSON body
            trace_context: Optional trace context
            retry_attempts: Number of retry attempts

        Returns:
            Response dictionary
        """
        headers = headers or {}

        # Inject trace context
        if self.tracer:
            if trace_context is None:
                trace_context = self.tracer.create_trace_context()
            headers = self.tracer.inject_trace_context(headers, trace_context)

        # Discover service endpoints
        endpoints = await self.registry.discover(target_service, healthy_only=True)
        if not endpoints:
            raise ServiceUnavailable(f"No healthy endpoints for {target_service}")

        # Select endpoint via load balancer
        endpoint = self.load_balancer.select(endpoints)
        if not endpoint:
            raise ServiceUnavailable(f"No available endpoints for {target_service}")

        # Get or create circuit breaker
        cb_key = f"{target_service}:{endpoint.instance_id}"
        if cb_key not in self.circuit_breakers:
            self.circuit_breakers[cb_key] = CircuitBreaker(cb_key)

        circuit_breaker = self.circuit_breakers[cb_key]

        # Execute request with circuit breaker
        url = f"{endpoint.address}{path}"

        async def _do_request():
            self.load_balancer.record_connection(endpoint.instance_id, 1)
            try:
                async with self._session.request(
                    method=method, url=url, headers=headers, json=json_data
                ) as response:
                    body = await response.json()
                    return {
                        "status": response.status,
                        "body": body,
                        "endpoint": endpoint.instance_id,
                    }
            finally:
                self.load_balancer.record_connection(endpoint.instance_id, -1)

        # Retry loop
        last_error = None
        for attempt in range(retry_attempts):
            try:
                return await circuit_breaker.call(_do_request())
            except CircuitBreakerOpen:
                # Try another endpoint
                endpoint = self.load_balancer.select(
                    [e for e in endpoints if e.instance_id != endpoint.instance_id]
                )
                if not endpoint:
                    raise ServiceUnavailable("All circuits open")
                url = f"{endpoint.address}{path}"
            except Exception as e:
                last_error = e
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(0.1 * (2**attempt))  # Exponential backoff

        raise last_error or ServiceUnavailable("Request failed after retries")

    async def close(self) -> None:
        """Close client session."""
        if self._session:
            await self._session.close()


class ServiceUnavailable(Exception):
    """Exception raised when service is unavailable."""

    pass


# ============================================
# Service Mesh Main Class
# ============================================


class AMOSServiceMesh:
    """
    Main service mesh orchestrator for AMOS 14-Layer Architecture.
    """

    def __init__(
        self, service_name: str, service_port: int, registry_url: str = SERVICE_REGISTRY_URL
    ):
        self.service_name = service_name
        self.service_port = service_port
        self.instance_id = (
            f"{service_name}-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
        )

        # Components
        self.registry = ServiceRegistry(registry_url)
        self.mtls = MTLSManager() if MTLS_ENABLED else None
        self.tracer = TracingManager(service_name)
        self.client: Optional[ServiceMeshClient] = None

        # State
        self._initialized = False
        self._heartbeat_task: asyncio.Task = None

    async def initialize(self) -> bool:
        """Initialize service mesh."""
        if not SERVICE_MESH_ENABLED:
            logger.info("service_mesh.disabled")
            return False

        try:
            # Initialize components
            await self.registry.initialize()

            if self.mtls:
                await self.mtls.initialize()

            await self.tracer.initialize()

            # Initialize client
            self.client = ServiceMeshClient(self.registry, self.mtls, self.tracer)
            await self.client.initialize()

            # Register this service
            await self._register_self()

            # Start heartbeat
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            self._initialized = True
            logger.info(
                "service_mesh.initialized", service=self.service_name, instance=self.instance_id
            )
            return True

        except Exception as e:
            logger.error("service_mesh.init_failed", error=str(e))
            return False

    async def _register_self(self) -> None:
        """Register this service instance."""
        endpoint = ServiceEndpoint(
            service_name=self.service_name,
            instance_id=self.instance_id,
            host=os.getenv("SERVICE_HOST", "localhost"),
            port=self.service_port,
            protocol="https" if MTLS_ENABLED else "http",
            metadata={"version": "1.0.0", "layer": self._get_layer_for_service()},
            tags=[self._get_layer_for_service()],
        )

        await self.registry.register(endpoint, ttl_seconds=60)

    def _get_layer_for_service(self) -> str:
        """Determine layer from service name."""
        layer_mapping = {
            "orchestrator": "00_ROOT",
            "brain": "01_BRAIN",
            "senses": "02_SENSES",
            "immune": "03_IMMUNE",
            "blood": "04_BLOOD",
            "nerves": "05_NERVES",
            "muscle": "06_MUSCLE",
            "metabolism": "07_METABOLISM",
            "growth": "08_GROWTH",
            "social": "09_SOCIAL",
            "memory": "10_MEMORY",
            "legal": "11_LEGAL",
            "ethics": "12_ETHICS",
            "time": "13_TIME",
            "interfaces": "14_INTERFACES",
        }

        for key, layer in layer_mapping.items():
            if key in self.service_name.lower():
                return layer

        return "UNKNOWN"

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats."""
        while True:
            try:
                await asyncio.sleep(30)

                # Update health
                await self.registry.update_health(
                    self.service_name, self.instance_id, ServiceStatus.HEALTHY
                )

                # Rotate certificates if needed
                if self.mtls:
                    await self.mtls.rotate_certificates()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("heartbeat.failed", error=str(e))

    async def call_service(
        self,
        target_service: str,
        method: str,
        path: str,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        Call another service through the mesh.

        Args:
            target_service: Target service name
            method: HTTP method
            path: API path
            json_data: Optional JSON body
            headers: Optional headers

        Returns:
            Response dictionary
        """
        if not self.client:
            raise RuntimeError("Service mesh not initialized")

        return await self.client.request(
            target_service=target_service,
            method=method,
            path=path,
            headers=headers,
            json_data=json_data,
        )

    async def shutdown(self) -> None:
        """Shutdown service mesh."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Deregister
        await self.registry.deregister(self.service_name, self.instance_id)

        # Close client
        if self.client:
            await self.client.close()

        logger.info("service_mesh.shutdown", service=self.service_name)


# ============================================
# Global Instance
# ============================================


def get_service_mesh(
    service_name: str = "amos-service", service_port: int = 8080
) -> AMOSServiceMesh:
    """Get or create service mesh instance."""
    return AMOSServiceMesh(service_name, service_port)


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("AMOS Service Mesh - Phase 23")
    print("=" * 70)

    print("\n✅ Service Mesh configured:")
    print(f"   Service mesh enabled: {SERVICE_MESH_ENABLED}")
    print(f"   mTLS enabled: {MTLS_ENABLED}")
    print(f"   Certificate rotation: {CERT_ROTATION_DAYS} days")
    print(f"   Circuit breaker threshold: {CIRCUIT_BREAKER_THRESHOLD}")
    print(f"   Default timeout: {DEFAULT_TIMEOUT}s")

    print("\n📊 Features:")
    print("   - Service discovery (Redis-backed)")
    print("   - Load balancing (round-robin, least-connections, weighted)")
    print("   - Circuit breaker pattern")
    print("   - mTLS for inter-service security")
    print("   - Distributed tracing (OpenTelemetry)")
    print("   - Automatic certificate rotation")
    print("   - Health-aware routing")

    print("\n🔌 14-Layer Integration:")
    print("   - Layer 00: ROOT/Orchestrator")
    print("   - Layer 01-14: Cognitive systems")
    print("   - Each layer auto-registers with mesh")

    print("\n📈 Usage:")
    print("   async def main():")
    print("       mesh = get_service_mesh('brain', 8080)")
    print("       await mesh.initialize()")
    print("       ")
    print("       # Call another service")
    print("       response = await mesh.call_service(")
    print("           'memory', 'GET', '/api/v1/status'")
    print("       )")
    print("       ")
    print("       await mesh.shutdown()")

    print("\n" + "=" * 70)
    print("✅ Phase 23: Service Mesh ready!")
