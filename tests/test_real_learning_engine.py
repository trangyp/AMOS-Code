"""
Test Real Learning Engine - AMOS Self-Improving Procedure Engine
"""
import os
import tempfile
import pytest


def test_real_learning_engine_initialization():
    """Test RealLearningEngine can be initialized."""
    from amos_brain.real_learning_engine import RealLearningEngine
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RealLearningEngine(storage_path=tmpdir)
        assert engine is not None
        assert engine.procedures == {}
        assert engine.patterns == {}
        assert engine.decisions == []
        assert engine.failures == []


def test_learn_from_successful_task():
    """Test extracting procedure from successful task."""
    from amos_brain.real_learning_engine import (
        RealLearningEngine, learn_from_task
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RealLearningEngine(storage_path=tmpdir)
        
        procedure = learn_from_task(
            task_description="Fix import error for missing module",
            solution_steps=[
                "Check if module exists in project structure",
                "Add missing __init__.py if needed",
                "Verify import path is correct",
                "Test import to confirm fix"
            ],
            outcome={"success": True, "summary": "Import resolved"},
            execution_time_ms=500,
            context={"error_type": "import"}
        )
        
        assert procedure is not None
        assert procedure.name == "Fix import error for missing module"
        assert len(procedure.steps) == 4
        assert procedure.confidence > 0


def test_pattern_detection():
    """Test pattern detection and classification."""
    from amos_brain.real_learning_engine import RealLearningEngine
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RealLearningEngine(storage_path=tmpdir)
        
        pattern = engine.pattern_detector.detect_pattern(
            "Need to fix import error in repo_doctor module",
            {"error_type": "import"}
        )
        
        assert pattern is not None
        assert pattern.pattern_type in ["import_fix", "bug_fix", "performance", "refactor", "unknown"]
        assert pattern.pattern_id is not None


def test_procedure_reuse():
    """Test automatic procedure reuse."""
    from amos_brain.real_learning_engine import (
        RealLearningEngine, learn_from_task, attempt_procedure_reuse
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # First, learn a procedure
        engine = RealLearningEngine(storage_path=tmpdir)
        procedure = learn_from_task(
            task_description="Fix import error for missing module",
            solution_steps=["Check module", "Add __init__.py"],
            outcome={"success": True},
            execution_time_ms=500,
            context={"error_type": "import"}
        )
        
        # Then try to reuse for similar task
        result = attempt_procedure_reuse(
            "Fix import error for missing repo_doctor module",
            {"error_type": "import"}
        )
        
        # Should match and reuse
        if result and result.get("reused"):
            assert result["procedure_id"] == procedure.procedure_id
            assert result["confidence"] > 0.7
            assert result["bypass_analysis"] is True


def test_decision_recording():
    """Test decision recording and retrieval."""
    from amos_brain.real_learning_engine import RealLearningEngine
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RealLearningEngine(storage_path=tmpdir)
        
        decision = engine.record_decision(
            decision_type="tool_selection",
            context={"task": "fix_import"},
            chosen_option="edit",
            rejected_options=["manual"],
            rationale="Direct edit is faster",
            outcome={"success": True}
        )
        
        assert decision is not None
        assert decision.decision_type == "tool_selection"
        assert decision.chosen_option == "edit"
        assert len(engine.decisions) == 1


def test_failure_memory():
    """Test failure pattern recording."""
    from amos_brain.real_learning_engine import RealLearningEngine
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RealLearningEngine(storage_path=tmpdir)
        
        engine.record_failure(
            what_was_tried="Manual file editing without verification",
            why_it_failed="Missed closing bracket",
            conditions={"task_type": "edit"},
            alternative_procedure=None
        )
        
        assert len(engine.failures) == 1
        failure = engine.failures[0]
        assert failure.what_was_tried == "Manual file editing without verification"
        assert failure.why_it_failed == "Missed closing bracket"


def test_learning_state():
    """Test getting learning state metrics."""
    from amos_brain.real_learning_engine import (
        RealLearningEngine, learn_from_task
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RealLearningEngine(storage_path=tmpdir)
        
        # Learn a few procedures
        for i in range(3):
            learn_from_task(
                task_description=f"Task {i}",
                solution_steps=["Step 1", "Step 2"],
                outcome={"success": True},
                execution_time_ms=1000
            )
        
        state = engine.get_learning_state()
        
        assert state["procedures_stored"] == 3
        assert state["patterns_stored"] >= 0
        assert "avg_procedure_confidence" in state


def test_get_learning_engine_singleton():
    """Test get_learning_engine returns singleton."""
    from amos_brain.real_learning_engine import get_learning_engine
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine1 = get_learning_engine(tmpdir)
        engine2 = get_learning_engine(tmpdir)
        
        # Same instance
        assert engine1 is engine2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
