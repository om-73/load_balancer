from http.server import BaseHTTPRequestHandler
import json
import socket
import threading
import concurrent.futures
import time
from urllib.parse import urlparse

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len)

        try:
            data = json.loads(post_body)
            host_url = data.get("host", "")
            
            if not host_url:
                raise ValueError("Host is required")

            # Extract Hostname
            host = self.extract_host(host_url)
            
            # Scan Ports
            results = self.scan_common_ports(host)
            
            # Format Output matching the Java tool's style for the frontend
            output_lines = [f"Starting scan for {host}...", f"Scanning common ports..."]
            for port in results:
                output_lines.append(f"✅ Port {port} is OPEN")
            
            # Simple duration mock or calculation
            output_lines.append("Scan completed.")
            
            response_data = {
                "output": "\n".join(output_lines)
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def extract_host(self, url):
        if "://" not in url:
            return url
        try:
            parsed = urlparse(url)
            return parsed.hostname or url
        except:
            return url

    def scan_common_ports(self, host):
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 6379, 8080, 8443]
        open_ports = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_port = {executor.submit(self.check_port, host, port): port for port in common_ports}
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    is_open = future.result()
                    if is_open:
                        open_ports.append(port)
                except:
                    pass
        
        return sorted(open_ports)

    def check_port(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5) # 500ms timeout
                s.connect((host, port))
                return True
        except:
            return False
