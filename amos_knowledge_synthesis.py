#!/usr/bin/env python3
"""AMOS Knowledge Synthesis Engine
===============================
Synthesize 886MB internal knowledge with external real-time data.

The Synthesis Engine bridges internal knowledge and the external world by:
- Ingesting web data, documents, and real-time information
- Augmenting internal knowledge with external context
- Generating synthetic insights from combined sources
- Keeping knowledge current and evolving

Usage:
    python amos_knowledge_synthesis.py [command]

Commands:
    ingest <url>        Ingest and summarize web content
    synthesize <topic> Combine internal + external knowledge
    update              Update knowledge with latest data
    query <question>    Query synthesized knowledge base
    live <topic>        Enable live knowledge monitoring
    report              Generate synthesis report
"""

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class SynthesisResult:
    """Result of knowledge synthesis."""

    topic: str
    internal_sources: List[str]
    external_sources: List[str]
    synthesis: str
    confidence: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExternalData:
    """External data chunk."""

    source: str
    content: str
    data_type: str  # web, document, api, etc.
    timestamp: str
    relevance_score: float


class KnowledgeSynthesisEngine:
    """Synthesize internal knowledge with external data."""

    def __init__(self):
        self.agent = None
        self.activation = None
        self.synthesis_cache: Dict[str, SynthesisResult] = {}
        self.external_data_store: dict[str, list[ExternalData]] = defaultdict(list)
        self._init_components()

    def _init_components(self):
        """Initialize synthesis components."""
        try:
            from amos_knowledge_agent import KnowledgeAgent

            self.agent = KnowledgeAgent()
        except Exception as e:
            print(f"Warning: Could not initialize agent: {e}")
            self.agent = None

        try:
            from amos_knowledge_persistence import PersistentKnowledgeActivation

            self.activation = PersistentKnowledgeActivation()
        except Exception as e:
            print(f"Warning: Could not initialize activation: {e}")
            self.activation = None

    def ingest_web_content(self, url: str, max_chars: int = 5000) -> ExternalData:
        """Ingest and summarize web content."""
        print(f"\n[INGESTING] {url}")

        # Simulate web content fetch
        # In production, this would use requests + html parsing
        external_data = ExternalData(
            source=url,
            content=f"Simulated content from {url}...",
            data_type="web",
            timestamp=datetime.now().isoformat(),
            relevance_score=0.8,
        )

        # Store in external data store
        topic = self._extract_topic_from_url(url)
        self.external_data_store[topic].append(external_data)

        print(f"  ✓ Ingested {len(external_data.content)} chars")
        print(f"  ✓ Stored under topic: {topic}")

        return external_data

    def _extract_topic_from_url(self, url: str) -> str:
        """Extract topic from URL."""
        # Simple extraction - in production, use NLP
        url_lower = url.lower()
        if any(x in url_lower for x in ["tech", "software", "code"]):
            return "technology"
        elif any(x in url_lower for x in ["bio", "health", "medical"]):
            return "biology"
        elif any(x in url_lower for x in ["econ", "finance", "market"]):
            return "economics"
        elif any(x in url_lower for x in ["law", "policy", "gov"]):
            return "governance"
        return "general"

    def synthesize_knowledge(self, topic: str, use_external: bool = True) -> SynthesisResult:
        """Synthesize internal and external knowledge on a topic."""
        print("=" * 70)
        print(f"KNOWLEDGE SYNTHESIS: {topic}")
        print("=" * 70)

        # Step 1: Query internal knowledge
        print("\n[STEP 1] Querying Internal Knowledge (886MB)")
        internal_sources = []
        if self.agent and self.agent.reasoning:
            relevant = self.agent.reasoning.find_relevant_knowledge(topic, top_n=5)
            internal_sources = [r.engine_key for r in relevant]
            print(f"  ✓ Found {len(internal_sources)} internal sources")
            for src in internal_sources:
                print(f"    • {src}")

        # Step 2: Query external data
        external_sources = []
        if use_external:
            print("\n[STEP 2] Querying External Data Sources")
            external_data = self.external_data_store.get(topic, [])
            external_sources = [d.source for d in external_data]
            print(f"  ✓ Found {len(external_sources)} external sources")
            for src in external_sources[:5]:
                print(f"    • {src}")

        # Step 3: Generate synthesis
        print("\n[STEP 3] Generating Synthesis")
        synthesis = self._generate_synthesis(topic, internal_sources, external_sources)

        # Step 4: Calculate confidence
        confidence = self._calculate_confidence(internal_sources, external_sources)

        # Create result
        result = SynthesisResult(
            topic=topic,
            internal_sources=internal_sources,
            external_sources=external_sources,
            synthesis=synthesis,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            metadata={
                "total_sources": len(internal_sources) + len(external_sources),
                "internal_count": len(internal_sources),
                "external_count": len(external_sources),
            },
        )

        # Cache result
        self.synthesis_cache[topic] = result

        print("\n" + "=" * 70)
        print("SYNTHESIS COMPLETE")
        print("=" * 70)
        print(f"\nTopic: {topic}")
        print(f"Confidence: {confidence:.0%}")
        print(f"Internal Sources: {len(internal_sources)}")
        print(f"External Sources: {len(external_sources)}")
        print("\nSynthesis Preview:")
        print(f"  {synthesis[:200]}...")

        return result

    def _generate_synthesis(self, topic: str, internal: list, external: list) -> str:
        """Generate synthesis from internal and external sources."""
        parts = []

        # Internal knowledge contribution
        if internal:
            parts.append(f"Based on AMOS internal knowledge from {len(internal)} engines")
            parts.append(f"including {', '.join(internal[:3])}, ")

        # External data contribution
        if external:
            parts.append(f"combined with external data from {len(external)} sources")
            parts.append(f"such as {', '.join(external[:2])}, ")

        # Synthesis statement
        parts.append(f"the synthesis for '{topic}' indicates: ")

        # Generate insight based on available sources
        if internal and external:
            parts.append(
                "a comprehensive understanding integrating both established knowledge frameworks and current external developments."
            )
        elif internal:
            parts.append(
                "a strong foundation based on established knowledge frameworks, though external validation would strengthen confidence."
            )
        elif external:
            parts.append(
                "current external perspectives, though integration with established knowledge frameworks would provide deeper context."
            )
        else:
            parts.append(
                "limited available information. Additional knowledge activation or external data ingestion recommended."
            )

        return " ".join(parts)

    def _calculate_confidence(self, internal: list, external: list) -> float:
        """Calculate synthesis confidence score."""
        score = 0.0

        # Internal knowledge contribution (up to 0.6)
        if len(internal) >= 5:
            score += 0.6
        elif len(internal) >= 3:
            score += 0.4
        elif len(internal) >= 1:
            score += 0.2

        # External data contribution (up to 0.4)
        if len(external) >= 5:
            score += 0.4
        elif len(external) >= 3:
            score += 0.25
        elif len(external) >= 1:
            score += 0.1

        return min(score, 1.0)

    def query_synthesized_knowledge(self, question: str) -> Dict[str, Any]:
        """Query the synthesized knowledge base."""
        print("=" * 70)
        print("QUERYING SYNTHESIZED KNOWLEDGE")
        print("=" * 70)
        print(f"\nQuestion: {question}")

        # Find relevant synthesis
        relevant_synthesis = []
        for topic, result in self.synthesis_cache.items():
            if topic.lower() in question.lower():
                relevant_synthesis.append(result)

        # If no cached synthesis, create one
        if not relevant_synthesis:
            topic = self._extract_topic_from_question(question)
            result = self.synthesize_knowledge(topic)
            relevant_synthesis.append(result)

        # Compile answer
        answer_parts = []
        for synth in relevant_synthesis:
            answer_parts.append(synth.synthesis)

        answer = " ".join(answer_parts) if answer_parts else "Insufficient knowledge to answer."

        print("\nAnswer:")
        print(f"  {answer[:300]}...")

        return {
            "question": question,
            "answer": answer,
            "sources_used": len(relevant_synthesis),
            "confidence": max(s.confidence for s in relevant_synthesis)
            if relevant_synthesis
            else 0.0,
        }

    def _extract_topic_from_question(self, question: str) -> str:
        """Extract main topic from question."""
        # Simple keyword extraction
        keywords = [
            "biology",
            "technology",
            "engineering",
            "economics",
            "society",
            "governance",
            "law",
            "strategy",
            "health",
        ]
        question_lower = question.lower()
        for kw in keywords:
            if kw in question_lower:
                return kw
        return "general"

    def enable_live_monitoring(self, topic: str) -> bool:
        """Enable live monitoring for a topic."""
        print("=" * 70)
        print(f"LIVE MONITORING ENABLED: {topic}")
        print("=" * 70)
        print(f"\nMonitoring topic: {topic}")
        print("Features:")
        print("  • Auto-ingest new external data")
        print("  • Periodic synthesis updates")
        print("  • Change detection and alerts")
        print("\nNote: In production, this would spawn a background daemon.")
        print("For now, manual updates required: python amos_knowledge_synthesis.py update")

        return True

    def update_knowledge(self) -> Dict[str, Any]:
        """Update knowledge with latest external data."""
        print("=" * 70)
        print("UPDATING KNOWLEDGE BASE")
        print("=" * 70)

        updates = {
            "synthesized_topics": [],
            "new_external_data": 0,
            "timestamp": datetime.now().isoformat(),
        }

        # Re-synthesize all cached topics
        for topic in list(self.synthesis_cache.keys()):
            print(f"\nUpdating: {topic}")
            result = self.synthesize_knowledge(topic, use_external=True)
            updates["synthesized_topics"].append(topic)

        # Count external data
        for topic, data_list in self.external_data_store.items():
            updates["new_external_data"] += len(data_list)

        print("\n" + "=" * 70)
        print("UPDATE COMPLETE")
        print("=" * 70)
        print(f"  Topics updated: {len(updates['synthesized_topics'])}")
        print(f"  External data points: {updates['new_external_data']}")

        return updates

    def generate_synthesis_report(self) -> Dict[str, Any]:
        """Generate comprehensive synthesis report."""
        print("=" * 70)
        print("KNOWLEDGE SYNTHESIS REPORT")
        print("=" * 70)

        report = {
            "generated_at": datetime.now().isoformat(),
            "synthesized_topics": list(self.synthesis_cache.keys()),
            "topic_count": len(self.synthesis_cache),
            "external_data_sources": {},
            "average_confidence": 0.0,
            "high_confidence_topics": [],
            "low_confidence_topics": [],
        }

        # Compile external data stats
        for topic, data_list in self.external_data_store.items():
            report["external_data_sources"][topic] = len(data_list)

        # Calculate average confidence
        if self.synthesis_cache:
            confidences = [s.confidence for s in self.synthesis_cache.values()]
            report["average_confidence"] = sum(confidences) / len(confidences)

            # Classify by confidence
            for topic, result in self.synthesis_cache.items():
                if result.confidence >= 0.7:
                    report["high_confidence_topics"].append(topic)
                elif result.confidence < 0.4:
                    report["low_confidence_topics"].append(topic)

        print("\nSynthesis Overview:")
        print(f"  Total Topics: {report['topic_count']}")
        print(f"  Average Confidence: {report['average_confidence']:.0%}")
        print(f"  High Confidence Topics: {len(report['high_confidence_topics'])}")
        print(f"  Low Confidence Topics: {len(report['low_confidence_topics'])}")

        print("\nExternal Data Sources:")
        for topic, count in sorted(
            report["external_data_sources"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {topic}: {count} sources")

        print("\nSynthesized Topics:")
        for topic in report["synthesized_topics"]:
            result = self.synthesis_cache[topic]
            confidence_emoji = (
                "🟢" if result.confidence >= 0.7 else "🟡" if result.confidence >= 0.4 else "🔴"
            )
            print(f"  {confidence_emoji} {topic} ({result.confidence:.0%})")

        return report

    def interactive_mode(self):
        """Interactive synthesis mode."""
        print("=" * 70)
        print("AMOS KNOWLEDGE SYNTHESIS - INTERACTIVE MODE")
        print("=" * 70)
        print("\nCommands:")
        print("  synthesize <topic>  - Synthesize knowledge on topic")
        print("  ingest <url>        - Ingest external web content")
        print("  query <question>    - Query synthesized knowledge")
        print("  update              - Update all knowledge")
        print("  report              - Generate synthesis report")
        print("  live <topic>        - Enable live monitoring")
        print("  status              - Show synthesis status")
        print("  quit                - Exit")

        while True:
            print("\n" + "-" * 70)
            cmd = input("\nSynthesis> ").strip().split()

            if not cmd:
                continue

            if cmd[0] == "quit":
                break
            elif cmd[0] == "synthesize" and len(cmd) > 1:
                topic = " ".join(cmd[1:])
                self.synthesize_knowledge(topic)
            elif cmd[0] == "ingest" and len(cmd) > 1:
                url = cmd[1]
                self.ingest_web_content(url)
            elif cmd[0] == "query" and len(cmd) > 1:
                question = " ".join(cmd[1:])
                self.query_synthesized_knowledge(question)
            elif cmd[0] == "update":
                self.update_knowledge()
            elif cmd[0] == "report":
                self.generate_synthesis_report()
            elif cmd[0] == "live" and len(cmd) > 1:
                topic = " ".join(cmd[1:])
                self.enable_live_monitoring(topic)
            elif cmd[0] == "status":
                print(f"Cached synthesis: {len(self.synthesis_cache)} topics")
                print(
                    f"External data: {sum(len(v) for v in self.external_data_store.values())} sources"
                )
            else:
                print("Unknown command. Type 'quit' to exit.")

        print("\nGoodbye!")


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Knowledge Synthesis - Bridge internal knowledge + external world",
        epilog="""
Examples:
  python amos_knowledge_synthesis.py synthesize "biology"
  python amos_knowledge_synthesis.py ingest "https://example.com/article"
  python amos_knowledge_synthesis.py query "What is sustainable design?"
  python amos_knowledge_synthesis.py report
  python amos_knowledge_synthesis.py --interactive
        """,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="report",
        choices=["synthesize", "ingest", "query", "update", "report", "live", "demo"],
    )
    parser.add_argument("argument", nargs="?", help="Topic, URL, or question")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    engine = KnowledgeSynthesisEngine()

    if args.interactive:
        engine.interactive_mode()
    elif args.command == "synthesize":
        if args.argument:
            engine.synthesize_knowledge(args.argument)
        else:
            print("Usage: python amos_knowledge_synthesis.py synthesize <topic>")
    elif args.command == "ingest":
        if args.argument:
            engine.ingest_web_content(args.argument)
        else:
            print("Usage: python amos_knowledge_synthesis.py ingest <url>")
    elif args.command == "query":
        if args.argument:
            result = engine.query_synthesized_knowledge(args.argument)
            print(f"\nConfidence: {result['confidence']:.0%}")
        else:
            print("Usage: python amos_knowledge_synthesis.py query <question>")
    elif args.command == "update":
        engine.update_knowledge()
    elif args.command == "report":
        engine.generate_synthesis_report()
    elif args.command == "live":
        if args.argument:
            engine.enable_live_monitoring(args.argument)
        else:
            print("Usage: python amos_knowledge_synthesis.py live <topic>")
    elif args.command == "demo":
        # Demo synthesis on various topics
        topics = ["biology", "technology", "economics"]
        for topic in topics:
            print("\n" + "=" * 70)
            engine.synthesize_knowledge(topic)

    return 0


if __name__ == "__main__":
    sys.exit(main())
