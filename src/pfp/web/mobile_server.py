"""Convenience launcher for running PFP on a local network."""

from __future__ import annotations

import argparse
from http.client import RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pfp.web.server import serve


PACKAGE_DIR = Path(__file__).resolve().parent
MANIFEST_FILE = PACKAGE_DIR / "manifest.webmanifest"
SERVICE_WORKER_FILE = PACKAGE_DIR / "sw.js"


def _inject_pwa(html: bytes) -> bytes:
    text = html.decode("utf-8")
    text = text.replace(
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<link rel="manifest" href="/manifest.webmanifest">'
        '<meta name="theme-color" content="#172033">',
        1,
    )
    text = text.replace(
        "</body>",
        '<script>if ("serviceWorker" in navigator) { window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js")); }</script></body>',
        1,
    )
    return text.encode("utf-8")


def _serve_file(handler: BaseHTTPRequestHandler, path: Path, content_type: str) -> None:
    body = path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PFP web app for access from a mobile device")
    parser.add_argument("movements_file")
    parser.add_argument("--investments-file", default="data/imports/investments.csv")
    parser.add_argument("--sales-file", default="data/imports/sales.csv")
    parser.add_argument("--assets-file", default="data/assets.csv")
    parser.add_argument("--reconciliations-file", default="data/accounts/reconciliation_history.csv")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    backend_port = args.port + 1
    Thread(
        target=serve,
        kwargs={
            "movements_file": Path(args.movements_file),
            "host": "127.0.0.1",
            "port": backend_port,
            "investments_file": Path(args.investments_file),
            "sales_file": Path(args.sales_file),
            "assets_file": Path(args.assets_file),
            "reconciliations_file": Path(args.reconciliations_file),
        },
        daemon=True,
    ).start()

    class MobileHandler(BaseHTTPRequestHandler):
        def _proxy(self) -> None:
            body = None
            if self.command == "POST":
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
            request = Request(
                f"http://127.0.0.1:{backend_port}{self.path}",
                data=body,
                method=self.command,
            )
            for name in ("Content-Type", "Accept"):
                value = self.headers.get(name)
                if value:
                    request.add_header(name, value)
            try:
                with urlopen(request, timeout=30) as response:
                    response_body = response.read()
                    content_type = response.headers.get("Content-Type", "text/plain; charset=utf-8")
                    status = response.status
            except HTTPError as exc:
                response_body = exc.read()
                content_type = exc.headers.get("Content-Type", "text/plain; charset=utf-8")
                status = exc.code
            except (URLError, RemoteDisconnected) as exc:
                self.send_error(502, f"No se puede conectar con PFP: {exc}")
                return

            if content_type.startswith("text/html"):
                response_body = _inject_pwa(response_body)

            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

        def do_GET(self) -> None:
            if self.path == "/manifest.webmanifest":
                _serve_file(self, MANIFEST_FILE, "application/manifest+json; charset=utf-8")
                return
            if self.path == "/sw.js":
                _serve_file(self, SERVICE_WORKER_FILE, "application/javascript; charset=utf-8")
                return
            self._proxy()

        def do_POST(self) -> None:
            self._proxy()

        def log_message(self, format: str, *args) -> None:
            return

    ThreadingHTTPServer(("0.0.0.0", args.port), MobileHandler).serve_forever()


if __name__ == "__main__":
    main()
