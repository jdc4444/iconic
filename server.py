#!/usr/bin/env python3
"""Tiny static server with a /prefs endpoint for reading/writing preferences to disk."""
import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

PREFS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prefs.json')

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/prefs':
            try:
                with open(PREFS_FILE, 'r') as f:
                    data = f.read()
            except FileNotFoundError:
                data = '{}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data.encode())
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/prefs':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                parsed = json.loads(body)
                with open(PREFS_FILE, 'w') as f:
                    json.dump(parsed, f, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
            return
        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # silent

port = int(sys.argv[1]) if len(sys.argv) > 1 else 3480
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f'Iconic serving on http://localhost:{port}')
HTTPServer(('', port), Handler).serve_forever()
