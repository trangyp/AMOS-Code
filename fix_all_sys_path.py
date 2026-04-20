#!/usr/bin/env python3
"""Fix all sys.path.insert and sys.path.append in Python files."""

import re
from pathlib import Path

# List of files to fix (from previous batch script and additional ones)
FILES_TO_FIX = [
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


def fix_file(filepath: Path) -> tuple[bool, int]:
    """Remove sys.path.insert/sys.path.append from a file."""
    try:
        content = filepath.read_text()
        original = content
        count = 0

        # Pattern 1: Setup paths blocks with for loops
        pattern1 = re.compile(
            r"^# Setup paths\s*\n"
            r"AMOS_ROOT = [^\n]+\n"
            r"(?:for [^:]+:\s*\n"
            r"\s+if [^:]+:\s*\n"
            r"\s+sys\.path\.insert\([^)]+\)\s*\n)+",
            re.MULTILINE,
        )
        if pattern1.search(content):
            content = pattern1.sub("\n", content)
            count += 1

        # Pattern 2: Brain integration path setup
        pattern2 = re.compile(
            r"^# Brain integration\s*\n"
            r"AMOS_ROOT = [^\n]+\n"
            r"[^\n]*sys\.path\.insert\([^)]+\)\s*\n",
            re.MULTILINE,
        )
        if pattern2.search(content):
            content = pattern2.sub("\n", content)
            count += 1

        # Pattern 3: Add paths to sys.path
        pattern3 = re.compile(
            r"^(?:# Add [^\n]+ to path\s*\n)?"
            r"[^\n]*sys\.path\.insert\(0,[^\n]+\)\s*\n",
            re.MULTILINE,
        )
        matches = pattern3.findall(content)
        if matches:
            content = pattern3.sub("\n", content)
            count += len(matches)

        # Pattern 4: Any remaining sys.path.insert
        pattern4 = re.compile(r"^[^\n]*sys\.path\.insert\([^)]+\)[^\n]*\n", re.MULTILINE)
        matches = pattern4.findall(content)
        if matches:
            content = pattern4.sub("\n", content)
            count += len(matches)

        # Pattern 5: Any remaining sys.path.append
        pattern5 = re.compile(r"^[^\n]*sys\.path\.append\([^)]+\)[^\n]*\n", re.MULTILINE)
        matches = pattern5.findall(content)
        if matches:
            content = pattern5.sub("\n", content)
            count += len(matches)

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        if content != original and count > 0:
            filepath.write_text(content)
            return True, count
        return False, 0

    except Exception as e:
        print(f"  Error: {e}")
        return False, 0


def main():
    root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    total_fixed = 0
    total_files = 0

    for rel_path in FILES_TO_FIX:
        filepath = root / rel_path
        if filepath.exists():
            fixed, count = fix_file(filepath)
            if fixed:
                print(f"✅ Fixed {count} patterns: {rel_path}")
                total_fixed += count
                total_files += 1
        else:
            print(f"⚠️ Not found: {rel_path}")

    print(f"\n✅ Fixed {total_fixed} patterns in {total_files} files")


if __name__ == "__main__":
    main()
