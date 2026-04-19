#!/usr/bin/env python3
"""AMOS Knowledge-Integrated Reasoning
====================================
Query 886MB of activated knowledge during AMOS Brain reasoning.

Features:
- Auto-knowledge lookup during reasoning
- Context injection from relevant engines
- Relevance scoring for knowledge matching
- Real-time knowledge augmentation
- Hybrid reasoning: base + knowledge-enhanced

Usage:
    python amos_reasoning_with_knowledge.py [command]

Commands:
    reason <problem>    Reason with knowledge augmentation
    query <topic>       Query knowledge during analysis
    augment <text>      Augment text with relevant knowledge
    demo                Demonstrate knowledge-enhanced reasoning
"""

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class KnowledgeMatch:
    """A knowledge match with relevance score."""

    engine_key: str
    category: str
    relevance_score: float
    excerpt: str
    source: str


class KnowledgeIntegratedReasoning:
    """AMOS reasoning with 886MB knowledge integration."""

    # Knowledge category mappings for problem types
    PROBLEM_CATEGORIES = {
        "biology": ["biology", "nbi", "bei", "ubi"],
        "engineering": ["engineering", "physics", "master_brain"],
        "law": ["law", "si", "master_brain"],
        "economics": ["economics", "strategy", "master_brain"],
        "society": ["society", "si", "nei", "master_brain"],
        "strategy": ["strategy", "master_brain", "si"],
        "cognition": ["biology", "nbi", "nei", "ubi"],
        "health": ["biology", "nbi", "bei", "ubi"],
        "decision": ["strategy", "law", "economics", "master_brain"],
        "ethics": ["law", "si", "nei", "master_brain"],
    }

    def __init__(self):
        self.activation = None
        self._init_activation()

    def _init_activation(self):
        """Initialize knowledge activation."""
        try:
            from amos_knowledge_activation import KnowledgeActivation

            self.activation = KnowledgeActivation()
            # Activate critical engines
            self.activation.activate_critical_engines()
        except Exception as e:
            print(f"Warning: Could not initialize knowledge activation: {e}")
            self.activation = None

    def _get_active_knowledge(self) -> Dict[str, Any]:
        """Get currently active knowledge."""
        if not self.activation:
            return {}
        return self.activation.active_knowledge

    def _score_relevance(self, problem: str, engine_key: str, knowledge: Any) -> float:
        """Score relevance of knowledge to problem (0-1)."""
        problem_lower = problem.lower()
        score = 0.0

        # Category matching
        for category, engines in self.PROBLEM_CATEGORIES.items():
            if category in problem_lower and engine_key in engines:
                score += 0.5

        # Engine name matching
        if engine_key in problem_lower:
            score += 0.3

        # Content keyword matching (if content is dict)
        if hasattr(knowledge, "content") and isinstance(knowledge.content, dict):
            content_str = json.dumps(knowledge.content).lower()
            problem_words = set(problem_lower.split())
            matches = sum(1 for word in problem_words if len(word) > 4 and word in content_str)
            score += min(matches * 0.05, 0.2)

        return min(score, 1.0)

    def find_relevant_knowledge(self, problem: str, top_n: int = 5) -> List[KnowledgeMatch]:
        """Find most relevant knowledge for a problem."""
        active = self._get_active_knowledge()
        if not active:
            return []

        matches = []
        for engine_key, knowledge in active.items():
            score = self._score_relevance(problem, engine_key, knowledge)
            if score > 0.1:  # Minimum relevance threshold
                # Get excerpt from content
                excerpt = ""
                if hasattr(knowledge, "content") and isinstance(knowledge.content, dict):
                    # Try to get description or first meaningful field
                    if "description" in knowledge.content:
                        excerpt = knowledge.content["description"][:200]
                    elif "meta" in knowledge.content and isinstance(
                        knowledge.content["meta"], dict
                    ):
                        excerpt = str(knowledge.content["meta"])[:200]
                    else:
                        excerpt = (
                            str(list(knowledge.content.values())[0])[:200]
                            if knowledge.content
                            else ""
                        )

                matches.append(
                    KnowledgeMatch(
                        engine_key=engine_key,
                        category=knowledge.category
                        if hasattr(knowledge, "category")
                        else "unknown",
                        relevance_score=score,
                        excerpt=excerpt,
                        source=f"AMOS_{engine_key}_Engine",
                    )
                )

        # Sort by relevance and return top N
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches[:top_n]

    def reason_with_knowledge(
        self, problem: str, use_rule_of_2: bool = True, use_rule_of_4: bool = True
    ) -> Dict[str, Any]:
        """Perform knowledge-integrated reasoning."""
        print("=" * 70)
        print("AMOS KNOWLEDGE-INTEGRATED REASONING")
        print("=" * 70)
        print(f"\nProblem: {problem}")
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Step 1: Find relevant knowledge
        print("\n[STEP 1] Knowledge Retrieval")
        relevant = self.find_relevant_knowledge(problem, top_n=5)
        print(f"  Found {len(relevant)} relevant knowledge sources")

        for i, match in enumerate(relevant[:3], 1):
            print(f"  {i}. {match.engine_key} ({match.category})")
            print(f"     Relevance: {match.relevance_score:.2f}")
            if match.excerpt:
                print(f"     Excerpt: {match.excerpt[:80]}...")

        # Step 2: Base reasoning
        print("\n[STEP 2] Base Reasoning (AMOS Brain)")
        base_analysis = self._base_reasoning(problem, use_rule_of_2, use_rule_of_4)

        # Step 3: Knowledge augmentation
        print("\n[STEP 3] Knowledge Augmentation")
        augmented = self._augment_with_knowledge(base_analysis, relevant)

        # Step 4: Integrated conclusion
        print("\n[STEP 4] Integrated Conclusion")
        conclusion = self._generate_conclusion(problem, base_analysis, augmented, relevant)

        result = {
            "problem": problem,
            "timestamp": datetime.now().isoformat(),
            "knowledge_sources_used": len(relevant),
            "base_analysis": base_analysis,
            "knowledge_augmented": augmented,
            "conclusion": conclusion,
            "relevant_knowledge": [
                {"engine": m.engine_key, "score": m.relevance_score, "category": m.category}
                for m in relevant[:5]
            ],
        }

        print("\n" + "=" * 70)
        print("REASONING COMPLETE")
        print("=" * 70)

        return result

    def _base_reasoning(
        self, problem: str, use_rule_of_2: bool, use_rule_of_4: bool
    ) -> Dict[str, Any]:
        """Perform base AMOS reasoning."""
        analysis = {
            "problem_type": self._classify_problem(problem),
            "frameworks_applied": [],
            "initial_analysis": "",
        }

        # Rule of 2: Dual perspective
        if use_rule_of_2:
            analysis["frameworks_applied"].append("Rule of 2 (Dual Perspective)")
            analysis["dual_perspective"] = {
                "perspective_a": self._generate_perspective(problem, "internal"),
                "perspective_b": self._generate_perspective(problem, "external"),
            }

        # Rule of 4: Four quadrants
        if use_rule_of_4:
            analysis["frameworks_applied"].append("Rule of 4 (Four Quadrants)")
            analysis["four_quadrants"] = {
                "biological": self._analyze_quadrant(problem, "biological"),
                "technical": self._analyze_quadrant(problem, "technical"),
                "economic": self._analyze_quadrant(problem, "economic"),
                "social": self._analyze_quadrant(problem, "social"),
            }

        return analysis

    def _classify_problem(self, problem: str) -> str:
        """Classify problem type."""
        problem_lower = problem.lower()

        keywords = {
            "biology": ["biology", "health", "medical", "body", "brain", "neuro"],
            "engineering": ["engineering", "system", "design", "architecture", "build"],
            "law": ["law", "legal", "policy", "governance", "compliance"],
            "economics": ["economics", "finance", "money", "cost", "market"],
            "society": ["society", "social", "culture", "people", "community"],
            "strategy": ["strategy", "decision", "plan", "tactics", "game"],
        }

        scores = {}
        for category, words in keywords.items():
            scores[category] = sum(1 for word in words if word in problem_lower)

        if scores:
            best = max(scores, key=scores.get)
            return best if scores[best] > 0 else "general"
        return "general"

    def _generate_perspective(self, problem: str, perspective_type: str) -> str:
        """Generate a perspective on the problem."""
        perspectives = {
            "internal": f"Internal view: The core mechanisms and internal dynamics of: {problem[:50]}...",
            "external": f"External view: Environmental factors and external influences on: {problem[:50]}...",
        }
        return perspectives.get(perspective_type, "Perspective not available")

    def _analyze_quadrant(self, problem: str, quadrant: str) -> str:
        """Analyze problem from a quadrant perspective."""
        analyses = {
            "biological": f"Biological dimension: Living systems, organisms, health impacts of: {problem[:40]}...",
            "technical": f"Technical dimension: Systems, engineering, implementation of: {problem[:40]}...",
            "economic": f"Economic dimension: Costs, benefits, market dynamics of: {problem[:40]}...",
            "social": f"Social dimension: Human factors, cultural impacts of: {problem[:40]}...",
        }
        return analyses.get(quadrant, "Analysis not available")

    def _augment_with_knowledge(
        self, base_analysis: dict, relevant: List[KnowledgeMatch]
    ) -> Dict[str, Any]:
        """Augment analysis with knowledge."""
        augmentation = {"knowledge_contributions": [], "enhanced_insights": []}

        for match in relevant[:3]:
            contribution = {
                "source": match.engine_key,
                "relevance": match.relevance_score,
                "insight": f"From {match.engine_key}: {match.excerpt[:100]}...",
            }
            augmentation["knowledge_contributions"].append(contribution)

        # Generate enhanced insights
        problem_type = base_analysis.get("problem_type", "general")
        augmentation["enhanced_insights"].append(
            f"Knowledge-enhanced analysis for {problem_type} domain"
        )

        if relevant:
            top_engine = relevant[0].engine_key
            augmentation["enhanced_insights"].append(
                f"Primary knowledge source: {top_engine} (relevance: {relevant[0].relevance_score:.2f})"
            )

        return augmentation

    def _generate_conclusion(
        self, problem: str, base: dict, augmented: dict, relevant: list
    ) -> Dict[str, Any]:
        """Generate final integrated conclusion."""
        conclusion = {
            "summary": f"Integrated analysis of: {problem[:60]}...",
            "frameworks_used": base.get("frameworks_applied", []),
            "knowledge_leveraged": len(relevant),
            "recommendation": "",
            "confidence": 0.0,
        }

        # Calculate confidence based on knowledge availability
        if len(relevant) >= 3:
            conclusion["confidence"] = 0.85
            conclusion["recommendation"] = (
                "High confidence: Multiple knowledge sources aligned. Proceed with integrated approach."
            )
        elif len(relevant) >= 1:
            conclusion["confidence"] = 0.65
            conclusion["recommendation"] = (
                "Moderate confidence: Limited knowledge sources available. Consider activating more engines."
            )
        else:
            conclusion["confidence"] = 0.45
            conclusion["recommendation"] = (
                "Low confidence: No relevant knowledge activated. Activate appropriate engines first."
            )

        print(f"\n  Summary: {conclusion['summary']}")
        print(f"  Frameworks: {', '.join(conclusion['frameworks_used'])}")
        print(f"  Knowledge Sources: {conclusion['knowledge_leveraged']}")
        print(f"  Confidence: {conclusion['confidence']:.0%}")
        print(f"  Recommendation: {conclusion['recommendation']}")

        return conclusion

    def augment_text(self, text: str) -> str:
        """Augment text with relevant knowledge."""
        relevant = self.find_relevant_knowledge(text, top_n=3)

        if not relevant:
            return text

        # Build knowledge appendix
        appendix = "\n\n[Knowledge-Augmented Context]\n"
        for i, match in enumerate(relevant, 1):
            appendix += f"{i}. [{match.engine_key}] {match.excerpt[:100]}...\n"

        return text + appendix

    def demo(self):
        """Demonstrate knowledge-integrated reasoning."""
        demo_problems = [
            "How should we approach building a sustainable biological system?",
            "What is the optimal strategy for ethical AI governance?",
            "How do social and economic factors interact in urban planning?",
            "Design a resilient technical architecture for planetary-scale systems",
        ]

        for problem in demo_problems:
            print("\n" + "=" * 70)
            result = self.reason_with_knowledge(problem)
            print("\n" + "-" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Knowledge-Integrated Reasoning - Use 886MB during cognition",
        epilog="""
Examples:
  python amos_reasoning_with_knowledge.py reason "How do we build ethical AI?"
  python amos_reasoning_with_knowledge.py query "biology"
  python amos_reasoning_with_knowledge.py augment "System design problem..."
  python amos_reasoning_with_knowledge.py demo
        """,
    )
    parser.add_argument(
        "command", nargs="?", default="demo", choices=["reason", "query", "augment", "demo"]
    )
    parser.add_argument("text", nargs="?", help="Problem text or query")

    args = parser.parse_args()

    reasoning = KnowledgeIntegratedReasoning()

    if args.command == "reason":
        if args.text:
            result = reasoning.reason_with_knowledge(args.text)
            # Save result
            output_file = Path("amos_reasoning_result.json")
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n✓ Result saved to: {output_file}")
        else:
            print("Usage: python amos_reasoning_with_knowledge.py reason '<problem>'")
    elif args.command == "query":
        if args.text:
            matches = reasoning.find_relevant_knowledge(args.text, top_n=10)
            print(f"\nQuery: {args.text}")
            print(f"Found {len(matches)} relevant knowledge sources:")
            for i, match in enumerate(matches, 1):
                print(f"\n{i}. {match.engine_key}")
                print(f"   Category: {match.category}")
                print(f"   Relevance: {match.relevance_score:.2f}")
                if match.excerpt:
                    print(f"   Excerpt: {match.excerpt[:100]}...")
        else:
            print("Usage: python amos_reasoning_with_knowledge.py query <topic>")
    elif args.command == "augment":
        if args.text:
            augmented = reasoning.augment_text(args.text)
            print("\nOriginal:")
            print(args.text[:100] + "...")
            print("\nAugmented:")
            print(augmented)
        else:
            print("Usage: python amos_reasoning_with_knowledge.py augment '<text>'")
    elif args.command == "demo":
        reasoning.demo()

    return 0


if __name__ == "__main__":
    sys.exit(main())
