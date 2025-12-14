from http.server import BaseHTTPRequestHandler
import json
import random
import time

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Simulate processing time
        time.sleep(1)

        # Generate mock result
        result = {
            "duration": 5.0,
            "rps": round(random.uniform(20.0, 100.0), 2),
            "success": random.randint(900, 1000),
            "failed": 0
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
