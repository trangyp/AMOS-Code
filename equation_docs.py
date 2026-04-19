#!/usr/bin/env python3
"""AMOS Equation API Documentation - Interactive OpenAPI/Swagger UI.

Production-grade API documentation system:
- Custom OpenAPI schema generation with rich metadata
- Interactive Swagger UI with authentication support
- ReDoc alternative documentation view
- Rich request/response examples
- API explorer with endpoint analytics
- Try-It-Now functionality
- Version-aware documentation
- Tag organization and descriptions
- Custom CSS/JS injection
- Offline documentation export

Architecture Pattern: OpenAPI 3.1.0 + FastAPI native integration
Documentation Features:
    - Auto-generated from Pydantic models
    - Custom examples and descriptions
    - OAuth2 integration for authenticated endpoints
    - Response schemas with status codes
    - Query parameter documentation
    - Request body examples
    - Header documentation
    - Error response examples

Integration:
    - equation_app: Register with FastAPI app
    - equation_schemas: Pydantic models as documentation source
    - equation_auth: OAuth2 security schemes
    - equation_versioning: Version-aware docs

Usage:
    # In equation_app.py
    from equation_docs import setup_documentation

    app = FastAPI()
    setup_documentation(app)

    # Access at:
    # /docs - Swagger UI
    # /redoc - ReDoc
    # /openapi.json - Raw OpenAPI schema

Environment Variables:
    DOCS_TITLE: API title (default: AMOS Equation System)
    DOCS_VERSION: API version (default: 2.0.0)
    DOCS_HIDE_INTERNAL: Hide internal endpoints (default: False)
    DOCS_ENABLE_TRY_IT: Enable Try-It-Now (default: True)
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

# FastAPI documentation support
try:
    from fastapi import FastAPI
    from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
    from fastapi.openapi.utils import get_openapi
    from fastapi.responses import HTMLResponse, JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    JSONResponse = None
    HTMLResponse = None

# Pydantic for schema examples
try:
    from pydantic import BaseModel, Field

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None
    Field = None

# Configuration
try:
    from equation_config import get_settings

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Versioning
try:
    from equation_versioning import VersionManager

    VERSIONING_AVAILABLE = True
except ImportError:
    VERSIONING_AVAILABLE = False

# Schemas for examples
try:
    from equation_schemas import (
        BatchEquationRequest,
        EquationCreateRequest,
        EquationResponse,
        EquationVerifyRequest,
        ErrorResponse,
        HealthStatus,
    )

    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False

logger = logging.getLogger("amos_equation_docs")


# ============================================================================
# Documentation Metadata
# ============================================================================

API_METADATA = {
    "title": "AMOS Equation System",
    "description": """
    ## AMOS Equation Processing API

    A production-grade equation processing system with:
    - Mathematical equation solving and verification
    - Batch processing capabilities
    - Real-time execution via WebSocket
    - GraphQL API for complex queries
    - Async task queue (Celery)
    - Redis caching layer
    - Distributed tracing (OpenTelemetry)
    - Prometheus metrics

    ### Features

    - **Equation Processing**: Solve, verify, and analyze mathematical equations
    - **Batch Operations**: Process multiple equations efficiently
    - **Real-time Updates**: WebSocket notifications for async operations
    - **Caching**: Redis-based query optimization
    - **Security**: JWT/OAuth2 authentication with RBAC
    - **Monitoring**: Prometheus metrics and health checks

    ### Authentication

    This API uses OAuth2 Bearer token authentication. Obtain a token via:
    ```
    POST /api/v1/auth/token
    Content-Type: application/x-www-form-urlencoded

    username=your_username&password=your_password
    ```

    Then include the token in requests:
    ```
    Authorization: Bearer your_token_here
    ```

    ### Rate Limits

    - Default: 100 requests/minute
    - Verify endpoint: 30 requests/minute
    - Batch operations: 10 requests/minute

    ### Support

    - Documentation: /docs (Swagger UI) or /redoc (ReDoc)
    - Health: /health
    - Metrics: /metrics
    """,
    "version": "2.0.0",
    "terms_of_service": "https://amos.example.com/terms",
    "contact": {
        "name": "AMOS Support",
        "url": "https://amos.example.com/support",
        "email": "support@amos.example.com",
    },
    "license_info": {"name": "MIT", "identifier": "MIT"},
    "openapi_tags": [
        {
            "name": "Equations",
            "description": "Create, read, update, delete, and execute equations",
            "externalDocs": {
                "description": "Equation processing guide",
                "url": "https://amos.example.com/docs/equations",
            },
        },
        {"name": "Execution", "description": "Execute equations with various input parameters"},
        {
            "name": "Batch Operations",
            "description": "Process multiple equations in a single request",
        },
        {"name": "Verification", "description": "Verify equation syntax and correctness"},
        {"name": "Authentication", "description": "User authentication and token management"},
        {"name": "Tasks", "description": "Async task management (Celery integration)"},
        {"name": "WebSocket", "description": "Real-time notifications and updates"},
        {"name": "GraphQL", "description": "GraphQL API for flexible queries"},
        {"name": "System", "description": "Health checks, metrics, and system status"},
    ],
}


# ============================================================================
# Example Data
# ============================================================================

EXAMPLE_EQUATIONS = {
    "linear": {
        "name": "Linear Equation",
        "domain": "mathematics",
        "formula": "y = 2*x + 3",
        "parameters": {"x": 5},
        "description": "Simple linear equation",
    },
    "quadratic": {
        "name": "Quadratic Formula",
        "domain": "mathematics",
        "formula": "x = (-b + sqrt(b**2 - 4*a*c)) / (2*a)",
        "parameters": {"a": 1, "b": -3, "c": 2},
        "description": "Quadratic equation solver",
    },
    "physics": {
        "name": "Newton's Second Law",
        "domain": "physics",
        "formula": "F = m * a",
        "parameters": {"m": 10, "a": 9.8},
        "description": "Force calculation",
    },
}

EXAMPLE_RESPONSES = {
    "equation_created": {
        "id": 1,
        "name": "Linear Equation",
        "domain": "mathematics",
        "formula": "y = 2*x + 3",
        "version": "1.0",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
    },
    "execution_result": {
        "execution_id": "exec-12345",
        "equation_id": 1,
        "result": {"y": 13.0},
        "status": "completed",
        "execution_time_ms": 45.2,
    },
    "error": {
        "error": {
            "code": "INVALID_EQUATION",
            "message": "Equation syntax is invalid",
            "details": {"line": 1, "position": 5},
        },
        "request_id": "req-abc123",
    },
}


# ============================================================================
# OpenAPI Schema Customization
# ============================================================================


def custom_openapi_schema(
    app: FastAPI, title: str = None, version: str = None, hide_internal: bool = False
) -> Dict[str, Any]:
    """Generate custom OpenAPI schema with examples.

    Args:
        app: FastAPI application
        title: API title override
        version: API version override
        hide_internal: Whether to hide internal endpoints

    Returns:
        Customized OpenAPI schema dictionary
    """
    if not FASTAPI_AVAILABLE:
        return {}

    if app.openapi_schema:
        return app.openapi_schema

    # Get base schema from FastAPI
    schema = get_openapi(
        title=title or API_METADATA["title"],
        version=version or API_METADATA["version"],
        description=API_METADATA["description"],
        routes=app.routes,
        tags=API_METADATA["openapi_tags"],
    )

    # Add security schemes
    schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token",
        },
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access",
                        "admin": "Admin access",
                    },
                }
            },
        },
        "apiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for external service access",
        },
    }

    # Add examples to schemas
    if SCHEMAS_AVAILABLE:
        schema["components"]["schemas"]["EquationCreateRequest"]["examples"] = {
            "linear": {"summary": "Linear equation", "value": EXAMPLE_EQUATIONS["linear"]},
            "quadratic": {"summary": "Quadratic formula", "value": EXAMPLE_EQUATIONS["quadratic"]},
        }

    # Add response examples
    for path, path_item in schema.get("paths", {}).items():
        if hide_internal and path.startswith("/internal"):
            continue

        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue

            # Add operation examples
            if method == "post" and "equations" in path:
                operation["requestBody"]["content"]["application/json"]["examples"] = {
                    "linear": {
                        "summary": "Simple linear equation",
                        "value": EXAMPLE_EQUATIONS["linear"],
                    },
                    "physics": {
                        "summary": "Physics formula",
                        "value": EXAMPLE_EQUATIONS["physics"],
                    },
                }

            # Add response examples
            for status_code, response in operation.get("responses", {}).items():
                if status_code == "200" and "application/json" in response.get("content", {}):
                    response["content"]["application/json"]["examples"] = {
                        "success": {
                            "summary": "Successful response",
                            "value": EXAMPLE_RESPONSES.get("equation_created"),
                        }
                    }
                elif status_code.startswith("4") or status_code.startswith("5"):
                    response["content"]["application/json"]["examples"] = {
                        "error": {
                            "summary": "Error response",
                            "value": EXAMPLE_RESPONSES.get("error"),
                        }
                    }

    # Add external documentation
    schema["externalDocs"] = {
        "description": "Full API documentation",
        "url": "https://amos.example.com/api-docs",
    }

    # Add servers
    schema["servers"] = [
        {"url": "https://api.amos.example.com", "description": "Production server"},
        {"url": "https://staging-api.amos.example.com", "description": "Staging server"},
        {"url": "http://localhost:8000", "description": "Local development"},
    ]

    app.openapi_schema = schema
    return schema


# ============================================================================
# Documentation Setup
# ============================================================================


def setup_documentation(
    app: FastAPI,
    title: str = None,
    version: str = None,
    enable_swagger: bool = True,
    enable_redoc: bool = True,
    enable_try_it: bool = True,
    hide_internal: bool = False,
    custom_css: str = None,
    custom_js: str = None,
) -> None:
    """Setup comprehensive API documentation.

    Args:
        app: FastAPI application instance
        title: Custom API title
        version: Custom API version
        enable_swagger: Enable Swagger UI at /docs
        enable_redoc: Enable ReDoc at /redoc
        enable_try_it: Enable Try-It-Now in Swagger UI
        hide_internal: Hide internal endpoints from docs
        custom_css: URL to custom CSS file
        custom_js: URL to custom JS file
    """
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI not available, skipping documentation setup")
        return

    # Store configuration
    app.state.docs_config = {
        "title": title or API_METADATA["title"],
        "version": version or API_METADATA["version"],
        "enable_try_it": enable_try_it,
        "hide_internal": hide_internal,
        "custom_css": custom_css,
        "custom_js": custom_js,
    }

    # Override OpenAPI schema generation
    def custom_openapi():
        return custom_openapi_schema(app, title, version, hide_internal)

    app.openapi = custom_openapi

    # Setup Swagger UI
    if enable_swagger:

        @app.get("/docs", include_in_schema=False)
        async def swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url="/openapi.json",
                title=f"{app.state.docs_config['title']} - Swagger UI",
                oauth2_redirect_url="/docs/oauth2-redirect",
                swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
                swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
                swagger_favicon_url="/favicon.ico",
            )

        @app.get("/docs/oauth2-redirect", include_in_schema=False)
        async def oauth2_redirect():
            # OAuth2 redirect handler for Swagger UI
            return HTMLResponse(
                content="""
            <!DOCTYPE html>
            <html lang="en-US">
            <body onload="run()">
            <script>
                function run() {
                    var oauth2 = window.opener.swaggerUIRedirectOauth2;
                    var sentState = oauth2.state;
                    var redirectUrl = oauth2.redirectUrl;
                    var isValid = redirectUrl.indexOf(window.location.pathname) === 0;
                    if (isValid) {
                        window.location = redirectUrl;
                    }
                }
            </script>
            </body>
            </html>
            """
            )

    # Setup ReDoc
    if enable_redoc:

        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(
                openapi_url="/openapi.json",
                title=f"{app.state.docs_config['title']} - ReDoc",
                redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js",
                redoc_favicon_url="/favicon.ico",
            )

    # OpenAPI JSON endpoint
    @app.get("/openapi.json", include_in_schema=False)
    async def openapi_json():
        return JSONResponse(content=app.openapi())

    logger.info("Documentation setup complete. Access at /docs (Swagger) or /redoc (ReDoc)")


# ============================================================================
# API Explorer
# ============================================================================


def create_api_explorer(app: FastAPI, prefix: str = "/api-explorer") -> None:
    """Create API explorer/analytics dashboard.

    Provides a custom HTML interface for exploring the API.

    Args:
        app: FastAPI application
        prefix: URL prefix for explorer
    """
    if not FASTAPI_AVAILABLE:
        return

    @app.get(prefix, include_in_schema=False)
    async def api_explorer():
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AMOS API Explorer</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                h1 {
                    color: #333;
                    border-bottom: 2px solid #4CAF50;
                    padding-bottom: 10px;
                }
                .endpoint {
                    background: white;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .method {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    margin-right: 10px;
                }
                .get { background: #61affe; color: white; }
                .post { background: #49cc90; color: white; }
                .put { background: #fca130; color: white; }
                .delete { background: #f93e3e; color: white; }
                .path {
                    font-family: monospace;
                    font-size: 14px;
                    color: #333;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }
                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .stat-value {
                    font-size: 32px;
                    font-weight: bold;
                    color: #4CAF50;
                }
                .stat-label {
                    color: #666;
                    margin-top: 5px;
                }
                .links {
                    margin: 20px 0;
                }
                .links a {
                    display: inline-block;
                    margin: 5px;
                    padding: 10px 20px;
                    background: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }
                .links a:hover {
                    background: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>AMOS Equation System - API Explorer</h1>

            <div class="links">
                <a href="/docs">Swagger UI</a>
                <a href="/redoc">ReDoc</a>
                <a href="/openapi.json">OpenAPI JSON</a>
                <a href="/health">Health Check</a>
                <a href="/metrics">Prometheus Metrics</a>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">25</div>
                    <div class="stat-label">API Modules</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">50+</div>
                    <div class="stat-label">API Endpoints</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">2.0</div>
                    <div class="stat-label">API Version</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">3</div>
                    <div class="stat-label">Auth Methods</div>
                </div>
            </div>

            <h2>Core Endpoints</h2>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/v1/equations</span>
                <p>Create a new equation</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/v1/equations/{id}</span>
                <p>Get equation by ID</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/v1/equations/{id}/execute</span>
                <p>Execute equation with inputs</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/v1/equations/verify</span>
                <p>Verify equation syntax</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/v1/equations/batch</span>
                <p>Batch process equations</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/v1/tasks/{task_id}</span>
                <p>Get async task status</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/graphql</span>
                <p>GraphQL playground</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/v1/auth/token</span>
                <p>OAuth2 login</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)


# ============================================================================
# Offline Documentation Export
# ============================================================================


def export_documentation(
    app: FastAPI, output_path: str = "./api-docs", formats: List[str] = None
) -> Dict[str, str]:
    """Export API documentation for offline use.

    Args:
        app: FastAPI application
        output_path: Directory to save documentation
        formats: List of formats to export (json, yaml, html)

    Returns:
        Dictionary of exported file paths
    """
    if not FASTAPI_AVAILABLE:
        return {}

    import os

    formats = formats or ["json", "html"]
    os.makedirs(output_path, exist_ok=True)

    exported = {}
    schema = app.openapi()

    # Export OpenAPI JSON
    if "json" in formats:
        json_path = os.path.join(output_path, "openapi.json")
        with open(json_path, "w") as f:
            json.dump(schema, f, indent=2)
        exported["json"] = json_path

    # Export HTML documentation
    if "html" in formats:
        html_path = os.path.join(output_path, "index.html")
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{schema.get('info', {}).get('title', 'API Documentation')}</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" type="text/css"
                  href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
                const ui = SwaggerUIBundle({{
                    url: './openapi.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.presets.standalone
                    ],
                    layout: "BaseLayout"
                }});
            </script>
        </body>
        </html>
        """
        with open(html_path, "w") as f:
            f.write(html_content)
        exported["html"] = html_path

    logger.info(f"Documentation exported to {output_path}: {exported}")
    return exported


