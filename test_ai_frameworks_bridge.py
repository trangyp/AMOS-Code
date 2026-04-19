#!/usr/bin/env python3
"""
Test suite for AMOS AI Frameworks Bridge.

Validates integration between GLOBAL_AI_FRAMEWORKS_EQUATIONS_AND_INVARIANTS.md
and the AMOS SuperBrain system.
"""

from pathlib import Path

from amos_ai_frameworks_bridge import (
    AIFrameworkCategory,
    AIFrameworkEntry,
    AIFrameworkKnowledgeGraph,
    AIFrameworkParser,
    AIFrameworkSuperBrainIntegration,
    build_ai_frameworks_knowledge_base,
    integrate_with_superbrain,
)


def test_categories():
    """Test all 37 AI framework categories exist."""
    categories = list(AIFrameworkCategory)
    assert len(categories) == 37, f"Expected 37 categories, got {len(categories)}"
    print(f"✓ All {len(categories)} AI framework categories defined")


def test_framework_entry_creation():
    """Test creating framework entries."""
    fw = AIFrameworkEntry(
        id="",
        section_number=2,
        name="Scaled Dot-Product Attention",
        category=AIFrameworkCategory.TRANSFORMERS,
        latex_formula=r"Attention(Q,K,V) = softmax(QK^T/\sqrt{d_k})V",
        description="Core attention mechanism",
        implementation_hint="Use einsum",
        invariants=["Weights sum to 1"],
        source_framework="PyTorch",
        paper_reference="Vaswani et al. 2017",
        tags=["attention", "transformer"],
    )

    assert fw.id != "", "ID should be auto-generated"
    assert fw.section_number == 2
    assert fw.category == AIFrameworkCategory.TRANSFORMERS
    print(f"✓ Framework entry created: {fw.name} (ID: {fw.id})")


def test_knowledge_graph_operations():
    """Test knowledge graph CRUD operations."""
    graph = AIFrameworkKnowledgeGraph()

    # Add frameworks
    fw1 = AIFrameworkEntry(
        id="",
        section_number=75,
        name="MAML",
        category=AIFrameworkCategory.META_LEARNING,
        latex_formula=r"\min_\theta \sum L_i",
        description="Meta-learning",
        implementation_hint="Second-order grads",
    )

    fw2 = AIFrameworkEntry(
        id="",
        section_number=76,
        name="SimCLR",
        category=AIFrameworkCategory.SELF_SUPERVISED,
        latex_formula=r"l_{i,j} = -log[exp(sim/\tau)]",
        description="Contrastive learning",
        implementation_hint="Large batches",
    )

    id1 = graph.add_framework(fw1)
    id2 = graph.add_framework(fw2)

    # Test retrieval
    assert graph.get_by_section(75) == fw1
    assert graph.get_by_section(76) == fw2

    # Test category filtering
    meta_fws = graph.get_by_category(AIFrameworkCategory.META_LEARNING)
    assert len(meta_fws) == 1
    assert meta_fws[0].name == "MAML"

    print(f"✓ Knowledge graph operations working ({len(graph.frameworks)} frameworks)")


def test_cross_references():
    """Test cross-reference traversal."""
    graph = AIFrameworkKnowledgeGraph()

    fw1 = AIFrameworkEntry(
        id="",
        section_number=75,
        name="MAML",
        category=AIFrameworkCategory.META_LEARNING,
        latex_formula=r"\min_\theta L",
        description="Meta-learning",
        implementation_hint="Hint",
    )

    fw2 = AIFrameworkEntry(
        id="",
        section_number=76,
        name="SimCLR",
        category=AIFrameworkCategory.SELF_SUPERVISED,
        latex_formula=r"l = -log",
        description="Contrastive",
        implementation_hint="Hint",
        cross_references=[fw1.id],
    )

    graph.add_framework(fw1)
    graph.add_framework(fw2)

    related = graph.find_cross_references(fw1.id, depth=1)
    assert len(related) == 1
    assert related[0].name == "SimCLR"

    print("✓ Cross-reference traversal working")


def test_superbrain_integration():
    """Test integration with SuperBrain equation bridge."""
    graph = AIFrameworkKnowledgeGraph()

    # Add sample frameworks
    frameworks = [
        AIFrameworkEntry(
            id="",
            section_number=2,
            name="Attention",
            category=AIFrameworkCategory.TRANSFORMERS,
            latex_formula=r"softmax(QK^T)V",
            description="Attention",
            implementation_hint="Hint",
        ),
        AIFrameworkEntry(
            id="",
            section_number=75,
            name="MAML",
            category=AIFrameworkCategory.META_LEARNING,
            latex_formula=r"\min L",
            description="MAML",
            implementation_hint="Hint",
        ),
    ]

    for fw in frameworks:
        graph.add_framework(fw)

    integration = AIFrameworkSuperBrainIntegration(graph)

    # Test domain mapping
    domain = integration.get_superbrain_domain(AIFrameworkCategory.TRANSFORMERS)
    assert domain is not None

    # Test cross-domain link generation
    fw_id = list(graph.frameworks.keys())[0]
    links = integration.find_cross_domain_equations(fw_id)
    assert isinstance(links, list)

    print("✓ SuperBrain integration working")


