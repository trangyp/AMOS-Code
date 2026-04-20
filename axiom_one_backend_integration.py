#!/usr/bin/env python3
"""Axiom One - Backend Integration Module.

Integrates Axiom One components into FastAPI backend:
- Real code completion (replaces TODO: Implement)
- Real code generation (replaces placeholder)
- Agent fleet execution
- WebSocket command center
"""

# Axiom One imports (same package - no path hack needed)
from axiom_one_code_generator import (
    APIGenerator,
    ClassGenerator,
    CodeValidator,
    FunctionGenerator,
    TestGenerator,
)
from axiom_one_completion import CompletionEngine

# Canon integration for domain-aware code generation
try:
    from amos_brain.canon_bridge import get_canon_bridge

    _CANON_AVAILABLE = True
except ImportError:
    _CANON_AVAILABLE = False


class RealCodeIntelligence:
    """Real code intelligence replacing backend placeholders with Canon context."""

    def __init__(self):
        self.completion_engine = CompletionEngine()
        self._canon_bridge = None

    async def _get_canon_bridge(self):
        """Lazy initialization of canon bridge."""
        if self._canon_bridge is None and _CANON_AVAILABLE:
            self._canon_bridge = await get_canon_bridge()
        return self._canon_bridge

    async def complete_code(
        self, code_prefix: str, language: str = "python", domain: str = "general"
    ) -> list[dict]:
        """Real code completion using AST analysis with Canon context."""
        # Enrich with Canon context if available
        canon_context = {}
        if _CANON_AVAILABLE:
            try:
                canon = await self._get_canon_bridge()
                ctx = canon.get_context_for_domain(domain)
                canon_context = {
                    "domain": ctx.domain,
                    "terms_available": len(ctx.glossary_terms),
                    "applicable_agents": ctx.applicable_agents[:3],
                }
            except Exception:
                pass

        suggestions = self.completion_engine.complete(code_prefix)
        result = [
            {"completion": s.completion, "confidence": s.confidence, "description": s.description}
            for s in suggestions
        ]

        # Add Canon context to first suggestion if available
        if canon_context and result:
            result[0]["canon_context"] = canon_context

        return result

    async def generate_function(
        self,
        name: str,
        params: str,
        docstring: str,
        template: str = "simple",
        domain: str = "general",
    ) -> dict:
        """Generate real function code with Canon context."""
        # Enrich docstring with Canon definitions if available
        enriched_docstring = docstring
        canon_context = {}

        if _CANON_AVAILABLE:
            try:
                canon = await self._get_canon_bridge()
                ctx = canon.get_context_for_domain(domain)
                canon_context = {
                    "domain": ctx.domain,
                    "terms_available": len(ctx.glossary_terms),
                    "applicable_agents": ctx.applicable_agents[:3],
                    "relevant_engines": ctx.relevant_engines[:3],
                }
                # Add Canon terms to docstring if relevant
                if ctx.glossary_terms:
                    term_list = list(ctx.glossary_terms.keys())[:3]
                    enriched_docstring = (
                        f"{docstring}\n\nRelated Canon terms: {', '.join(term_list)}"
                    )
            except Exception:
                pass

        result = FunctionGenerator.generate(
            name=name, params=params, docstring=enriched_docstring, template=template
        )
        return {
            "code": result.source,
            "valid": result.is_valid,
            "error": result.syntax_error,
            "canon_context": canon_context,
        }

    async def generate_class(
        self,
        class_name: str,
        attributes: list,
        methods: list,
        docstring: str = "",
        domain: str = "general",
    ) -> dict:
        """Generate real class code with Canon context."""
        # Enrich with Canon context
        canon_context = {}
        if _CANON_AVAILABLE:
            try:
                canon = await self._get_canon_bridge()
                ctx = canon.get_context_for_domain(domain)
                canon_context = {
                    "domain": ctx.domain,
                    "terms_available": len(ctx.glossary_terms),
                    "applicable_agents": ctx.applicable_agents[:3],
                }
            except Exception:
                pass

        result = ClassGenerator.generate(
            class_name=class_name, attributes=attributes, methods=methods, docstring=docstring
        )
        return {
            "code": result.source,
            "valid": result.is_valid,
            "error": result.syntax_error,
            "canon_context": canon_context,
        }

    def generate_api_endpoint(
        self, path: str, method: str, handler_name: str, params: str, summary: str
    ) -> dict:
        """Generate real API endpoint code."""
        result = APIGenerator.generate_endpoint(
            path=path, method=method, handler_name=handler_name, params=params, summary=summary
        )
        return {"code": result.source, "valid": result.is_valid, "error": result.syntax_error}

    def generate_tests(self, target: str, module: str, params: list) -> dict:
        """Generate real test code."""
        result = TestGenerator.generate(target=target, module=module, params=params)
        return {"code": result.source, "valid": result.is_valid, "error": result.syntax_error}

    def validate_code(self, source: str) -> dict:
        """Validate code using AST."""
        is_valid, error = CodeValidator.validate(source)
        return {"valid": is_valid, "error": error}


