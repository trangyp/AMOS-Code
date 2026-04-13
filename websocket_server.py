#!/usr/bin/env python3
"""AMOS Brain WebSocket Server - Real-Time Streaming

Usage:
    python websocket_server.py

Endpoints:
    ws://neurosyncai.tech/ws/think - Stream thinking process
    ws://neurosyncai.tech/ws/decide - Stream decision process
"""

import asyncio
import json
import websockets
from amos_brain import BrainClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

brain = BrainClient()
connected_clients = set()


async def handler(websocket, path):
    """Handle WebSocket connections."""
    connected_clients.add(websocket)
    logger.info(f"Client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'think':
                await stream_think(websocket, data)
            elif action == 'decide':
                await stream_decide(websocket, data)
            else:
                await websocket.send(json.dumps({
                    'error': 'Unknown action. Use: think, decide'
                }))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)


async def stream_think(websocket, data):
    """Stream thinking process in real-time."""
    query = data.get('query', '')
    domain = data.get('domain', 'general')
    
    # Send start signal
    await websocket.send(json.dumps({
        'type': 'start',
        'action': 'think',
        'query': query
    }))
    
    # Simulate streaming reasoning steps
    try:
        result = brain.think(query, domain=domain)
        
        # Stream each reasoning step
        for i, step in enumerate(result.reasoning, 1):
            await websocket.send(json.dumps({
                'type': 'step',
                'number': i,
                'content': step
            }))
            await asyncio.sleep(0.1)  # Small delay for streaming effect
        
        # Send final result
        await websocket.send(json.dumps({
            'type': 'complete',
            'confidence': result.confidence,
            'law_compliant': result.law_compliant,
            'final_content': result.content[:500]
        }))
        
    except Exception as e:
        await websocket.send(json.dumps({
            'type': 'error',
            'message': str(e)
        }))


async def stream_decide(websocket, data):
    """Stream decision process in real-time."""
    question = data.get('question', '')
    options = data.get('options', [])
    
    await websocket.send(json.dumps({
        'type': 'start',
        'action': 'decide',
        'question': question,
        'options_count': len(options)
    }))
    
    try:
        # Simulate analysis steps
        steps = [
            'Analyzing question context...',
            f'Evaluating {len(options)} options...',
            'Checking against global laws...',
            'Calculating risk levels...',
            'Generating recommendation...'
        ]
        
        for step in steps:
            await websocket.send(json.dumps({
                'type': 'analysis',
                'step': step
            }))
            await asyncio.sleep(0.2)
        
        # Get actual decision
        result = brain.decide(question, options)
        
        await websocket.send(json.dumps({
            'type': 'complete',
            'approved': result.approved,
            'risk_level': result.risk_level,
            'reasoning': result.reasoning[:300]
        }))
        
    except Exception as e:
        await websocket.send(json.dumps({
            'type': 'error',
            'message': str(e)
        }))


async def main():
    """Start WebSocket server."""
    async with websockets.serve(handler, "0.0.0.0", 8765):
        logger.info("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
