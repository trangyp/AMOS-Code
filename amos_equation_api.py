"""AMOS Equation API - FastAPI REST API for equation library.

Provides REST endpoints for accessing 32+ equations with:
- Equation discovery and search
- Execution with JSON parameters
- Batch processing
- Pattern-based filtering
- Isomorphism detection

Usage:
    uvicorn amos_equation_api:app --reload

    # API documentation at:
    # http://localhost:8000/docs (Swagger UI)
    # http://localhost:8000/redoc (ReDoc)

Endpoints:
    GET  /api/v1/equations - List all equations
    GET  /api/v1/equations/{name} - Get equation details
    POST /api/v1/equations/{name}/execute - Execute equation
    POST /api/v1/equations/batch - Batch execute
    GET  /api/v1/patterns - List mathematical patterns
    GET  /api/v1/isomorphisms - Get cross-domain isomorphisms
    GET  /api/v1/stats - Library statistics
"""

import json
from typing import Any, Dict, List

import numpy as np

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Dummy classes for type checking
    class FastAPI:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):
            return lambda f: f

        def post(self, *args, **kwargs):
            return lambda f: f

        def add_middleware(self, *args, **kwargs):
            pass

    class BaseModel:
        pass

    class HTTPException(Exception):
        pass

    class Query:
        def __init__(self, *args, **kwargs):
            pass

    HTMLResponse = JSONResponse = None

try:
    from amos_equation_jax import JAXEquationKernel

    KERNEL = JAXEquationKernel()
    JAX_MODE = KERNEL.is_jax_available()
    KERNEL_TYPE = "jax"
except ImportError:
    try:
        from amos_equation_extended import ExtendedEquationKernel

        KERNEL = ExtendedEquationKernel()
        JAX_MODE = False
        KERNEL_TYPE = "extended"
    except ImportError:
        # Fallback to SuperBrain bridge
        from amos_superbrain_equation_bridge import AMOSSuperBrainBridge

        KERNEL = AMOSSuperBrainBridge().registry
        JAX_MODE = False
        KERNEL_TYPE = "superbrain"

# ============================================================================
# Pydantic Models for API
# ============================================================================

if FASTAPI_AVAILABLE:

    class EquationMetadata(BaseModel):
        name: str
        domain: str
        pattern: str
        formula: str
        description: str
        invariants: List[str]
        parameters: Dict[str, str]

    class ExecuteRequest(BaseModel):
        parameters: Dict[str, Any] = Field(default_factory=dict)
        use_jit: bool = Field(default=True, description="Use JIT if available")

    class ExecuteResponse(BaseModel):
        equation: str
        value: Any
        invariants_valid: bool
        errors: List[str]
        execution_time_ms: float = None
        jax_accelerated: bool = False

    class BatchRequest(BaseModel):
        equation: str
        batch_params: List[dict[str, Any]]

    class BatchResponse(BaseModel):
        equation: str
        results: List[Any]
        successful: int
        failed: int

    class IsomorphismInfo(BaseModel):
        equation1: str
        equation2: str
        similarity: str
        description: str

    class LibraryStats(BaseModel):
        total_equations: int
        domains_covered: int
        patterns_identified: int
        isomorphisms_found: int
        jax_accelerated: bool
        version: str = "9.0.0"

