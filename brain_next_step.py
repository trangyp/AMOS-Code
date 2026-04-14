#!/usr/bin/env python3
"""AMOS Brain: Next Step Analysis - Post-CI/CD Build"""

import json
from pathlib import Path

from amos_brain import decide, think


def check_current_state():
    """Check what has already been built."""
    # Use file-relative path for portability
    repo = Path(__file__).resolve().parent

    built_files = {
        "ci_cd_workflow": (repo / ".github" / "workflows" / "deploy.yml").exists(),
        "api_server": (repo / "amos_api_server.py").exists(),
        "requirements_deploy": (repo / "requirements-deploy.txt").exists(),
        "dockerfile_updated": "amos_api_server.py" in (repo / "Dockerfile").read_text()
        if (repo / "Dockerfile").exists()
        else False,
    }

    return built_files


def analyze_next_needs(built_files):
    """Use brain to decide what to build next."""
    print("=" * 70)
    print("AMOS BRAIN: State-Aware Next Step Analysis")
    print("=" * 70)

    print("\n📊 Current Build State:")
    for item, status in built_files.items():
        icon = "✅" if status else "⏳"
        print(f"   {icon} {item}")

    # All CI/CD files built - what's next?
    context = """
    Context: CI/CD workflow, API server, and Dockerfile have been created.
    Domain neurosyncai.tech uses Hostinger hosting via connect.hostinger.com.
    Need to determine next logical step for actual deployment and operation.
    """

    print(f"\n📋 {context.strip()}")

    # Use brain to think about next steps
    response = think(
        "What should be built next after CI/CD workflow and API server are ready? "
        "The domain is neurosyncai.tech on Hostinger. "
        "Need to complete the deployment pipeline and ensure the service runs.",
        domain="software",
    )

    print("\n🧠 Brain Analysis:")
    print(f"   Confidence: {response.confidence}")
    print(f"   Law Compliant: {response.law_compliant}")

    return response


def decide_next_step():
    """Decide the specific next action."""
    print("\n" + "=" * 70)
    print("AMOS BRAIN: Decision - Next Build Target")
    print("=" * 70)

    decision = decide(
        "What is the next specific thing to build after CI/CD is set up? "
        "Files created: deploy.yml, amos_api_server.py, requirements-deploy.txt. "
        "Next priority: make deployment actually work on Hostinger.",
        options=[
            "Create docker-compose.yml for production deployment",
            "Build Hostinger deployment script with API integration",
            "Create environment configuration (.env.example, config loader)",
            "Add nginx reverse proxy configuration",
            "Build monitoring/health dashboard endpoint",
        ],
    )

    print(f"\n✅ Decision Approved: {decision.approved}")
    print(f"🎯 Decision ID: {decision.decision_id}")
    print(f"⚠️ Risk Level: {decision.risk_level}")
    print("\n📝 Reasoning:")
    print(f"   {decision.reasoning[:300]}...")

    return decision


def determine_next_build():
    """Determine exactly what files to create next."""
    print("\n" + "=" * 70)
    print("AMOS BRAIN: Next Build Target")
    print("=" * 70)

    # Based on analysis - docker-compose is most logical next step
    next_build = {
        "action": "CREATE_DOCKER_COMPOSE",
        "priority": "high",
        "files": ["docker-compose.yml", ".env.example", "deploy-to-hostinger.sh"],
        "rationale": "Docker Compose orchestrates API server + any future services (db, cache). Environment config separates secrets from code. Deployment script automates Hostinger push.",
        "validation": "After this, only need to configure Hostinger webhook or run deploy script",
    }

    print("\n🎯 NEXT BUILD TARGET:")
    print(f"   Action: {next_build['action']}")
    print(f"   Priority: {next_build['priority']}")

    print("\n📁 Files to Create:")
    for f in next_build["files"]:
        print(f"   • {f}")

    print(f"\n💭 Rationale: {next_build['rationale']}")
    print(f"\n✓ Validation: {next_build['validation']}")

    return next_build


def main():
    print("\n" + "=" * 70)
    print("AMOS BRAIN: State-Aware Build Orchestrator")
    print("=" * 70)

    # Check what exists
    state = check_current_state()

    # Analyze needs
    analysis = analyze_next_needs(state)

    # Make decision
    decision = decide_next_step()

    # Determine build target
    build = determine_next_build()

    # Summary
    print("\n" + "=" * 70)
    print("📦 BUILD PLAN")
    print("=" * 70)

    output = {
        "current_state": state,
        "next_build": build["action"],
        "files_to_create": build["files"],
        "rationale": build["rationale"],
    }

    print(json.dumps(output, indent=2))

    return build


if __name__ == "__main__":
    build_plan = main()
    print("\n" + "=" * 70)
    print("✨ Analysis complete. Ready to build next phase.")
    print("=" * 70)