def test_implementation_plan_generation():
    """Test generating implementation plans."""
    graph = AIFrameworkKnowledgeGraph()

    fw = AIFrameworkEntry(
        id="",
        section_number=75,
        name="MAML Meta-Learning",
        category=AIFrameworkCategory.META_LEARNING,
        latex_formula=r"\min_\theta \sum L_i",
        description="Few-shot meta-learning",
        implementation_hint="Compute second-order gradients",
        invariants=["Fast adaptation"],
        source_framework="PyTorch",
        paper_reference="Finn et al. 2017",
        tags=["meta_learning"],
    )

    graph.add_framework(fw)

    integration = AIFrameworkSuperBrainIntegration(graph)
    plan = integration.generate_implementation_plan("MAML Meta-Learning")

    assert "framework" in plan
    assert plan["framework"] == "MAML Meta-Learning"
    assert "implementation_steps" in plan
    assert len(plan["implementation_steps"]) > 0

    print("✓ Implementation plan generation working")


def test_serialization():
    """Test JSON serialization/deserialization."""
    import tempfile

    graph = AIFrameworkKnowledgeGraph()

    fw = AIFrameworkEntry(
        id="",
        section_number=77,
        name="Backdoor Adjustment",
        category=AIFrameworkCategory.CAUSAL_INFERENCE,
        latex_formula=r"P(y|do(x)) = \sum_z P(y|x,z)P(z)",
        description="Causal inference",
        implementation_hint="Check backdoor criterion",
    )

    graph.add_framework(fw)

    # Serialize
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = Path(f.name)

    graph.to_json(temp_path)

    # Deserialize
    loaded_graph = AIFrameworkKnowledgeGraph.from_json(temp_path)

    assert len(loaded_graph.frameworks) == len(graph.frameworks)
    assert loaded_graph.metadata.total_equations == graph.metadata.total_equations

    # Cleanup
    temp_path.unlink()

    print("✓ Serialization/deserialization working")


def test_parser():
    """Test parser functionality."""
    # Create a mock markdown file
    import tempfile

    mock_content = """
## 1. Transformer Attention
**Formula:**
```
Attention(Q,K,V) = softmax(QK^T/√d_k)V
```

## 2. Gradient Descent
**Formula:**
```
w ← w - η·∇L
```
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(mock_content)
        temp_path = Path(f.name)

    parser = AIFrameworkParser(temp_path)
    graph = parser.parse()

    assert len(graph.frameworks) > 0

    # Cleanup
    temp_path.unlink()

    print(f"✓ Parser working ({len(graph.frameworks)} frameworks extracted)")


def test_full_integration():
    """Test full integration workflow."""
    import tempfile

    # Create mock document
    mock_doc = """
## 75. MAML Meta-Learning
**Source**: Finn et al. 2017

**Formula:**
```
min_θ Σ L(θ - α·∇L, D_query)
```

## 76. SimCLR
**Source**: Chen et al. 2020

**Formula:**
```
l = -log[exp(sim/τ) / Σ exp(sim/τ)]
```
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(mock_doc)
        doc_path = Path(f.name)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "ai_frameworks_kg.json"

        # Build knowledge base
        graph = build_ai_frameworks_knowledge_base(doc_path, output_path)

        # Integrate with SuperBrain
        integration = integrate_with_superbrain(graph)

        assert integration["integration_status"] == "success"
        assert integration["ai_frameworks_count"] > 0

    # Cleanup
    doc_path.unlink()

    print("✓ Full integration workflow working")


def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 60)
    print("AMOS AI Frameworks Bridge Test Suite")
    print("=" * 60 + "\n")

    tests = [
        ("Categories", test_categories),
        ("Framework Entry", test_framework_entry_creation),
        ("Knowledge Graph", test_knowledge_graph_operations),
        ("Cross References", test_cross_references),
        ("SuperBrain Integration", test_superbrain_integration),
        ("Implementation Plans", test_implementation_plan_generation),
        ("Serialization", test_serialization),
        ("Parser", test_parser),
        ("Full Integration", test_full_integration),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
