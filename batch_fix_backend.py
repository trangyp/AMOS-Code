#!/usr/bin/env python3
"""Batch fix sys.path hacks in backend files."""

import re
from pathlib import Path

# List of backend files with sys.path hacks
BACKEND_FILES = [
    "backend/api/axiom_one_slots.py",
    "backend/api/brain_v2.py",
    "backend/api/cognitive_websocket.py",
    "backend/api/enhanced_task_processor.py",
    "backend/cognitive_monitor.py",
    "backend/api/agent_monitor.py",
    "backend/api/axiom_one.py",
    "backend/api/brain_analytics_engine.py",
    "backend/api/brain_auto_heal.py",
    "backend/api/brain_code_intelligence.py",
    "backend/api/brain_cognitive_analysis.py",
    "backend/api/brain_cognitive_query.py",
    "backend/api/brain_dashboard_api.py",
    "backend/api/brain_decision_support.py",
    "backend/api/brain_knowledge_graph.py",
    "backend/api/brain_memory_api.py",
    "backend/api/brain_pattern_recognition.py",
    "backend/api/brain_powered_endpoints.py",
    "backend/api/brain_prediction_engine.py",
    "backend/api/brain_realtime_monitor.py",
    "backend/api/brain_streaming.py",
    "backend/api/brain_task_automation.py",
    "backend/api/brain_task_execution.py",
    "backend/api/brain_unified_api.py",
    "backend/api/brain_websocket.py",
    "backend/api/brain_workflow_orchestrator.py",
    "backend/api/fastloop.py",
    "backend/api/file_ingestion.py",
    "backend/api/llm_streaming.py",
    "backend/api/rag_engine.py",
    "backend/api/siks.py",
    "backend/api/simulation_dashboard.py",
    "backend/api/unified_orchestrator.py",
    "backend/api/vector_search.py",
    "backend/auth_integration.py",
    "backend/brain_integration.py",
    "backend/llm_providers.py",
    "backend/llm_providers_complete.py",
    "backend/main_amos_integrated.py",
    "backend/real_orchestrator_bridge.py",
]


def fix_file(filepath: Path) -> bool:
    """Remove sys.path.insert hacks from a file."""
    try:
        content = filepath.read_text()
        original = content

        # Pattern 1: Remove common path setup blocks
        patterns = [
            # Setup paths block with AMOS_ROOT
            r"\n?# Setup paths\s*\nAMOS_ROOT = [^\n]+\n(?:for [^:]+:\s*\n\s+if [^:]+:\s*\n\s+sys\.path\.insert\([^)]+\)\s*\n)+",
            # Simple sys.path.insert lines
            r"\n?sys\.path\.insert\(0,[^\n]+\)\s*\n",
            r"\n?sys\.path\.insert\(0, str\(AMOS_ROOT[^)]+\)\)\s*\n",
            # Path setup with for loop
            r"\n?# Add amos_brain to path\s*\n[^\n]+\nfor [^:]+:\s*\n\s+sys\.path\.insert\([^)]+\)\s*\n",
            # Brain integration path setup
            r"\n?# Brain integration\s*\nAMOS_ROOT = [^\n]+\n[^\n]*sys\.path\.insert\([^)]+\)\s*\n",
        ]

        for pattern in patterns:
            content = re.sub(pattern, "\n", content)

        # Remove any remaining sys.path.append or sys.path.insert
        content = re.sub(r"\n?sys\.path\.(?:insert|append)\([^)]+\)\s*\n", "\n", content)

        if content != original:
            filepath.write_text(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"⚠️ No changes: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error in {filepath}: {e}")
        return False


def main():
    root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    fixed = 0
    for rel_path in BACKEND_FILES:
        filepath = root / rel_path
        if filepath.exists():
            if fix_file(filepath):
                fixed += 1
        else:
            print(f"⚠️ Not found: {filepath}")

    print(f"\n✅ Fixed {fixed} files")


if __name__ == "__main__":
    main()
