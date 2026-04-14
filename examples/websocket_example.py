#!/usr/bin/env python3
"""AMOS Brain WebSocket Client (Python)

Usage:
    python websocket_example.py think "What are design patterns?"
    python websocket_example.py decide "Which database?" --options SQL NoSQL
"""

import argparse
import asyncio
import json

import websockets


class AMOSWebSocketClient:
    """Python WebSocket client for AMOS Brain."""

    def __init__(self, url="ws://neurosyncai.tech:8765"):
        self.url = url

    async def think(self, query, domain="general"):
        """Stream thinking process."""
        async with websockets.connect(self.url) as ws:
            # Send request
            await ws.send(json.dumps({"action": "think", "query": query, "domain": domain}))

            print(f"\n🤔 Thinking about: {query}\n")

            # Stream responses
            async for message in ws:
                data = json.loads(message)

                if data["type"] == "step":
                    print(f"  Step {data['number']}: {data['content'][:60]}...")

                elif data["type"] == "complete":
                    print("\n✅ Complete!")
                    print(f"   Confidence: {data['confidence']}")
                    print(f"   Law Compliant: {data['law_compliant']}")
                    break

                elif data["type"] == "error":
                    print(f"\n❌ Error: {data['message']}")
                    break

    async def decide(self, question, options=None):
        """Stream decision process."""
        async with websockets.connect(self.url) as ws:
            await ws.send(
                json.dumps({"action": "decide", "question": question, "options": options or []})
            )

            print(f"\n🎯 Deciding: {question}\n")

            async for message in ws:
                data = json.loads(message)

                if data["type"] == "analysis":
                    print(f"  📊 {data['step']}")

                elif data["type"] == "complete":
                    print("\n✅ Decision:")
                    print(f"   Approved: {data['approved']}")
                    print(f"   Risk: {data['risk_level']}")
                    print(f"   Reasoning: {data['reasoning'][:100]}...")
                    break

                elif data["type"] == "error":
                    print(f"\n❌ Error: {data['message']}")
                    break


def main():
    parser = argparse.ArgumentParser(description="AMOS Brain WebSocket Client")
    parser.add_argument("action", choices=["think", "decide"])
    parser.add_argument("input", help="Query or question")
    parser.add_argument("--domain", default="general", help="Domain for think")
    parser.add_argument("--options", nargs="+", help="Options for decide")
    parser.add_argument("--url", default="ws://neurosyncai.tech:8765", help="WebSocket URL")

    args = parser.parse_args()

    client = AMOSWebSocketClient(args.url)

    if args.action == "think":
        asyncio.run(client.think(args.input, args.domain))
    elif args.action == "decide":
        asyncio.run(client.decide(args.input, args.options))


if __name__ == "__main__":
    main()
