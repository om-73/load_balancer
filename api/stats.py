from http.server import BaseHTTPRequestHandler
import json
import random
import time
from datetime import datetime

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Current Server Time
        now = datetime.now().strftime("%H:%M:%S")

        # Mock Logs
        # Vercel Environment - Stateless
        # We cannot access local logs here.
        # Return empty state so the UI prompts for Custom Source.
        
        stats = {
            "total_requests": 0,
            "success_requests": 0,
            "failed_requests": 0,
            "rps": 0.0,
            "backend_counts": {},
            "recent_logs": [],
            "server_time": now
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode('utf-8'))
