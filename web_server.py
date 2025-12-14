import http.server
import socketserver
import json
import os
import subprocess
import socket
import re
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
        
        if self.path == "/stats":
            stats = self.get_stats()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def get_stats(self):
        # Default stats
        stats = {
            "total_requests": 0,
            "success_requests": 0,
            "failed_requests": 0,
            "rps": 0.0,
            "backend_counts": {}
        }
        
        log_file = "lb.log"
        if not os.path.exists(log_file):
            return stats

        try:
            # Read last 1000 lines or sufficient amount to get current state
            # For simplicity, we can read the whole file if small, or use tail logic. 
            # Since this is a demo, let's just read the file.
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Simple parsing similar to visualizer.py
            total = 0
            success = 0
            failed = 0
            counts = {}
            
            # We can re-parse everything or just grep for "Stats" lines if valid.
            # But the terminal visualizer parses stream.
            # Let's do a quick pass.
            
            for line in lines:
                if "Forwarding request to localhost:" in line:
                    match = re.search(r"Forwarding request to localhost:(\d+)", line)
                    if match:
                        port = match.group(1)
                        counts[port] = counts.get(port, 0) + 1
                        total += 1
                        success += 1
                elif "No backend servers available" in line or "Error forwarding" in line:
                    failed += 1
                    total += 1
            
            # Calculate RPS (very rough estimate based on file update time? or just 0 for now)
            # visualizer.py calculates it live.
            # For this web demo, valid RPS is hard without keeping state in memory.
            # We will just verify counts for now.
            
            stats["total_requests"] = total
            stats["success_requests"] = success
            stats["failed_requests"] = failed
            stats["backend_counts"] = counts
            
        except Exception as e:
            print(f"Error parsing log: {e}")
            
        return stats

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
        elif self.path == "/scan-ports":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                host_url = data.get("host", "google.com")
                
                # Run the Java port scanner
                # We need to capture stdout
                cmd = ["java", "-cp", "src/main/java", "com.loadbalancer.PortScanner", host_url]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Scanner failed: {stderr}")
                    
                # The visualizer expects JSON or text. Let's return the raw output for now or parse it.
                # The Java tool prints lines like "✅ Port 80 is OPEN"
                # We can just return the raw text to be displayed.
                
                response_data = {
                    "output": stdout
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())

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
