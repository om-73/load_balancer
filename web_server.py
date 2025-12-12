import http.server
import socketserver
import json
import os
import socket
from load_generator import LoadGenerator

PORT = 8000

def send_reset_signal():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(b"RESET", ("localhost", 9999))
    except:
        pass

class LoadTestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html by default
        if self.path == "/":
            self.path = "index.html"
            send_reset_signal()
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/run-test":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                url = data.get("url", "http://localhost:8080")
                requests = int(data.get("requests", 100))
                concurrency = int(data.get("concurrency", 10))

                print(f"Triggering Load Test: {requests} to {url}")
                
                # Run the load generator
                generator = LoadGenerator(url, requests, concurrency)
                result = generator.run()
                
                # Respond
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_error(404)

print(f"🌍 Web Interface running at http://localhost:{PORT}")
print(f"Open your browser to start valid testing!")

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReusableTCPServer(("", PORT), LoadTestHandler) as httpd:
    httpd.serve_forever()