# ============================================================================
# Numpy JSON Encoder
# ============================================================================


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles NumPy arrays and types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def numpy_to_json(obj: Any) -> Any:
    """Convert NumPy objects to JSON-serializable format."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: numpy_to_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [numpy_to_json(item) for item in obj]
    return obj


# ============================================================================
# FastAPI Application
# ============================================================================

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="AMOS Equation API",
        description="REST API for the AMOS Mathematical Equation Library",
        version="9.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = None

# ============================================================================
# API Endpoints
# ============================================================================

if FASTAPI_AVAILABLE and app:

    @app.get("/")
    async def root() -> Dict[str, str]:
        """Root endpoint with API info."""
        return {
            "name": "AMOS Equation API",
            "version": "9.0.0",
            "documentation": "/docs",
            "equations_endpoint": "/api/v1/equations",
        }

    @app.get("/api/v1/stats", response_model=LibraryStats)
    async def get_stats() -> LibraryStats:
        """Get library statistics."""
        all_eqs = KERNEL.get_all_equations()
        domains = set(eq.domain for eq in all_eqs)
        patterns = set(eq.pattern.value for eq in all_eqs)
        isos = KERNEL.find_isomorphisms()

        return LibraryStats(
            total_equations=len(all_eqs),
            domains_covered=len(domains),
            patterns_identified=len(patterns),
            isomorphisms_found=len(isos),
            jax_accelerated=JAX_MODE,
        )

    @app.get("/api/v1/equations")
    async def list_equations(
        domain: str = Query(None, description="Filter by domain"),
        pattern: str = Query(None, description="Filter by pattern"),
        search: str = Query(None, description="Search in name/description"),
    ) -> List[dict[str, Any]]:
        """List all equations with optional filtering."""
        equations = KERNEL.get_all_equations()

        # Apply filters
        if domain:
            equations = [eq for eq in equations if eq.domain == domain]
        if pattern:
            equations = [eq for eq in equations if eq.pattern.value == pattern]
        if search:
            search_lower = search.lower()
            equations = [
                eq
                for eq in equations
                if (search_lower in eq.name.lower() or search_lower in eq.description.lower())
            ]

        # Convert to dict
        result = []
        for eq in equations:
            result.append(
                {
                    "name": eq.name,
                    "domain": eq.domain,
                    "pattern": eq.pattern.value,
                    "formula": eq.formula,
                    "description": eq.description,
                    "invariants": eq.invariants,
                    "parameters": eq.parameters,
                }
            )

        return result

    @app.get("/api/v1/equations/{name}")
    async def get_equation(name: str) -> Dict[str, Any]:
        """Get detailed information about a specific equation."""
        all_eqs = KERNEL.get_all_equations()
        eq = next((e for e in all_eqs if e.name == name), None)

        if not eq:
            raise HTTPException(status_code=404, detail=f"Equation '{name}' not found")

        return {
            "name": eq.name,
            "domain": eq.domain,
            "pattern": eq.pattern.value,
            "formula": eq.formula,
            "description": eq.description,
            "invariants": eq.invariants,
            "parameters": eq.parameters,
        }

    @app.post("/api/v1/equations/{name}/execute")
    async def execute_equation(name: str, request: ExecuteRequest) -> ExecuteResponse:
        """Execute an equation with given parameters."""
        import time

        start_time = time.perf_counter()

        # Check if equation exists
        all_eqs = KERNEL.get_all_equations()
        eq = next((e for e in all_eqs if e.name == name), None)
        if not eq:
            raise HTTPException(status_code=404, detail=f"Equation '{name}' not found")

        # Convert parameters for NumPy/JAX
        params = request.parameters
        for key, value in params.items():
            if isinstance(value, list):
                params[key] = np.array(value)

        # Execute
        try:
            result = KERNEL.execute(name, params, use_jit=request.use_jit)
            execution_time = (time.perf_counter() - start_time) * 1000

            return ExecuteResponse(
                equation=name,
                value=numpy_to_json(result.value),
                invariants_valid=result.invariants_valid,
                errors=result.errors,
                execution_time_ms=round(execution_time, 3),
                jax_accelerated=JAX_MODE and request.use_jit,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/v1/equations/batch")
    async def batch_execute(request: BatchRequest) -> BatchResponse:
        """Execute equation on a batch of inputs."""
        # Check if equation exists
        all_eqs = KERNEL.get_all_equations()
        eq = next((e for e in all_eqs if e.name == request.equation), None)
        if not eq:
            raise HTTPException(status_code=404, detail=f"Equation '{request.equation}' not found")

        results = []
        successful = 0
        failed = 0

        # Convert batch params
        for params in request.batch_params:
            for key, value in params.items():
                if isinstance(value, list):
                    params[key] = np.array(value)

        # Execute batch
        try:
            if hasattr(KERNEL, "execute_batch"):
                batch_results = KERNEL.execute_batch(request.equation, request.batch_params)
                results = [numpy_to_json(r) for r in batch_results]
                successful = len(results)
            else:
                # Fallback to sequential
                for params in request.batch_params:
                    try:
                        result = KERNEL.execute(request.equation, params)
                        results.append(numpy_to_json(result.value))
                        successful += 1
                    except Exception as e:
                        results.append({"error": str(e)})
                        failed += 1
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        return BatchResponse(
            equation=request.equation, results=results, successful=successful, failed=failed
        )

    @app.get("/api/v1/patterns")
    async def list_patterns() -> List[dict[str, Any]]:
        """List all mathematical patterns and their equations."""

        from amos_equation_kernel import MathematicalPattern

        patterns = []
        for pattern in MathematicalPattern:
            equations = KERNEL.get_by_pattern(pattern)
            patterns.append(
                {
                    "pattern": pattern.value,
                    "description": pattern.name.replace("_", " ").title(),
                    "equation_count": len(equations),
                    "equations": [eq.name for eq in equations],
                }
            )

        return patterns

    @app.get("/api/v1/isomorphisms")
    async def get_isomorphisms() -> List[IsomorphismInfo]:
        """Get cross-domain equation isomorphisms."""
        isos = KERNEL.find_isomorphisms()
        return [
            IsomorphismInfo(
                equation1=iso["equation1"],
                equation2=iso["equation2"],
                similarity=iso["similarity"],
                description=iso["description"],
            )
            for iso in isos
        ]

    @app.get("/explorer", response_class=HTMLResponse)
    async def web_explorer() -> str:
        """Serve interactive web explorer."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AMOS Equation Explorer</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }
                .stat-card {
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #3498db;
                }
                .stat-label {
                    color: #7f8c8d;
                    font-size: 0.9em;
                }
                .equation-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                .equation-card {
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                .equation-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }
                .equation-name {
                    font-weight: bold;
                    color: #2c3e50;
                    font-size: 1.1em;
                }
                .equation-domain {
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                .equation-formula {
                    background: #ecf0f1;
                    padding: 10px;
                    border-radius: 4px;
                    margin-top: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                    overflow-x: auto;
                }
                .search-box {
                    width: 100%;
                    padding: 12px;
                    font-size: 16px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
                .filter-tags {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                .filter-tag {
                    padding: 5px 15px;
                    background: #3498db;
                    color: white;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 0.9em;
                }
                .filter-tag:hover {
                    background: #2980b9;
                }
                .try-it {
                    margin-top: 15px;
                    padding: 10px;
                    background: #2ecc71;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    width: 100%;
                }
                .try-it:hover {
                    background: #27ae60;
                }
                #modal {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 1000;
                }
                #modal-content {
                    background: white;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 30px;
                    border-radius: 8px;
                    max-height: 80vh;
                    overflow-y: auto;
                }
                .param-input {
                    margin: 10px 0;
                }
                .param-input label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                .param-input input {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .result-box {
                    background: #ecf0f1;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 15px;
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <h1>🔬 AMOS Equation Explorer</h1>
            <p>Interactive mathematical equation library with 32+ executable equations</p>

            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-eqs">-</div>
                    <div class="stat-label">Equations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="domains">-</div>
                    <div class="stat-label">Domains</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="patterns">-</div>
                    <div class="stat-label">Patterns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="jax">-</div>
                    <div class="stat-label">JAX Accel</div>
                </div>
            </div>

            <input type="text" class="search-box" id="search"
                   placeholder="🔍 Search equations...">

            <div class="filter-tags" id="filters">
                <span class="filter-tag" onclick="filterBy('all')">All</span>
            </div>

            <div class="equation-grid" id="equations"></div>

            <div id="modal">
                <div id="modal-content">
                    <h2 id="modal-title">Equation</h2>
                    <p id="modal-desc"></p>
                    <div id="modal-params"></div>
                    <button class="try-it" onclick="executeEquation()">Execute</button>
                    <div class="result-box" id="result" style="display:none;"></div>
                    <button onclick="closeModal()"
                            style="margin-top:10px; padding:10px; width:100%;">
                        Close
                    </button>
                </div>
            </div>

            <script>
                let allEquations = [];
                let currentEquation = null;

                async function loadStats() {
                    try {
                        const response = await fetch('/api/v1/stats');
                        const stats = await response.json();
                        document.getElementById('total-eqs').textContent = stats.total_equations;
                        document.getElementById('domains').textContent = stats.domains_covered;
                        document.getElementById('patterns').textContent = stats.patterns_identified;
                        document.getElementById('jax').textContent = stats.jax_accelerated ? '✓' : '✗';
                    } catch (e) {
                        console.error('Failed to load stats:', e);
                    }
                }

                async function loadEquations() {
                    try {
                        const response = await fetch('/api/v1/equations');
                        allEquations = await response.json();
                        renderEquations(allEquations);
                    } catch (e) {
                        console.error('Failed to load equations:', e);
                    }
                }

                function renderEquations(equations) {
                    const container = document.getElementById('equations');
                    container.innerHTML = equations.map(eq => `
                        <div class="equation-card" onclick="openModal('${eq.name}')">
                            <div class="equation-name">${eq.name}</div>
                            <div class="equation-domain">${eq.domain} • ${eq.pattern}</div>
                            <div class="equation-formula">${eq.formula}</div>
                            <button class="try-it">Try it</button>
                        </div>
                    `).join('');
                }

                function openModal(name) {
                    currentEquation = allEquations.find(e => e.name === name);
                    if (!currentEquation) return;

                    document.getElementById('modal-title').textContent = currentEquation.name;
                    document.getElementById('modal-desc').textContent = currentEquation.description;

                    const paramsDiv = document.getElementById('modal-params');
                    paramsDiv.innerHTML = Object.entries(currentEquation.parameters)
                        .map(([key, desc]) => `
                            <div class="param-input">
                                <label>${key} (${desc})</label>
                                <input type="text" id="param-${key}"
                                       placeholder="e.g., [1.0, 2.0, 3.0] or 1.5">
                            </div>
                        `).join('');

                    document.getElementById('result').style.display = 'none';
                    document.getElementById('modal').style.display = 'block';
                }

                function closeModal() {
                    document.getElementById('modal').style.display = 'none';
                    currentEquation = null;
                }

                async function executeEquation() {
                    if (!currentEquation) return;

                    const params = {};
                    Object.keys(currentEquation.parameters).forEach(key => {
                        const val = document.getElementById(`param-${key}`).value;
                        try {
                            params[key] = JSON.parse(val);
                        } catch {
                            params[key] = parseFloat(val) || val;
                        }
                    });

                    try {
                        const response = await fetch(`/api/v1/equations/${currentEquation.name}/execute`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({parameters: params})
                        });

                        const result = await response.json();
                        const resultBox = document.getElementById('result');
                        resultBox.style.display = 'block';
                        resultBox.innerHTML = `
                            <strong>Result:</strong> ${JSON.stringify(result.value, null, 2)}<br>
                            <strong>Invariants Valid:</strong> ${result.invariants_valid ? '✓' : '✗'}<br>
                            ${result.execution_time_ms ? `<strong>Time:</strong> ${result.execution_time_ms} ms<br>` : ''}
                            ${result.jax_accelerated ? '<strong>JAX Accelerated:</strong> ✓' : ''}
                            ${result.errors.length ? `<strong>Errors:</strong> ${result.errors.join(', ')}` : ''}
                        `;
                    } catch (e) {
                        alert('Execution failed: ' + e.message);
                    }
                }

                function filterBy(type) {
                    if (type === 'all') {
                        renderEquations(allEquations);
                    } else {
                        const filtered = allEquations.filter(e => e.domain === type);
                        renderEquations(filtered);
                    }
                }

                document.getElementById('search').addEventListener('input', (e) => {
                    const term = e.target.value.toLowerCase();
                    const filtered = allEquations.filter(eq =>
                        eq.name.toLowerCase().includes(term) ||
                        eq.description.toLowerCase().includes(term) ||
                        eq.domain.toLowerCase().includes(term)
                    );
                    renderEquations(filtered);
                });

                // Load data
                loadStats();
                loadEquations();
            </script>
        </body>
        </html>
        """
        return html_content


# Run server if executed directly
if __name__ == "__main__" and FASTAPI_AVAILABLE:
    import uvicorn

    print("Starting AMOS Equation API Server...")
    print(f"JAX Acceleration: {JAX_MODE}")
    print("API Documentation: http://localhost:8000/docs")
    print("Web Explorer: http://localhost:8000/explorer")
    uvicorn.run(app, host="0.0.0.0", port=8000)
elif not FASTAPI_AVAILABLE:
    print("FastAPI not available. Install with: pip install fastapi uvicorn pydantic")
    print("Then run: python amos_equation_api.py")
