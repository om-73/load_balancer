```
import http.server
import socketserver
import json
import os
import subprocess
import socket
import re
from load_generator import LoadGenerator

import time

# Render provides the PORT environment variable
PORT = int(os.environ.get("PORT", 8000))
SERVICE_PORT = 9081 # Not used directly but good to track

# Global state for RPS calculation
last_check_time = time.time()
last_total_requests = 0

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
        
        if self.path.startswith("/stats"):
            stats = self.get_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.send_header('Access-Control-Allow-Private-Network', 'true')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

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
            print(f"Debug: {log_file} not found")
            return stats

        try:
            # Read last 1000 lines or sufficient amount to get current state
            # For simplicity, we can read the whole file if small, or use tail logic. 
            # Since this is a demo, let's just read the file.
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # print(f"Debug: Read {len(lines)} lines from log")
            
            # Simple parsing similar to visualizer.py
            total = 0
            success = 0
            failed = 0
            counts = {}
            recent_logs = []
            
            # Global RPS state
            global last_check_time, last_total_requests
            
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
                    recent_logs.append("❌ " + line.strip())
                elif "Forwarding request" in line:
                    # Optional: Add forwarding logs too, maybe just the last few
                    # recent_logs.append("➡️ " + line.strip())
                    pass

            # Capture last 10 "Forwarding" or important lines for the visualizer
            # Re-iterate or just capture during the first pass?
            # Let's just grab the last 10 meaningful lines from the file end.
            
            meaningful_logs = []
            for line in reversed(lines):
                line = line.strip()
                if not line: continue
                if "Forwarding request" in line:
                    meaningful_logs.append("➡️ " + line)
                elif "status changed" in line:
                    meaningful_logs.append("⚠️ " + line)
                elif "No backend" in line:
                    meaningful_logs.append("❌ NO BACKENDS AVAILABLE")
                
                if len(meaningful_logs) >= 10:
                    break
            
            recent_logs = meaningful_logs # They are in reverse order
            # Reverse back to normal chronological order
            # But normally visualizer shows newest at bottom? Or top?
            # Let's send them chronological
            # recent_logs.reverse() -> No, let's keep newest at top for web or bottom?
            # Let's send newest first (index 0) for easy display at top? 
            # Or newest last? Terminal scrolls down. Web console usually new at bottom.
            # So let's reverse them to be chronological [Oldest ... Newest]
            recent_logs.reverse()
            
            # Calculate RPS
            current_time = time.time()
            time_diff = current_time - last_check_time
            
            # Only calculate if enough time has passed (e.g., > 0.5s) and we have new data
            # OR if this is the first real check after some time.
            # But the frontend polls every 1s.
            
            if time_diff > 0:
                # Delta requests
                delta_reqs = total - last_total_requests
                # Only update RPS if delta is non-negative (log rotation/reset might cause negative)
                if delta_reqs >= 0:
                    stats["rps"] = delta_reqs / time_diff
                else:
                    stats["rps"] = 0.0
            
            # Update state for next call
            last_check_time = current_time
            last_total_requests = total
            
            stats["total_requests"] = total
            stats["success_requests"] = success
            stats["failed_requests"] = failed
            stats["backend_counts"] = counts
            stats["recent_logs"] = recent_logs
            stats["server_time"] = time.strftime("%H:%M:%S")
            
            # print(f"Debug: Stats parsed: {stats}")
            
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

                # Safety: Cap concurrency to avoid "can't start new thread" errors
                MAX_CONCURRENCY = 200
                if concurrency > MAX_CONCURRENCY:
                    print(f"⚠️ Capping concurrency from {concurrency} to {MAX_CONCURRENCY}")
                    concurrency = MAX_CONCURRENCY

                print(f"Triggering Load Test: {requests} to {url} with {concurrency} threads")
                
                # Run the load generator
                generator = LoadGenerator(url, requests, concurrency)
                result = generator.run()
                
                # Respond
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
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
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/upload-strategy":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                java_code = data.get("code")
                if not java_code:
                    raise Exception("No 'code' field in payload")
                
                # 1. Save File
                src_path = "src/main/java/com/loadbalancer/CustomStrategy.java"
                with open(src_path, "w") as f:
                    f.write(java_code)
                    
                # 2. Recompile
                print("Compiling CustomStrategy...")
                result = subprocess.run(["javac", "-d", "bin", src_path, "-cp", "src/main/java"], capture_output=True, text=True)
                if result.returncode != 0:
                     raise Exception("Compilation Failed:\n" + result.stderr)
                
                # 3. Restart Load Balancer
                subprocess.Popen(["./restart_lb.sh"])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "Strategy Uploaded & Compiling. Restarting Service..."}).encode())

            except Exception as e:
                with open("debug_upload.log", "a") as f:
                    f.write(f"Error: {e}\n")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/network-ip":
            try:
                # Find local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Doesn't actually connect, just determines route
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps({"ip": local_ip}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Private-Network', 'true')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "ip": "127.0.0.1"}).encode())

        else:
            self.send_error(404)

print(f"🌍 Web Interface running at http://localhost:{PORT}")
print(f"Open your browser to start valid testing!")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

print(f"🌍 Web Interface running at http://localhost:{PORT}")
print(f"Open your browser to start valid testing!")

with ThreadedTCPServer(("", PORT), LoadTestHandler) as httpd:
    httpd.serve_forever()
