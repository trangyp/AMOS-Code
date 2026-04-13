#!/usr/bin/env python3
"""AMOS Brain: Next Iteration Analysis - What to build now?"""

from pathlib import Path
from amos_brain import think, decide


def check_complete_stack():
    """Check everything that's been built."""
    # Use file-relative path for portability
    repo = Path(__file__).resolve().parent

    components = {
        # Infrastructure
        "CI/CD Workflow": (repo / ".github" / "workflows" / "deploy.yml").exists(),
        "API Server": (repo / "amos_api_server.py").exists(),
        "Dockerfile": (repo / "Dockerfile").exists(),
        "Docker Compose": (repo / "docker-compose.yml").exists(),
        "Env Template": (repo / ".env.example").exists(),
        "Deploy Script": (repo / "deploy-to-hostinger.sh").exists(),
        # Verification
        "Test Dashboard": (repo / "test-api.html").exists(),
        "Verify Script": (repo / "verify-deployment.py").exists(),
    }

    return components


def main():
    print("=" * 70)
    print("AMOS BRAIN: Iteration 4 - Post-Infrastructure Analysis")
    print("=" * 70)

    stack = check_complete_stack()
    complete = sum(1 for v in stack.values() if v)
    total = len(stack)

    print(f"\n📊 Current State: {complete}/{total} components complete")
    for name, exists in stack.items():
        print(f"   {'✅' if exists else '❌'} {name}")

    # What is missing or could be improved?
    context = f"""
    Infrastructure is {complete}/{total} complete.
    All core deployment files exist.
    Domain neurosyncai.tech is configured.
    Next: What adds most value? Options:
    1. Documentation/README for API usage
    2. More API endpoints (orchestrate, batch processing)
    3. Authentication/security layer
    4. Monitoring/alerting system
    5. Client SDK for consuming the API
    6. Demo/tutorial scripts
    """

    print(f"\n{context.strip()}")

    # Brain decision
    print("\n" + "=" * 70)
    print("AMOS BRAIN: Decision")
    print("=" * 70)

    decision = decide(
        "What to build after deployment infrastructure is complete? "
        f"Current: {complete}/{total} components ready. "
        "Goal: Make the API usable and valuable immediately upon deployment.",
        options=[
            "API Documentation with examples",
            "Python client SDK for easy API consumption",
            "Demo/tutorial scripts showing use cases",
            "Authentication system (API keys)",
            "Batch processing endpoint for multiple queries",
            "WebSocket real-time endpoint"
        ]
    )

    print(f"\n✅ Decision: {decision.approved}")
    print(f"🎯 ID: {decision.decision_id}")
    print(f"⚠️ Risk: {decision.risk_level}")
    print(f"\n📝 Reasoning:\n{decision.reasoning[:400]}...")

    # Determine exact next build
    print("\n" + "=" * 70)
    print("🎯 NEXT BUILD TARGET")
    print("=" * 70)

    next_build = {
        "action": "CREATE_API_DOCUMENTATION",
        "files": [
            "API_README.md",
            "examples/python_client.py",
            "examples/curl_examples.sh"
        ],
        "rationale": "Documentation enables immediate API adoption. Examples show practical usage. No value in deployed API if no one knows how to use it."
    }

    print(f"\nAction: {next_build['action']}")
    print(f"\nFiles:")
    for f in next_build['files']:
        print(f"   • {f}")
    print(f"\nRationale: {next_build['rationale']}")

    return next_build


if __name__ == "__main__":
    build = main()
    print("\n" + "=" * 70)
    print("✨ Analysis complete.")
    print("=" * 70)
