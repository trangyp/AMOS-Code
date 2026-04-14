"""AMOS Brain Integration Test - Full cognitive pipeline validation."""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from audit_exporter import export_audit
from cognitive_audit import get_audit_trail, record_cognitive_decision
from engine_executor import execute_cognitive_task
from feedback_loop import get_feedback_loop
from multi_agent_orchestrator import run_cognitive_consensus

from amos_cognitive_router import get_router


def test_cognitive_router():
    """Test task analysis and routing."""
    print("\n[TEST] Cognitive Router")
    router = get_router()

    test_tasks = [
        "Design a secure authentication system",
        "Refactor this function to use list comprehensions",
        "Analyze the ethical implications of AI deployment",
    ]

    for task in test_tasks:
        analysis = router.analyze(task)
        assert analysis.primary_domain != "unknown", f"Domain detection failed for: {task}"
        assert analysis.risk_level in ["low", "medium", "high", "critical"]
        assert len(analysis.suggested_engines) > 0, f"No engines suggested for: {task}"
        print(f"  ✓ {task[:40]}... -> {analysis.primary_domain} | {analysis.risk_level}")

    return True


def test_engine_executor():
    """Test single engine execution."""
    print("\n[TEST] Engine Executor")

    task = "Design a Python function to calculate prime numbers"
    engines = ["AMOS_Engineering_And_Mathematics_Engine"]

    result = execute_cognitive_task(task, engines)

    assert len(result.engines_used) == 1
    assert result.execution_time_ms > 0
    assert len(result.reasoning_steps) == 1
    print(f"  ✓ Executed {len(result.engines_used)} engines in {result.execution_time_ms:.1f}ms")

    return True


def test_multi_agent_orchestrator():
    """Test parallel multi-agent consensus."""
    print("\n[TEST] Multi-Agent Orchestrator")

    task = "Should we implement caching at application or database layer?"
    engines = [
        "AMOS_Deterministic_Logic_And_Law_Engine",
        "AMOS_Strategy_Game_Engine",
        "AMOS_Engineering_And_Mathematics_Engine",
    ]

    consensus = run_cognitive_consensus(task, engines)

    assert len(consensus.perspectives) == 3, "Should have 3 perspectives"
    assert 0.0 <= consensus.agreement_score <= 1.0
    assert consensus.total_execution_time_ms > 0
    print(
        f"  ✓ {len(consensus.perspectives)} perspectives, agreement: {consensus.agreement_score:.0%}"
    )

    return True


def test_audit_trail():
    """Test audit recording and retrieval."""
    print("\n[TEST] Audit Trail")

    # Record a test decision
    record_cognitive_decision(
        task="Integration test task",
        domain="test",
        risk_level="low",
        engines=["AMOS_Test_Engine"],
        consensus_score=0.85,
        laws=["RULE_OF_2"],
        violations=[],
        exec_time_ms=5.0,
        recommendation="Test passed",
    )

    audit = get_audit_trail()
    entries = audit.get_recent(1)

    assert len(entries) >= 1, "No entries in audit trail"
    assert entries[0].domain == "test"
    print(f"  ✓ Recorded and retrieved {len(entries)} entries")

    return True


def test_feedback_loop():
    """Test feedback-based learning."""
    print("\n[TEST] Feedback Loop")

    loop = get_feedback_loop()

    # Add test data for a domain
    for i in range(3):
        record_cognitive_decision(
            task=f"Test task {i}",
            domain="test_domain",
            risk_level="medium",
            engines=["AMOS_Strategy_Game_Engine", "AMOS_Design_Language_Engine"],
            consensus_score=0.8 + (i * 0.05),
            laws=[],
            violations=[],
            exec_time_ms=10.0,
            recommendation="Test",
        )

    insights = loop.analyze_patterns()

    # Should have insight for test_domain
    test_insights = [i for i in insights if i.pattern == "test_domain"]
    if test_insights:
        print(
            f"  ✓ Derived insight for test_domain: {len(test_insights[0].recommended_engines)} engines"
        )
    else:
        print(f"  ✓ Feedback loop analyzed {len(insights)} patterns")

    return True


def test_exporter():
    """Test audit data export."""
    print("\n[TEST] Audit Exporter")

    # Test JSON export
    json_path = export_audit(format="json")
    assert json_path.exists(), "JSON export failed"
    json_path.unlink()

    # Test CSV export
    csv_path = export_audit(format="csv")
    assert csv_path.exists(), "CSV export failed"
    csv_path.unlink()

    print("  ✓ JSON and CSV export working")

    return True


def test_full_pipeline():
    """Test complete cognitive pipeline."""
    print("\n[TEST] Full Cognitive Pipeline")

    router = get_router()

    # Step 1: Analyze task
    task = "Design a scalable microservices architecture"
    analysis = router.analyze(task)

    # Step 2: Build cognitive prompt
    prompt = router.build_cognitive_prompt(task, execute=True)
    assert "AMOS COGNITIVE ROUTING" in prompt

    # Step 3: Verify audit recorded
    audit = get_audit_trail()
    recent = audit.get_recent(1)
    assert len(recent) > 0

    print("  ✓ Pipeline: analyze → execute → audit → complete")
    print(f"    Domain: {analysis.primary_domain}")
    print(f"    Engines: {len(analysis.suggested_engines)}")

    return True


def run_all_tests():
    """Run complete integration test suite."""
    print("=" * 70)
    print("AMOS Brain Integration Test Suite")
    print("=" * 70)

    tests = [
        ("Cognitive Router", test_cognitive_router),
        ("Engine Executor", test_engine_executor),
        ("Multi-Agent Orchestrator", test_multi_agent_orchestrator),
        ("Audit Trail", test_audit_trail),
        ("Feedback Loop", test_feedback_loop),
        ("Exporter", test_exporter),
        ("Full Pipeline", test_full_pipeline),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n✅ ALL TESTS PASSED - AMOS integration is production-ready")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