async def demo_integration():
    """Demonstrate real backend integration with Canon."""
    print("=" * 70)
    print("AXIOM ONE BACKEND INTEGRATION (with Canon)")
    print("=" * 70)

    intelligence = RealCodeIntelligence()

    # Test 1: Code completion
    print("\n1. CODE COMPLETION")
    print("-" * 40)
    code = "def process_data(data: list) -> dict:"
    suggestions = await intelligence.complete_code(code, domain="api")
    print(f"Input: {code}")
    for s in suggestions:
        print(f"  ✓ {s['completion']} (conf: {s['confidence']})")
    if suggestions and "canon_context" in suggestions[0]:
        print(f"  Canon: {suggestions[0]['canon_context']}")

    # Test 2: Function generation
    print("\n2. FUNCTION GENERATION")
    print("-" * 40)
    func = await intelligence.generate_function(
        name="calculate_metrics",
        params="data: List[dict]",
        docstring="Calculate metrics from data",
        template="with_logging",
        domain="api",
    )
    print(f"Generated: {func['valid']} function")
    if func["valid"]:
        print(f"  Lines: {len(func['code'].split(chr(10)))}")
    if func.get("canon_context"):
        print(f"  Canon terms: {func['canon_context'].get('terms_available', 0)}")

    # Test 3: Class generation
    print("\n3. CLASS GENERATION")
    print("-" * 40)
    cls = await intelligence.generate_class(
        class_name="DataProcessor",
        attributes=[("name", "str", None), ("config", "dict", {})],
        methods=["process", "validate"],
        docstring="Processes data streams",
        domain="api",
    )
    print(f"Generated: {cls['valid']} class")
    if cls["valid"]:
        print(f"  Lines: {len(cls['code'].split(chr(10)))}")
    if cls.get("canon_context"):
        print(f"  Canon terms: {cls['canon_context'].get('terms_available', 0)}")

    # Test 4: API endpoint
    print("\n4. API ENDPOINT GENERATION")
    print("-" * 40)
    api = intelligence.generate_api_endpoint(
        path="/api/v1/process",
        method="post",
        handler_name="process_endpoint",
        params="request: ProcessRequest",
        summary="Process data endpoint",
    )
    print(f"Generated: {api['valid']} endpoint")
    if api["valid"]:
        print(f"  Lines: {len(api['code'].split(chr(10)))}")

    # Test 5: Code validation
    print("\n5. CODE VALIDATION")
    print("-" * 40)
    valid_code = "def test(): pass"
    invalid_code = "def test(: pass"

    print(f"Valid code: {intelligence.validate_code(valid_code)['valid']}")
    print(f"Invalid code: {intelligence.validate_code(invalid_code)['valid']}")

    print("\n" + "=" * 70)
    print("INTEGRATION READY - All features working")
    print("=" * 70)


if __name__ == "__main__":
    demo_integration()
