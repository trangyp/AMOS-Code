#!/usr/bin/env python3
"""Fix timezone.utc imports for Python 3.9 compatibility"""

import re
from pathlib import Path


def fix_datetime_utc(filepath):
    """Fix timezone.utc imports in a file."""
    try:
        with open(filepath) as f:
            content = f.read()

        original = content

        # Replace 'from datetime import datetime, timezone' patterns
        content = re.sub(
            r"from datetime import datetime, timezone",
            "from datetime import datetime, timezone",
            content,
        )

        # Replace 'from datetime import UTC' followed by other imports
        content = re.sub(
            r"from datetime import UTC, ([^\n]+)",
            r"from datetime import \1\nfrom datetime import timezone",
            content,
        )

        # Replace standalone 'from datetime import UTC'
        content = re.sub(
            r"from datetime import UTC\s*$",
            "from datetime import timezone",
            content,
            flags=re.MULTILINE,
        )

        # Replace timezone.utc usage with timezone.utc
        content = re.sub(r"datetime\.UTC", "timezone.utc", content)
        content = re.sub(r"\bUTC\b", "timezone.utc", content)

        if content != original:
            with open(filepath, "w") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def main():
    """Main function to fix all timezone.utc issues."""
    base_path = Path(".")

    # Files known to have issues (from grep results)
    files_to_check = [
        "AXIOM_ONE_PROTOCOLS.py",
        "analytics/api.py",
        "analytics/warehouse.py",
        "amos_primary_feature_handler.py",
        "amos_coherence_omega.py",
        "amos_energy.py",
        "amos_meta.py",
        "amos_file_ingestion_runtime.py",
        "amos_production_runtime.py",
        "equation_webhooks.py",
        "amos_container_orchestrator.py",
        "amos_verified_patch_workflow.py",
        "axiom_one/execution_slot.py",
        "amos_architectural_decision_engine.py",
        "axiom_one/ledger.py",
        "axiom_one/git_service.py",
        "amos_field_dynamics.py",
        "axiom_one/twin.py",
        "amos_runtime.py",
        "axiom_one/server.py",
        "axiom_one_repo_autopsy.py",
        "amos_platform_orchestrator.py",
        "amos_api_gateway_enterprise.py",
        "amosl_ledger.py",
        "axiom_one_agent_fleet.py",
        "amos_superintelligence_core.py",
        "amos_cognitive_router.py",
        "axiom_one_websocket_command.py",
        "amos_bootstrap_orchestrator.py",
        "amos_observability_v2.py",
        "amos_brain_enhanced_ui.py",
        "amos_api.py",
        "axiom_one_standalone.py",
        "scripts/init_registries.py",
        "amos_multitenancy.py",
        "axiom_one_agent_tools.py",
        "test_production_readiness.py",
        "amos_brain_coding_tools.py",
        "amos_cli.py",
        "amos_api_interpreter.py",
        "amos_synthesis_engine.py",
        "amos_field_economy.py",
        "amos_equation_crawler.py",
        "amos_web_search_processor.py",
        "amos_orchestrator.py",
        "amos_simulation_core.py",
        "amos_organism_runner.py",
        "backend/api/agents.py",
        "backend/api/brain_cognitive_analysis.py",
        "backend/api/llm.py",
        "backend/api/system.py",
        "backend/main.py",
        "backend/real_orchestrator_bridge.py",
        "backend/database.py",
        "backend/auth.py",
        "clawspring/amos_brain/predictive_integration.py",
    ]

    fixed_files = []

    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            if fix_datetime_utc(full_path):
                print(f"Fixed: {file_path}")
                fixed_files.append(file_path)

    print(f"\nFixed {len(fixed_files)} files")


if __name__ == "__main__":
    main()
