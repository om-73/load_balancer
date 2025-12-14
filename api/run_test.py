from http.server import BaseHTTPRequestHandler
import json
import time
import urllib.request
import concurrent.futures

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len)

        try:
            data = json.loads(post_body)
            url = data.get("url", "")
            # Verify URL
            if not url or not url.startswith("http"):
                 raise ValueError("Invalid URL: Must start with http:// or https://")

            # Limits for Vercel (Serverless has timeouts/CPU limits)
            # We will run a "Lightweight" check: 20 requests
            TOTAL_REQUESTS = 20
            CONCURRENCY = 5 

            start_time = time.time()
            success_count = 0
            fail_count = 0

            # Define the single request function
            def fetch_url(target_url):
                try:
                    # Timeout of 2s to fail fast
                    with urllib.request.urlopen(target_url, timeout=2) as conn:
                        return conn.status < 400
                except:
                    return False

            # Run concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
                futures = [executor.submit(fetch_url, url) for _ in range(TOTAL_REQUESTS)]
                
                for future in concurrent.futures.as_completed(futures):
                    if future.result():
                        success_count += 1
                    else:
                        fail_count += 1

            duration = time.time() - start_time
            rps = TOTAL_REQUESTS / duration if duration > 0 else 0

            result = {
                "duration": round(duration, 2),
                "rps": round(rps, 2),
                "success": success_count,
                "failed": fail_count
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
