#!/usr/bin/env python3
"""Simple HTTP server to demonstrate brain is working"""
import sys
sys.path.insert(0, '.')

from http.server import HTTPServer, BaseHTTPRequestHandler

class BrainHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        try:
            from amos_brain import get_super_brain
            b = get_super_brain()
            b.initialize()
            s = b.get_state()
            
            html = f"""
            <h1>AMOS Brain Status</h1>
            <p>Status: {s.status}</p>
            <p>Health: {s.health_score}</p>
            <p>Active Kernels: {len(s.active_kernels)}</p>
            <p>Brain ID: {b.brain_id[:8]}...</p>
            <p><strong>BRAIN IS OPERATIONAL</strong></p>
            """
        except Exception as e:
            html = f"<h1>Error</h1><pre>{e}</pre>"
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8765), BrainHandler)
    print("Brain server running at http://localhost:8765")
    server.serve_forever()
