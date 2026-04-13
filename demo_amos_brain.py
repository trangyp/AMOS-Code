#!/usr/bin/env python3
"""
AMOS Brain Integration Demo

Demonstrates:
1. Brain initialization and status
2. Global laws enforcement
3. Rule of 2 and Rule of 4 reasoning
4. Cognitive stack routing
5. Brain-enhanced system prompts
"""

import sys
sys.path.insert(0, '/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code')

from amos_brain import get_brain, GlobalLaws, RuleOfTwo, RuleOfFour
from amos_brain.cognitive_stack import CognitiveStack
from amos_brain.integration import get_amos_integration


def demo_brain_loading():
    """Demo 1: Brain initialization and status."""
    print("=" * 60)
    print("DEMO 1: AMOS Brain Initialization")
    print("=" * 60)

    amos = get_amos_integration()
    status = amos.get_status()

    print(f"Initialized: {status['initialized']}")
    print(f"Brain Loaded: {status['brain_loaded']}")
    print(f"Engines Available: {status['engines_count']}")
    print(f"Active Laws: {', '.join(status['laws_active'])}")
    print(f"Domains Covered: {len(status['domains_covered'])}")
    print()


def demo_global_laws():
    """Demo 2: Global laws summary."""
    print("=" * 60)
    print("DEMO 2: AMOS Global Laws")
    print("=" * 60)

    amos = get_amos_integration()
    print(amos.get_laws_summary())
    print()


def demo_law_enforcement():
    """Demo 3: Law enforcement examples."""
    print("=" * 60)
    print("DEMO 3: Law Enforcement")
    print("=" * 60)

    laws = GlobalLaws()

    # L1: Operational scope check
    print("L1 - Law of Law (Operational Scope):")
    for action in ["analysis", "financial execution", "medical treatment"]:
        permitted, reason = laws.check_l1_constraint(action)
        print(f"  {action}: {'✓' if permitted else '✗'} {reason}")
    print()

    # L2: Rule of 2
    print("L2 - Rule of 2 (Dual Perspective):")
    analysis = "The market will go up"
    counter = "The market may go down due to external factors"
    passed, result = laws.enforce_l2_dual_check(analysis, counter)
    print(f"  Analysis: '{analysis}'")
    print(f"  Counter: '{counter}'")
    print(f"  Result: {'✓' if passed else '✗'} {result}")

    no_counter = None
    failed, result = laws.enforce_l2_dual_check(analysis, no_counter)
    print(f"  Without counter: {'✓' if failed else '✗'} {result}")
    print()

    # L4: Communication check
    print("L4 - Structural Integrity & L5 - Communication:")
    bad_text = "This field contains sovereignty truth_claims_without_evidence"
    ok, issues = laws.l5_communication_check(bad_text)
    print(f"  Text: '{bad_text}'")
    print(f"  Violations: {issues}")
    print()


def demo_rule_of_two():
    """Demo 4: Rule of 2 reasoning."""
    print("=" * 60)
    print("DEMO 4: Rule of 2 - Dual Perspective Analysis")
    print("=" * 60)

    rule2 = RuleOfTwo()
    problem = "Should we migrate our database to a cloud provider?"
    result = rule2.analyze(problem)

    print(f"Problem: {result['problem']}")
    print()

    for i, p in enumerate(result['perspectives'], 1):
        print(f"Perspective {i}: {p.name}")
        print(f"  Viewpoint: {p.viewpoint}")
        print(f"  Evidence: {p.supporting_evidence}")
        print(f"  Limitations: {p.limitations}")
        print()

    print(f"Synthesis: {result['synthesis']['recommended_path']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print()


def demo_rule_of_four():
    """Demo 5: Rule of 4 reasoning."""
    print("=" * 60)
    print("DEMO 5: Rule of 4 - Four Quadrant Analysis")
    print("=" * 60)

    rule4 = RuleOfFour()
    problem = "Implementing AI automation in our manufacturing process"
    result = rule4.analyze(problem)

    print(f"Problem: {result['problem']}")
    print(f"Completeness: {result['completeness_score']:.0%}")
    print()

    for q_key, q_data in result['quadrant_details'].items():
        print(f"Quadrant: {q_data['name']}")
        print(f"  Priority: {q_data['priority']}")
        print(f"  Relevant Factors: {q_data['relevant_factors']}")
        print(f"  Risks: {q_data['applicable_risks']}")
        print()

    integration = result['integration']
    print(f"Key Quadrants: {integration['key_quadrants']}")
    print(f"Recommendation: {integration['integrated_recommendation']}")
    print()


def demo_cognitive_stack():
    """Demo 6: Cognitive stack routing."""
    print("=" * 60)
    print("DEMO 6: Cognitive Stack Engine Routing")
    print("=" * 60)

    stack = CognitiveStack()

    print(f"Available Engines: {len(stack.list_engines())}")
    print()

    queries = [
        "Design a new user interface for mobile banking",
        "Calculate stress forces on a bridge support beam",
        "Model the economic impact of climate policy",
        "Analyze biological signals from wearable sensors"
    ]

    for query in queries:
        routed = stack.route_query(query)
        print(f"Query: {query[:50]}...")
        print(f"  Routed to: {', '.join(routed[:2])}")
        print()


def demo_system_prompt():
    """Demo 7: Brain-enhanced system prompt."""
    print("=" * 60)
    print("DEMO 7: Enhanced System Prompt (excerpt)")
    print("=" * 60)

    amos = get_amos_integration()
    base = "You are an AI assistant."
    enhanced = amos.enhance_system_prompt(base)

    lines = enhanced.split('\n')
    for line in lines[:30]:
        print(line)
    print("...")
    print()


def demo_pre_post_processing():
    """Demo 8: Pre and post processing."""
    print("=" * 60)
    print("DEMO 8: Pre/Post Processing with Brain")
    print("=" * 60)

    amos = get_amos_integration()

    # Pre-processing
    print("Pre-processing checks:")
    messages = [
        "Analyze the benefits of renewable energy adoption",
        "Design a system for sustainable urban development"
    ]
    for msg in messages:
        result = amos.pre_process(msg)
        status = "BLOCKED" if result.get('blocked') else "OK"
        print(f"  '{msg[:40]}...' -> {status}")
    print()

    # Post-processing
    print("Post-processing validation:")
    responses = [
        "I think the solution is promising but uncertain.",
        "This is definitely the best approach without question."
    ]
    for resp in responses:
        result = amos.post_process(resp, "test")
        print(f"  Text: '{resp[:50]}...'")
        print(f"    Validation: {'PASS' if result['passed_validation'] else 'ISSUES'}")
        if result['structural_issues']:
            print(f"    Issues: {result['structural_issues']}")
    print()


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " AMOS BRAIN INTEGRATION DEMO ".center(58) + "║")
    print("║" + " Cognitive Architecture + Agent Runtime ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    demo_brain_loading()
    demo_global_laws()
    demo_law_enforcement()
    demo_rule_of_two()
    demo_rule_of_four()
    demo_cognitive_stack()
    demo_system_prompt()
    demo_pre_post_processing()

    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("AMOS Brain Integration Layer successfully bridges:")
    print("  • 12 domain intelligences")
    print("  • 6 global laws (L1-L6)")
    print("  • Rule of 2 (dual perspective)")
    print("  • Rule of 4 (four quadrant analysis)")
    print("  • UBI (Unified Biological Intelligence) alignment")
    print("  • Pre/post processing hooks for agent")
    print()


if __name__ == "__main__":
    main()
