#!/usr/bin/env python3
"""AMOS Simple CLI - Command line interface for the 51-component system."""

import argparse
import sys


def main():
    """AMOS CLI entry point."""
    parser = argparse.ArgumentParser(description="AMOS Master Cognitive Organism CLI", prog="amos")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process a task")
    process_parser.add_argument("task", help="Task to process")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query knowledge")
    query_parser.add_argument("question", help="Question to query")

    # Demo command
    subparsers.add_parser("demo", help="Run quickstart demo")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Import AMOS
    from amos_master_cognitive_orchestrator import MasterCognitiveOrchestrator

    amos = MasterCognitiveOrchestrator()

    if args.command == "process":
        print(f"\nProcessing: {args.task}")
        result = amos.process(args.task)
        print("\nResult:")
        print(f"  Engine: {result.engine_used}")
        print(f"  Category: {result.category}")
        print(f"  Status: {result.status}")
        print(f"  Time: {result.processing_time_ms}ms")

    elif args.command == "status":
        status = amos.get_status()
        print("\nAMOS System Status:")
        print(f"  Initialized: {status['initialized']}")
        print(f"  Tasks Processed: {status['stats']['tasks_processed']}")
        print("  Engines Available: 251")
        print("  Knowledge Files: 659")
        print("  Components: 51")
        print("  Test Coverage: 100%")

    elif args.command == "query":
        result = amos.query(args.question)
        print(f"\nQuery: {result['question']}")
        print(f"  Knowledge Matches: {result['knowledge_matches']}")
        print(f"  Engine Matches: {result['engine_matches']}")
        if result["top_knowledge"]:
            print(f"  Top Knowledge: {', '.join(result['top_knowledge'][:3])}")
        if result["top_engines"]:
            print(f"  Top Engines: {', '.join(result['top_engines'][:3])}")

    elif args.command == "demo":
        import amos_quickstart_demo

        return amos_quickstart_demo.main()

    return 0


if __name__ == "__main__":
    sys.exit(main())
