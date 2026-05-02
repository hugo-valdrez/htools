from __future__ import annotations

import json
import socket
import threading
import webbrowser
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import polars as pl

from data_visualizer.abstract.base_data_pager import BaseDataPager
from data_visualizer.abstract.csv_data_pager import CSVDataPager
from data_visualizer.abstract.parquet_data_pager import ParquetDataPager

PAGE_SIZE = 50
SUPPORTED_FORMATS = {".csv", ".parquet"}
HTML_PATH = Path(__file__).with_name("index.html")


def create_pager(file_path: Path) -> BaseDataPager:
    suffix = file_path.suffix.lower()
    if suffix == ".parquet":
        return ParquetDataPager(file_path)
    if suffix == ".csv":
        return CSVDataPager(file_path)

    supported = ", ".join(sorted(SUPPORTED_FORMATS))
    raise ValueError(f"Unsupported file format: {suffix}. Supported: {supported}")


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Quickly inspect CSV and parquet files.")
    parser.add_argument("input_file", type=Path, help="Path to the input data file.")
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


def serialize_frame(frame: pl.DataFrame) -> list[dict[str, object]]:
    return frame.to_dicts()


def load_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def make_handler(pager: BaseDataPager):
    class VisualizerHandler(BaseHTTPRequestHandler):
        def _send_json(self, payload: dict[str, object]) -> None:
            body = json.dumps(payload, default=str).encode("utf-8")
            self.send_response(200)
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

        def do_GET(self) -> None:
            parsed = urlparse(self.path)

            if parsed.path == "/":
                self._send_html(load_html())
                return

            if parsed.path == "/api/meta":
                self._send_json(
                    {
                        "file_name": pager.file_path.name,
                        "format": pager.format_name,
                        "columns": pager.columns(),
                        "total_rows": pager.total_rows(),
                        "page_size": PAGE_SIZE,
                    }
                )
                return

            if parsed.path == "/api/page":
                query = parse_qs(parsed.query)
                index = int(query.get("index", ["0"])[0])
                if index < 0:
                    index = 0

                frame = pager.page(index, PAGE_SIZE)
                self._send_json({"page_index": index, "rows": serialize_frame(frame)})
                return

            self.send_error(404)

        def log_message(self, format: str, *args) -> None:
            return

    return VisualizerHandler


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    file_path = args.input_file.resolve()
    pager = create_pager(file_path)

    port = find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(pager))
    url = f"http://127.0.0.1:{port}"

    if not args.no_browser:
        threading.Timer(0.2, lambda: webbrowser.open(url)).start()

    print(f"Serving {file_path.name} at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
