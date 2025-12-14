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
        logs = [
            f"➡️ Forwarding request to localhost:908{random.randint(1,4)} [Health: UP]",
            f"➡️ Forwarding request to localhost:908{random.randint(1,4)} [Health: UP]",
            f"⚠️ Scale Up Triggered: High RPS detected!",
            f"✅ Health Check Passed: Backend 9081",
            f"➡️ Forwarding request to localhost:908{random.randint(1,4)} [Health: UP]"
        ]
        
        # Shuffle/Randomize logs
        recent_logs = random.sample(logs, 3)

        # Generate mock data consistent with index.html expectations
        stats = {
            "total_requests": random.randint(10000, 50000),
            "success_requests": random.randint(9900, 49900),
            "failed_requests": random.randint(0, 50),
            "rps": round(random.uniform(15.0, 120.0), 1),
            "backend_counts": {
                "9081": random.randint(3000, 5000),
                "9082": random.randint(3000, 5000),
                "9083": random.randint(3000, 5000),
                "9084": random.randint(0, 1000) # Simulating scaling
            },
            "recent_logs": recent_logs,
            "server_time": now
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode('utf-8'))
