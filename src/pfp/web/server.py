"""HTTP server for the PFP web application."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pfp.cli import load_portfolio
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def serve(movements_file: Path, host: str = "127.0.0.1", port: int = 8000) -> None:
    portfolio = load_portfolio(movements_file)
    report = PortfolioReport.from_portfolio(portfolio)
    app = WebApp(report)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            path = self.path.split("?", 1)[0]
            try:
                body = app.render(path).encode("utf-8")
            except KeyError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"PFP Dashboard: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PFP web dashboard")
    parser.add_argument("movements_file")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(Path(args.movements_file), args.host, args.port)


if __name__ == "__main__":
    main()
