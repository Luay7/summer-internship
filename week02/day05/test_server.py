from http.server import BaseHTTPRequestHandler, HTTPServer


class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Previous v0.5.0 test page
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(
                b"""
                <html>
                    <body>
                        <a href="/working">Working Link</a>
                        <a href="/working">Duplicate Working Link</a>
                        <a href="/working#section-one">Working Fragment One</a>
                        <a href="/working#section-two">Working Fragment Two</a>

                        <a href="/second">Second Link</a>
                        <a href="/second">Duplicate Second Link</a>

                        <a href="#top">Main Page Fragment</a>
                    </body>
                </html>
                """
            )

        # New v0.6.0 test page
        elif self.path == "/v06":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(
                b"""
                <html>
                    <body>
                        <a href="/head-401">HEAD 401 Fallback</a>
                        <a href="/head-429">HEAD 429 Fallback</a>
                        <a href="/large-file">Streaming GET Fallback</a>
                    </body>
                </html>
                """
            )

        # Previous test cases
        elif self.path == "/working":
            self.send_response(200)
            self.end_headers()

        elif self.path == "/second":
            self.send_response(200)
            self.end_headers()

        elif self.path == "/404":
            self.send_response(404)
            self.end_headers()

        elif self.path == "/503":
            self.send_response(503)
            self.end_headers()

        # New fallback test cases
        elif self.path == "/head-401":
            self.send_response(200)
            self.end_headers()

        elif self.path == "/head-429":
            self.send_response(200)
            self.end_headers()

        # New streaming GET test case
        elif self.path == "/large-file":
            file_size = 1024 * 1024

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()

            try:
                self.wfile.write(b"x" * file_size)
            except (BrokenPipeError, ConnectionResetError):
                pass

        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        # Previous test cases
        if self.path in ["/", "/v06", "/working", "/second"]:
            self.send_response(200)

        elif self.path == "/404":
            self.send_response(404)

        elif self.path == "/503":
            self.send_response(503)

        # New fallback cases
        elif self.path == "/head-401":
            self.send_response(401)

        elif self.path == "/head-429":
            self.send_response(429)

        # Force the large file to use GET fallback
        elif self.path == "/large-file":
            self.send_response(403)

        else:
            self.send_response(404)

        self.end_headers()

    def log_message(self, format, *args):
        pass


server = HTTPServer(("127.0.0.1", 8000), TestHandler)

print("Test server running at http://127.0.0.1:8000")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nTest server stopped.")
finally:
    server.server_close()
