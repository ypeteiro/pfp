"""HTTP server for the PFP web application."""

from __future__ import annotations

import argparse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pfp.cli import DEFAULT_INVESTMENTS_FILE, DEFAULT_SALES_FILE
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.market.price_provider import CompositePriceProvider
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def dashboard_html(report: PortfolioReport) -> str:
    """Render the legacy dashboard entry point used by the existing tests."""
    return WebApp(report).render("/")


def build_web_report(
    movements_file: Path,
    investments_file: Path | None = None,
    sales_file: Path | None = None,
    price_provider=None,
) -> PortfolioReport:
    """Build the same valued portfolio used by the CLI for the web UI."""
    investments_file = investments_file or Path(DEFAULT_INVESTMENTS_FILE)
    sales_file = sales_file or Path(DEFAULT_SALES_FILE)
    price_provider = price_provider or CompositePriceProvider()

    movements = TradeRepublicImporter().load(movements_file)
    investments = InvestmentRepository(investments_file).load()
    sales = SaleRepository(sales_file).load()
    engine = PortfolioEngine()

    portfolio = engine.build(movements, investments=investments, sales=sales)
    prices = price_provider.get_prices(list(portfolio.positions.keys()))
    price_consulted_at = datetime.now().astimezone()
    portfolio = engine.build(movements, prices, investments=investments, sales=sales)
    return PortfolioReport.from_portfolio(portfolio, price_consulted_at=price_consulted_at)


def serve(
    movements_file: Path,
    host: str = "127.0.0.1",
    port: int = 8000,
    investments_file: Path | None = None,
    sales_file: Path | None = None,
    price_provider=None,
) -> None:
    report = build_web_report(movements_file, investments_file, sales_file, price_provider)
    app = WebApp(report)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            # Keep the query string: WebApp uses it to apply sorting.
            path = self.path
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
    parser.add_argument("--investments-file", default=DEFAULT_INVESTMENTS_FILE)
    parser.add_argument("--sales-file", default=DEFAULT_SALES_FILE)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(
        Path(args.movements_file),
        args.host,
        args.port,
        Path(args.investments_file),
        Path(args.sales_file),
    )


if __name__ == "__main__":
    main()
