"""AMOS Local Runtime - Local LLM as execution engine with AMOS governance.

This module implements the reversed architecture where:
- AMOS serves as policy/orchestration layer (pre/post-processing)
- Local LLM (Ollama/LM Studio/vLLM) serves as the execution boundary
- Health checks verify actual model reachability
"""
from __future__ import annotations

import sys
from typing import Any

from .config_validator import validate_config
from .integration import AMOSBrainIntegration, get_amos_integration
from .metrics import get_metrics
from .model_backend import ModelBackend, build_backend_from_env


class AMOSLocalRuntime:
    """Runtime that puts AMOS brain in front of local LLM backends.

    Flow: input -> AMOS preprocess -> local LLM call -> optional post-check

    This reverses the traditional architecture where the agent runtime is
    primary and AMOS is attached around it. Here, the local LLM is the engine
    and AMOS provides reasoning, governance, and policy enforcement.
    """

    def __init__(
        self,
        amos_integration: AMOSBrainIntegration | None = None,
        backend: ModelBackend | None = None,
    ):
        self.amos = amos_integration or get_amos_integration()
        self.backend = backend or build_backend_from_env()
        self._ready: bool = False
        self._status: dict[str, Any] = {}

    def initialize(self) -> dict[str, Any]:
        """Initialize the runtime with full health verification.

        Unlike weak readiness checks, this verifies:
        1. AMOS config loaded
        2. Reasoning engine constructed
        3. Model endpoint responds
        4. Model name validated

        Returns:
            Status dict with success/failure details
        """
        results = {
            "amos": None,
            "backend": None,
            "ready": False,
        }

        # Initialize AMOS
        try:
            amos_status = self.amos.initialize()
            results["amos"] = {
                "status": "initialized",
                "brain_loaded": amos_status.get("brain_loaded", False),
                "engines": amos_status.get("engines_available", []),
            }
        except Exception as e:
            results["amos"] = {"status": "error", "error": str(e)}
            return results

        # Health check backend (verifies model reachability)
        backend_health = self.backend.health_check()
        results["backend"] = backend_health

        if backend_health.get("status") not in {"healthy", "warning"}:
            return results

        self._ready = True
        self._status = results
        results["ready"] = True
        return results

    @property
    def is_ready(self) -> bool:
        """Check if runtime is fully initialized and ready."""
        return self._ready

    def reply(self, user_message: str, context: dict | None = None) -> dict:
        """Process user message through AMOS + local LLM pipeline.

        Args:
            user_message: The user's input message
            context: Optional context dict with conversation history, etc.

        Returns:
            Response dict with text, routing info, and status
        """
        if not self._ready:
            return {
                "ok": False,
                "error": "Runtime not initialized. Call initialize() first.",
            }

        # AMOS pre-processing: enforce laws, route to engines
        pre = self.amos.pre_process(user_message, context)
        if pre.get("blocked"):
            return {
                "ok": False,
                "blocked": True,
                "reason": pre["reason"],
                "law": pre.get("law"),
            }

        # Build enhanced system prompt with AMOS context
        base_system = (
            "You are AMOS Brain, a deterministic cognitive operating system. "
            "You provide structured reasoning with Rule of 2 and Rule of 4. "
            "You acknowledge your limits: no embodiment, no consciousness, "
            "no autonomous action."
        )
        system_prompt = self.amos.enhance_system_prompt(base_system)

        # Start metrics tracking
        metrics = get_metrics()
        req_metrics = metrics.start_request(
            backend=getattr(self.backend, "base_url", "unknown"),
            model=getattr(self.backend, "model", "unknown"),
        )

        # Call local LLM backend
        try:
            result = self.backend.generate(
                system_prompt=system_prompt,
                user_prompt=user_message,
                temperature=0.2,
                max_tokens=1200,
            )
            metrics.end_request(req_metrics, success=True)
        except Exception as e:
            metrics.end_request(req_metrics, success=False, error_type=type(e).__name__)
            return {
                "ok": False,
                "error": f"Model generation failed: {e}",
            }

        # Optional: AMOS post-processing validation
        post = self.amos.post_process(result.text, user_message)

        return {
            "ok": True,
            "text": result.text,
            "routing": pre.get("routing"),
            "validation": post if post.get("structural_issues") else None,
            "raw": result.raw,
        }

    def reply_stream(self, user_message: str, context: dict | None = None):
        """Stream response from AMOS + local LLM pipeline.

        Args:
            user_message: The user's input message
            context: Optional context dict with conversation history

        Yields:
            Dict with 'type' (status/error/chunk/done) and content
        """
        if not self._ready:
            yield {"type": "error", "error": "Runtime not initialized"}
            return

        # AMOS pre-processing: enforce laws, route to engines
        pre = self.amos.pre_process(user_message, context)
        if pre.get("blocked"):
            yield {
                "type": "blocked",
                "reason": pre["reason"],
                "law": pre.get("law"),
            }
            return

        # Build enhanced system prompt with AMOS context
        base_system = (
            "You are AMOS Brain, a deterministic cognitive operating system. "
            "You provide structured reasoning with Rule of 2 and Rule of 4. "
            "You acknowledge your limits: no embodiment, no consciousness, "
            "no autonomous action."
        )
        system_prompt = self.amos.enhance_system_prompt(base_system)

        yield {"type": "status", "routing": pre.get("routing")}

        # Start metrics tracking
        metrics = get_metrics()
        req_metrics = metrics.start_request(
            backend=getattr(self.backend, "base_url", "unknown"),
            model=getattr(self.backend, "model", "unknown"),
        )

        # Stream from local LLM backend
        try:
            full_text = ""
            for chunk in self.backend.generate_stream(
                system_prompt=system_prompt,
                user_prompt=user_message,
                temperature=0.2,
                max_tokens=1200,
            ):
                full_text += chunk
                yield {"type": "chunk", "content": chunk}

            metrics.end_request(req_metrics, success=True)
            yield {"type": "done", "full_text": full_text}

        except Exception as e:
            metrics.end_request(req_metrics, success=False, error_type=type(e).__name__)
            yield {"type": "error", "error": f"Model generation failed: {e}"}

    def chat_loop(self) -> None:
        """Run interactive chat loop with AMOS local runtime."""
        print("\n" + "=" * 60)
        print("AMOS Local Runtime - Interactive Mode")
        print("=" * 60)
        backend_status = self._status.get("backend", {})
        print(f"Backend: {backend_status.get('backend', 'unknown')}")
        print(f"Model: {backend_status.get('model', 'unknown')}")
        print("Type 'quit', 'exit', or Ctrl+C to exit")
        print("-" * 60 + "\n")

        history: list[dict] = []

        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in {"quit", "exit", "q"}:
                    print("\n[AMOS] Session ended.")
                    break
                if not user_input:
                    continue

                # Build context with history
                context = {"history": history[-10:]} if history else None

                # Stream through AMOS + local LLM
                print("\nAMOS: ", end="", flush=True)
                full_response = ""
                routing_info = None

                for event in self.reply_stream(user_input, context):
                    etype = event.get("type")

                    if etype == "status":
                        routing_info = event.get("routing")
                    elif etype == "chunk":
                        chunk = event.get("content", "")
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    elif etype == "done":
                        print("\n")
                        full_response = event.get("full_text", full_response)
                    elif etype == "blocked":
                        print(f"\n[BLOCKED by {event.get('law')}]\n")
                        print(f"Reason: {event.get('reason')}\n")
                        break
                    elif etype == "error":
                        print(f"\n[ERROR: {event.get('error')}]\n")
                        break

                # Add to history if we got a response
                if full_response:
                    history.append({"role": "user", "content": user_input})
                    hist = {"role": "assistant", "content": full_response}
                    history.append(hist)

                    # Show routing info if available
                    if routing_info:
                        print(f"[Routing: {routing_info}]\n")

            except KeyboardInterrupt:
                print("\n\n[AMOS] Session terminated by user.")
                break
            except EOFError:
                break

        # Show metrics summary at session end
        print("\n" + "=" * 60)
        print("Session Metrics Summary")
        print("=" * 60)
        metrics_summary = self.get_metrics_summary()
        if metrics_summary.get("status") != "no_data":
            print(f"Total requests: {metrics_summary.get('total_requests', 0)}")
            print(f"Success rate: {metrics_summary.get('success_rate', 0):.1%}")
            print(f"Avg latency: {metrics_summary.get('avg_latency_ms', 0):.0f}ms")
            print(f"P95 latency: {metrics_summary.get('p95_latency_ms', 0):.0f}ms")
            if metrics_summary.get("failed", 0) > 0:
                print(f"Failed requests: {metrics_summary.get('failed', 0)}")
        else:
            print("No metrics data collected.")
        print("=" * 60)

    def get_status(self) -> dict[str, Any]:
        """Get current runtime status."""
        return {
            "ready": self._ready,
            "amos": self.amos.get_status() if self.amos else None,
            "backend": self.backend.health_check() if self.backend else None,
        }

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get metrics summary for operational visibility."""
        metrics = get_metrics()
        return metrics.get_summary()


def create_local_runtime(
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> AMOSLocalRuntime:
    """Factory function to create a configured AMOS local runtime.

    Args:
        provider: Backend type (ollama, lmstudio, vllm, etc.)
        model: Model name to use
        base_url: Custom base URL for the backend

    Returns:
        Configured AMOSLocalRuntime instance
    """
    import os

    # Set env vars if provided as args
    if provider:
        os.environ["AMOS_LLM_BACKEND"] = provider
    if model:
        os.environ["AMOS_MODEL"] = model
    if base_url:
        os.environ["AMOS_BASE_URL"] = base_url

    amos = get_amos_integration()
    backend = build_backend_from_env()

    return AMOSLocalRuntime(amos_integration=amos, backend=backend)


def main() -> int:
    """Main entry point for AMOS local runtime."""
    print(
        r"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   █████╗ ███╗   ███╗ ██████╗ ███████╗                            ║
║  ██╔══██╗████╗ ████║██╔═══██╗██╔════╝                            ║
║  ███████║██╔████╔██║██║   ██║███████╗                            ║
║  ██╔══██║██║╚██╔╝██║██║   ██║╚════██║                            ║
║  ██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║                            ║
║  ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝                            ║
║                                                                  ║
║   AMOS Brain + Local LLM Runtime                                 ║
║   Local models as execution engine, AMOS as governance layer     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    )

    # Validate configuration first
    validation = validate_config()
    if not validation.valid:
        print("\n[ERROR] Configuration validation failed:\n")
        for error in validation.errors:
            print(f"  - {error}")
        return 1

    # Create and initialize runtime
    runtime = create_local_runtime()

    print("[INIT] Initializing AMOS local runtime...")
    init_status = runtime.initialize()

    # Check initialization results
    if not init_status.get("ready"):
        print("\n[ERROR] Runtime initialization failed:\n")

        amos_status = init_status.get("amos", {})
        if amos_status.get("status") == "error":
            print(f"  AMOS: {amos_status.get('error')}")

        backend_status = init_status.get("backend", {})
        if backend_status.get("status") == "error":
            print(f"  Backend: {backend_status.get('error')}")
            if backend_status.get("help"):
                print(f"  Help: {backend_status['help']}")

        print("\nEnvironment variables:")
        print("  AMOS_LLM_BACKEND=ollama|lmstudio|vllm")
        print("  AMOS_MODEL=<model-name>")
        print("  AMOS_BASE_URL=<custom-url>")
        return 1

    # Show success status
    amos_info = init_status.get("amos", {})
    backend_info = init_status.get("backend", {})

    print(f"\n[OK] AMOS brain: {amos_info.get('brain_loaded', False)}")
    print(f"[OK] Backend: {backend_info.get('backend', 'unknown')}")
    print(f"[OK] Model: {backend_info.get('model', 'unknown')}")
    available_models = backend_info.get("available_models")
    if available_models:
        print(f"[OK] Available models: {len(available_models)}")

    # Start interactive loop
    runtime.chat_loop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