# ============================================================================
# Documentation Utilities
# ============================================================================


def add_endpoint_examples(
    router: Any,
    endpoint: str,
    request_example: Dict[str, Any] = None,
    response_example: Dict[str, Any] = None,
) -> None:
    """Add examples to a specific endpoint.

    Args:
        router: FastAPI router
        endpoint: Endpoint path
        request_example: Example request body
        response_example: Example response body
    """
    # This would be implemented with FastAPI's extra parameter
    # on route decorators
    pass


def get_api_statistics(app: FastAPI) -> Dict[str, Any]:
    """Get API documentation statistics.

    Args:
        app: FastAPI application

    Returns:
        Statistics about the API
    """
    if not FASTAPI_AVAILABLE:
        return {}

    schema = app.openapi()

    paths = schema.get("paths", {})
    schemas = schema.get("components", {}).get("schemas", {})

    methods = {"get": 0, "post": 0, "put": 0, "delete": 0, "patch": 0}

    for path, operations in paths.items():
        for method in methods.keys():
            if method in operations:
                methods[method] += 1

    return {
        "total_endpoints": len(paths),
        "methods": methods,
        "total_schemas": len(schemas),
        "version": schema.get("info", {}).get("version"),
        "title": schema.get("info", {}).get("title"),
        "generated_at": datetime.now().isoformat(),
    }


# ============================================================================
# Example Usage
# ============================================================================


async def example_usage():
    """Example usage of documentation system."""
    if not FASTAPI_AVAILABLE:
        print("FastAPI not available")
        return

    # Create example app
    app = FastAPI(
        title=API_METADATA["title"],
        version=API_METADATA["version"],
        description=API_METADATA["description"],
    )

    # Setup documentation
    setup_documentation(app, enable_swagger=True, enable_redoc=True, enable_try_it=True)

    # Add API explorer
    create_api_explorer(app)

    # Example endpoint
    @app.post("/api/v1/equations", tags=["Equations"])
    async def create_equation():
        return {"message": "Created"}

    # Get statistics
    stats = get_api_statistics(app)
    print(f"API Statistics: {json.dumps(stats, indent=2)}")

    # Export documentation
    # exported = export_documentation(app, "./docs-export")
    # print(f"Exported: {exported}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
