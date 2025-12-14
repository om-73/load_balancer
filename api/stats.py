from http.server import BaseHTTPRequestHandler
import json
import random

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Generate mock data for Vercel demo
        stats = {
            "total_requests": random.randint(1000, 5000),
            "success_requests": random.randint(900, 4900),
            "failed_requests": random.randint(0, 50),
            "rps": round(random.uniform(5.0, 50.0), 1),
            "backend_counts": {
                "9081": random.randint(300, 1500),
                "9082": random.randint(300, 1500),
                "9083": random.randint(300, 1500)
            }
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode('utf-8'))
