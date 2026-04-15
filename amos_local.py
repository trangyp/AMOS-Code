#!/usr/bin/env python3
"""AMOS Local Launcher - Default to local LLMs with AMOS governance.

This is the primary entry point for running AMOS with local model backends.
Unlike amos.py which boots through the ClawSpring agent runtime first,
this launcher makes local LLMs the execution boundary and AMOS the
policy/orchestration layer.

Usage:
    python amos_local.py                    # Start with Ollama default
    python amos_local.py --provider ollama  # Use Ollama explicitly
    python amos_local.py --provider lmstudio --model qwen2.5-14b

Environment:
    AMOS_LLM_BACKEND=ollama|lmstudio|vllm
    AMOS_MODEL=<model-name>
    AMOS_BASE_URL=<custom-endpoint>
    AMOS_API_KEY=<api-key-for-compatible-servers>
"""

from __future__ import annotations

import argparse
import os
import sys

# Ensure amos_brain is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E402

from amos_brain.config_validator import (  # noqa: E402
    validate_config,
)
from amos_brain.local_runtime import (  # noqa: E402
    create_local_runtime,
)
from amos_brain.local_runtime import (
    main as runtime_main,
)


def print_local_banner():
    """Print AMOS Local Runtime startup banner."""
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
║   Local models as execution engine                               ║
║   AMOS as policy/governance layer                                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=("AMOS Local Runtime - Local LLMs with cognitive governance"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python amos_local.py                          # Use Ollama default
  python amos_local.py --provider lmstudio    # Use LM Studio
  python amos_local.py --model llama3.2:latest  # Specific Ollama model
  python amos_local.py --base-url http://localhost:8080/v1

For more info, see README.MD and AMOS_BRAIN_GUIDE.md
        """,
    )

    parser.add_argument(
        "--provider",
        choices=["ollama", "lmstudio", "vllm", "llamacpp", "openai-local"],
        help="Backend type (default: from AMOS_LLM_BACKEND env or ollama)",
    )

    parser.add_argument(
        "--model", help="Model name (default: from AMOS_MODEL env or qwen2.5:14b-instruct)"
    )

    parser.add_argument("--base-url", help="Custom base URL for the backend server")

    parser.add_argument(
        "--api-key", help="API key for OpenAI-compatible servers (default: 'local')"
    )

    parser.add_argument("--check", action="store_true", help="Run health check and exit")

    return parser.parse_args()


def main():
    """Main entry point for AMOS local launcher."""
    args = parse_args()

    # Set environment variables from args
    if args.provider:
        os.environ["AMOS_LLM_BACKEND"] = args.provider
    if args.model:
        os.environ["AMOS_MODEL"] = args.model
    if args.base_url:
        os.environ["AMOS_BASE_URL"] = args.base_url
    if args.api_key:
        os.environ["AMOS_API_KEY"] = args.api_key

    # Validate configuration early
    validation = validate_config()
    if not validation.valid:
        print_local_banner()
        print("\n[ERROR] Configuration validation failed:\n")
        for error in validation.errors:
            print(f"  - {error}")
        if validation.warnings:
            print("\nWarnings:")
            for warning in validation.warnings:
                print(f"  - {warning}")
        return 1

    # Just run health check if requested
    if args.check:
        print_local_banner()
        print("[CHECK] Running health check...\n")

        runtime = create_local_runtime()
        status = runtime.initialize()

        print("AMOS Status:")
        amos = status.get("amos", {})
        print(f"  Initialized: {amos.get('status', 'unknown')}")
        print(f"  Brain loaded: {amos.get('brain_loaded', False)}")

        print("\nBackend Status:")
        backend = status.get("backend", {})
        print(f"  Status: {backend.get('status', 'unknown')}")
        btype = backend.get("backend", "unknown")
        print(f"  Backend type: {btype}")
        print(f"  Model: {backend.get('model', 'unknown')}")

        if backend.get("available_models"):
            avail = backend["available_models"]
            print(f"  Available models: {len(avail)}")
            for m in backend["available_models"][:5]:
                print(f"    - {m}")
            count = len(backend["available_models"])
            if count > 5:
                remaining = count - 5
                print(f"    ... and {remaining} more")

        if backend.get("error"):
            print(f"\n  Error: {backend['error']}")
        if backend.get("help"):
            print(f"  Help: {backend['help']}")

        return 0 if status.get("ready") else 1

    # Full startup
    print_local_banner()
    return runtime_main()


if __name__ == "__main__":
    sys.exit(main())
