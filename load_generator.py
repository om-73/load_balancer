import argparse
import urllib.request
import concurrent.futures
import time
import sys

def send_request(url, request_id):
    try:
        start = time.time()
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.status
        duration = time.time() - start
        return (True, status, duration)
    except Exception as e:
        return (False, str(e), 0)

class LoadGenerator:
    def __init__(self, url, requests_count, concurrency):
        self.url = url
        self.requests_count = requests_count
        self.concurrency = concurrency

    def run(self):
        print(f"🚀 Starting Load Test: {self.requests_count} requests to {self.url} with {self.concurrency} threads.")
        
        success_count = 0
        fail_count = 0
        total_time_start = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = [executor.submit(send_request, self.url, i) for i in range(self.requests_count)]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                success, status, duration = future.result()
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                
                # Simple progress bar logic (only if running as script?)
                # We'll skip TUI progress bar when called from API to avoid log spam, 
                # or we could keep it. Let's keep it simple.
        
        total_duration = time.time() - total_time_start
        rps = self.requests_count / total_duration if total_duration > 0 else 0
        
        return {
            "success": success_count,
            "failed": fail_count,
            "duration": total_duration,
            "rps": rps
        }

def main():
    parser = argparse.ArgumentParser(description="Load Generator for Load Balancer")
    parser.add_argument("--url", default="http://localhost:8080", help="Target URL")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent threads")
    args = parser.parse_args()

    generator = LoadGenerator(args.url, args.requests, args.concurrency)
    result = generator.run()

    print("\n\n=== Test Complete ===")
    print(f"✅ Success: {result['success']}")
    print(f"❌ Failed:  {result['failed']}")
    print(f"⏱️  Duration: {result['duration']:.2f}s")
    print(f"📊 RPS:      {result['rps']:.2f}")

if __name__ == "__main__":
    main()
