#!/usr/bin/env python3
"""AMOS SDK CLI - Command line interface for AMOS Brain.

Usage:
    amos think "What is the next logical step?"
    amos decide "Should I build X?" --options "yes,no,maybe"
    amos stats
    amos history
"""
import argparse
import os
import sys
from typing import Optional

from .client import Client
from .exceptions import AmosError


def get_api_key() -> str:
    """Get API key from environment or config."""
    api_key = os.environ.get('AMOS_API_KEY')
    if not api_key:
        print("Error: AMOS_API_KEY environment variable not set", file=sys.stderr)
        print("Get your API key from https://neurosyncai.tech/admin", file=sys.stderr)
        sys.exit(1)
    return api_key


def cmd_think(args):
    """Execute think command."""
    client = Client(api_key=get_api_key())
    
    try:
        result = client.think(args.query, domain=args.domain)
        
        print(f"\n🧠 AMOS Brain Analysis")
        print(f"   Domain: {result.domain}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Law Compliant: {'✓' if result.law_compliant else '✗'}")
        print(f"\n📋 Content:\n{result.content}")
        
        if result.reasoning:
            print(f"\n🔍 Reasoning Chain:")
            for i, step in enumerate(result.reasoning[:5], 1):
                print(f"   {i}. {step}")
                
    except AmosError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_decide(args):
    """Execute decide command."""
    client = Client(api_key=get_api_key())
    options = args.options.split(',') if args.options else []
    
    try:
        result = client.decide(args.question, options)
        
        print(f"\n⚖️  AMOS Brain Decision")
        print(f"   Approved: {'✓' if result.approved else '✗'}")
        print(f"   Risk Level: {result.risk_level}")
        print(f"   Decision ID: {result.decision_id}")
        print(f"\n📝 Reasoning:\n{result.reasoning}")
        
    except AmosError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_stats(args):
    """Execute stats command."""
    client = Client(api_key=get_api_key())
    
    try:
        stats = client.get_stats(days=args.days)
        
        print(f"\n📊 AMOS Brain Usage Stats ({stats.period_days} days)")
        print(f"   Total Requests: {stats.total_requests}")
        print(f"   Avg Response Time: {stats.avg_response_time_ms:.0f}ms")
        print(f"   Success Rate: {stats.success_rate_percent:.1f}%")
        
    except AmosError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_history(args):
    """Execute history command."""
    client = Client(api_key=get_api_key())
    
    try:
        history = client.get_history(limit=args.limit)
        
        print(f"\n📜 Query History (last {len(history)} records)")
        print("-" * 80)
        
        for record in history:
            status = "✓" if record.law_compliant else "✗"
            print(f"\n   [{status}] {record.endpoint.upper()} | {record.domain}")
            print(f"       Query: {record.query[:60]}...")
            print(f"       Time: {record.processing_time_ms}ms | {record.created_at}")
            
    except AmosError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_validate(args):
    """Execute validate command."""
    client = Client(api_key=get_api_key())
    
    try:
        is_valid = client.validate(args.action)
        
        if is_valid:
            print("✓ Action is valid according to AMOS Global Laws")
        else:
            print("✗ Action violates AMOS Global Laws")
            sys.exit(1)
            
    except AmosError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='amos',
        description='AMOS Brain CLI - Cognitive analysis and decision making'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # think command
    think_parser = subparsers.add_parser('think', help='Cognitive analysis')
    think_parser.add_argument('query', help='Query to analyze')
    think_parser.add_argument('--domain', default='general', help='Knowledge domain')
    think_parser.set_defaults(func=cmd_think)
    
    # decide command
    decide_parser = subparsers.add_parser('decide', help='Decision making')
    decide_parser.add_argument('question', help='Decision question')
    decide_parser.add_argument('--options', help='Comma-separated options')
    decide_parser.set_defaults(func=cmd_decide)
    
    # stats command
    stats_parser = subparsers.add_parser('stats', help='Usage statistics')
    stats_parser.add_argument('--days', type=int, default=7, help='Days to include')
    stats_parser.set_defaults(func=cmd_stats)
    
    # history command
    history_parser = subparsers.add_parser('history', help='Query history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of records')
    history_parser.set_defaults(func=cmd_history)
    
    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate action')
    validate_parser.add_argument('action', help='Action to validate')
    validate_parser.set_defaults(func=cmd_validate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
