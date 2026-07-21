from __future__ import annotations

import json
import socket
import sys
import threading
import webbrowser
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from anki import scheduler, store

HTML_PATH = Path(__file__).with_name("index.html")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="A really simple Anki-style flashcard app.")
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


def load_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


class AnkiHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            return None
        if length <= 0:
            return None
        try:
            data = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            return None
        return data if isinstance(data, dict) else None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/":
            self._send_html(load_html())
            return

        if parsed.path == "/api/decks":
            self._send_json(store.list_decks())
            return

        if parsed.path == "/api/cards":
            self._send_json(store.list_cards(query.get("deck", [""])[0]))
            return

        if parsed.path == "/api/study":
            deck_id = query.get("deck", [""])[0]
            include_all = query.get("all", [""])[0] == "1"
            self._send_json(store.study(deck_id, include_all))
            return

        self.send_error(404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        body = self._read_json()
        if body is None:
            self._send_json({"error": "invalid JSON body"}, status=400)
            return

        if parsed.path == "/api/decks":
            name = str(body.get("name", "")).strip()
            if not name:
                self._send_json({"error": "name is required"}, status=400)
                return
            self._send_json(store.add_deck(name))
            return

        if parsed.path == "/api/cards":
            front = str(body.get("front", "")).strip()
            back = str(body.get("back", "")).strip()
            hint = str(body.get("hint", "")).strip()
            if not front or not back:
                self._send_json({"error": "front and back are required"}, status=400)
                return
            card = store.add_card(str(body.get("deck_id", "")), front, back, hint)
            if card is None:
                self._send_json({"error": "deck not found"}, status=404)
                return
            self._send_json(card)
            return

        if parsed.path == "/api/review":
            rating = str(body.get("rating", ""))
            if rating not in scheduler.RATINGS:
                self._send_json({"error": "invalid rating"}, status=400)
                return
            ok = store.apply_review(
                str(body.get("deck_id", "")), str(body.get("card_id", "")), rating
            )
            self._send_json({"ok": ok}, status=200 if ok else 404)
            return

        self.send_error(404)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/api/decks":
            store.delete_deck(query.get("id", [""])[0])
            self._send_json({"ok": True})
            return

        if parsed.path == "/api/cards":
            store.delete_card(query.get("deck", [""])[0], query.get("id", [""])[0])
            self._send_json({"ok": True})
            return

        self.send_error(404)

    def log_message(self, format: str, *args) -> None:
        return


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)

    port = find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), AnkiHandler)
    url = f"http://127.0.0.1:{port}"

    if not args.no_browser:
        threading.Timer(0.2, lambda: webbrowser.open(url)).start()

    print(f"Serving anki at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
