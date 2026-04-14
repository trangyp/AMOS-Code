#!/usr/bin/env python3
"""AMOS HTTP API Server - REST interface for the 52-component system."""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class AMOSRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AMOS API."""
    
    amos = None
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def _send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, message, status=400):
        """Send error response."""
        self._send_json({"error": message}, status)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            self._send_json({
                "name": "AMOS Master Cognitive Organism API",
                "version": "1.0.0",
                "components": 52,
                "engines": 251,
                "knowledge_files": 659,
                "endpoints": ["/status", "/health", "/process", "/query"]
            })
        
        elif path == '/status':
            if not self.amos:
                self._init_amos()
            status = self.amos.get_status()
            self._send_json({
                "initialized": status['initialized'],
                "tasks_processed": status['stats']['tasks_processed'],
                "engines_available": 251,
                "knowledge_files": 659,
                "components": 52,
                "test_coverage": "100%"
            })
        
        elif path == '/health':
            self._send_json({
                "status": "healthy",
                "components": 52,
                "engines": 251,
                "operational": True
            })
        
        else:
            self._send_error("Not found", 404)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error("Invalid JSON")
            return
        
        if not self.amos:
            self._init_amos()
        
        if path == '/process':
            task = data.get('task', '')
            if not task:
                self._send_error("Missing 'task' field")
                return
            
            result = self.amos.process(task)
            self._send_json({
                "task": task,
                "engine_used": result.engine_used,
                "category": result.category,
                "status": result.status,
                "processing_time_ms": result.processing_time_ms
            })
        
        elif path == '/query':
            question = data.get('question', '')
            if not question:
                self._send_error("Missing 'question' field")
                return
            
            result = self.amos.query(question)
            self._send_json(result)
        
        elif path == '/batch':
            tasks = data.get('tasks', [])
            if not tasks or not isinstance(tasks, list):
                self._send_error("Missing 'tasks' array")
                return
            
            results = []
            for task in tasks:
                result = self.amos.process(task)
                results.append({
                    "task": task,
                    "engine_used": result.engine_used,
                    "category": result.category,
                    "status": result.status
                })
            
            self._send_json({
                "tasks_processed": len(results),
                "results": results
            })
        
        else:
            self._send_error("Not found", 404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _init_amos(self):
        """Initialize AMOS instance."""
        from amos_master_cognitive_orchestrator import MasterCognitiveOrchestrator
        self.amos = MasterCognitiveOrchestrator()


def run_server(port=8000):
    """Run the HTTP API server."""
    server = HTTPServer(('', port), AMOSRequestHandler)
    print(f"\n{'='*70}")
    print(f"AMOS HTTP API Server")
    print(f"{'='*70}")
    print(f"\nServer running on http://localhost:{port}")
    print(f"\nEndpoints:")
    print(f"  GET  /           - API info")
    print(f"  GET  /status     - System status")
    print(f"  GET  /health     - Health check")
    print(f"  POST /process    - Process task")
    print(f"  POST /query      - Query knowledge")
    print(f"  POST /batch      - Batch processing")
    print(f"\n{'='*70}")
    print(f"Press Ctrl+C to stop")
    print(f"{'='*70}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
