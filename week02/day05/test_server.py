import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class TestHandler(BaseHTTPRequestHandler):
    def send_html(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/final":
            self.send_html(
                """
                <html>
                    <body>
                        <a href="/ok-200">OK 200</a>
                        <a href="/ok-204">OK 204</a>
                        <a href="/redirect-ok">Redirect to OK</a>

                        <a href="/head-401-get-200">HEAD 401 to GET 200</a>
                        <a href="/head-403-get-204">HEAD 403 to GET 204</a>
                        <a href="/large-file">Streaming large file</a>

                        <a href="/dead-404">HEAD 404</a>
                        <a href="/head-405-get-404">HEAD 405 to GET 404</a>

                        <a href="/unavailable-503">HEAD 503</a>
                        <a href="/head-429-get-503">HEAD 429 to GET 503</a>

                        <a href="/head-500-get-429">HEAD 500 to GET 429</a>
                        <a href="/head-403-get-500">HEAD 403 to GET 500</a>

                        <a href="/ok-200">Duplicate OK</a>
                        <a href="/ok-200#top">OK fragment</a>
                    </body>
                </html>
                """
            )

        elif self.path == "/ok-200":
            self.send_response(200)
            self.end_headers()

        elif self.path == "/ok-204":
            self.send_response(204)
            self.end_headers()

        elif self.path == "/redirect-ok":
            self.send_response(302)
            self.send_header("Location", "/ok-200")
            self.end_headers()

        elif self.path == "/head-401-get-200":
            self.send_response(200)
            self.end_headers()

        elif self.path == "/head-403-get-204":
            self.send_response(204)
            self.end_headers()

        elif self.path == "/large-file":
            file_size = 5 * 1024 * 1024
            chunk = b"x" * 65536
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()

            try:
                sent = 0
                while sent < file_size:
                    self.wfile.write(chunk)
                    self.wfile.flush()
                    sent += len(chunk)
                    time.sleep(0.01)
            except (BrokenPipeError, ConnectionResetError):
                pass

        elif self.path in ["/dead-404", "/head-405-get-404"]:
            self.send_response(404)
            self.end_headers()

        elif self.path in ["/unavailable-503", "/head-429-get-503"]:
            self.send_response(503)
            self.end_headers()

        elif self.path == "/head-500-get-429":
            self.send_response(429)
            self.end_headers()

        elif self.path == "/head-403-get-500":
            self.send_response(500)
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        if self.path in ["/final", "/ok-200"]:
            self.send_response(200)

        elif self.path == "/ok-204":
            self.send_response(204)

        elif self.path == "/redirect-ok":
            self.send_response(302)
            self.send_header("Location", "/ok-200")

        elif self.path == "/head-401-get-200":
            self.send_response(401)

        elif self.path in ["/head-403-get-204", "/large-file", "/head-403-get-500"]:
            self.send_response(403)

        elif self.path == "/head-405-get-404":
            self.send_response(405)

        elif self.path == "/head-429-get-503":
            self.send_response(429)

        elif self.path == "/head-500-get-429":
            self.send_response(500)

        elif self.path == "/dead-404":
            self.send_response(404)

        elif self.path == "/unavailable-503":
            self.send_response(503)

        else:
            self.send_response(404)

        self.end_headers()

    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 8000), TestHandler)
print("Test server running at http://127.0.0.1:8000")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nTest server stopped.")
finally:
    server.server_close()


