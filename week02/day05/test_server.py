from http.server import BaseHTTPRequestHandler, HTTPServer


class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
                <html>
                    <body>
                        <a href="/working">Working Link</a>
                    </body>
                </html>
                """
            )

        elif self.path == "/working":
            self.send_response(200)
            self.end_headers()

        elif self.path == "/404":
            self.send_response(404)
            self.end_headers()

        elif self.path == "/503":
            self.send_response(503)
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        if self.path in ["/", "/working"]:
            self.send_response(200)
        elif self.path == "/404":
            self.send_response(404)
        elif self.path == "/503":
            self.send_response(503)
        else:
            self.send_response(404)

        self.end_headers()

    def log_message(self, format, *args):
        # Prevent test-server logs from cluttering the terminal.
        pass


server = HTTPServer(("127.0.0.1", 8000), TestHandler)

print("Test server running at http://127.0.0.1:8000")
print("Press Ctrl+C to stop it.")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nTest server stopped.")
finally:
    server.server_close()
