#!/bin/env python3

from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys

listen_address = ("localhost", 8080)

@dataclass
class Redirect:
    target_url: str
    status_code: int


class MyHandler(BaseHTTPRequestHandler):

    redirects = {
        "/one": Redirect("/two", 307),
        "/two": Redirect("/three", 307),
        "/three": Redirect("/four", 307),
        "/four": Redirect("/echo", 307),
    }

    def handle_request(self):
        # Log the request and its body.
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        sys.stdout.write(f">>> Request:\n{self.command} {self.path}\n")
        sys.stdout.write(body.decode("utf-8") + "\n\n")

        # Handle requests for index.
        if self.path == "/":
            sys.stdout.write("<<< Response:\n200 OK\n\n")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        # Handle redirects if the path is in the redirects dictionary.
        if self.path in self.redirects:
            redirect = self.redirects[self.path]
            sys.stdout.write(
                f"<<< Response:\n{redirect.status_code} {HTTPStatus(redirect.status_code).phrase}\n"
            )
            sys.stdout.write(f"Location: {redirect.target_url}\n\n")
            self.send_response(redirect.status_code)
            self.send_header("Location", redirect.target_url)
            self.end_headers()
            return

        # Handle echo request by returning the request body.
        if self.path == "/echo":
            sys.stdout.write(f"<<< Response:\n200 OK\n{body.decode('utf-8')}\n\n")
            self.send_response(200)
            self.send_header(
                "Content-Type", self.headers.get("Content-Type", "text/plain")
            )
            self.end_headers()
            self.wfile.write(body)
            return

        # Not found.
        sys.stdout.write("<<< Response:\n\n404 Not Found\n")
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"404 Not Found")

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    sys.stdout.write(f"Starting server on {listen_address}\n")
    server = HTTPServer(listen_address, MyHandler)
    server.serve_forever()
