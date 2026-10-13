from __future__ import annotations

import socket
import sys
import threading
import webbrowser
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

HTML_PATH = Path(__file__).with_name("index.html")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="HEMA footwork caller: voices random forward/backward calls."
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the local server without opening a browser tab.",
    )
    return parser


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class FootworkHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if urlparse(self.path).path != "/":
            self.send_error(404)
            return
        body = HTML_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)

    port = find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), FootworkHandler)
    url = f"http://127.0.0.1:{port}"

    if not args.no_browser:
        threading.Timer(0.2, lambda: webbrowser.open(url)).start()

    print(f"Serving footwork at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
