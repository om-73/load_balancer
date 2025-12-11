import http.server
import socketserver
import sys

PORT = int(sys.argv[1])

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        response = f"Hello from Backend Server on Port {PORT}\n"
        self.wfile.write(response.encode())

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
