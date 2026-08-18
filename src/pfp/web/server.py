"""HTTP server for the PFP web application."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from pfp.application.register_investment import RegisterInvestment, RegisterInvestmentRequest
from pfp.application.register_sale import RegisterSale, RegisterSaleRequest
from pfp.cli import DEFAULT_INVESTMENTS_FILE, DEFAULT_SALES_FILE
from pfp.domain.portfolio import Portfolio
from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.market.price_provider import CompositePriceProvider
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp


def dashboard_html(report: PortfolioReport) -> str:
    return WebApp(report).render("/")


def build_web_report(movements_file: Path, investments_file: Path | None = None, sales_file: Path | None = None, price_provider=None) -> PortfolioReport:
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


@dataclass(slots=True)
class WebRuntime:
    portfolio: Portfolio
    price_provider: object
    investment_repository: InvestmentRepository | None = None
    sale_repository: SaleRepository | None = None

    def register_investment(self, request: RegisterInvestmentRequest):
        if self.investment_repository is None:
            raise RuntimeError("Investment repository is not configured")
        if request.operation_id and self.investment_repository.exists_by_operation_id(request.operation_id):
            raise ValueError(f"La operación «{request.operation_id}» ya ha sido registrada")
        investment = RegisterInvestment().execute(self.portfolio, request)
        self.investment_repository.save(investment)
        return investment

    def register_sale(self, request: RegisterSaleRequest):
        if self.sale_repository is None:
            raise RuntimeError("Sale repository is not configured")
        if request.operation_id and self.sale_repository.exists_by_operation_id(request.operation_id):
            raise ValueError(f"La operación «{request.operation_id}» ya ha sido registrada")
        sale = RegisterSale().execute(self.portfolio, request)
        self.sale_repository.save(sale)
        return sale

    def report(self) -> PortfolioReport:
        prices = self.price_provider.get_prices(list(self.portfolio.positions.keys()))
        for symbol, position in self.portfolio.positions.items():
            position.market_price = prices.get(symbol)
        return PortfolioReport.from_portfolio(self.portfolio, price_consulted_at=datetime.now().astimezone())


def build_web_runtime(movements_file: Path, investments_file: Path | None = None, sales_file: Path | None = None, price_provider=None) -> WebRuntime:
    investments_file = investments_file or Path(DEFAULT_INVESTMENTS_FILE)
    sales_file = sales_file or Path(DEFAULT_SALES_FILE)
    price_provider = price_provider or CompositePriceProvider()
    movements = TradeRepublicImporter().load(movements_file)
    investments = InvestmentRepository(investments_file).load()
    sales = SaleRepository(sales_file).load()
    portfolio = PortfolioEngine().build(movements, investments=investments, sales=sales)
    return WebRuntime(portfolio, price_provider, InvestmentRepository(investments_file), SaleRepository(sales_file))


def _required(form: dict[str, list[str]], name: str) -> str:
    values = form.get(name, [])
    value = values[0].strip() if values else ""
    if not value:
        raise ValueError(f"El campo «{name}» es obligatorio")
    return value


def parse_investment_request(form: dict[str, list[str]]) -> RegisterInvestmentRequest:
    try:
        when = datetime.fromisoformat(_required(form, "datetime"))
        shares = Decimal(_required(form, "shares"))
        amount = Decimal(_required(form, "amount"))
        price = Decimal(_required(form, "price"))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError("Fecha, participaciones, importe o precio no válidos") from exc
    return RegisterInvestmentRequest(datetime=when, symbol=_required(form, "symbol"), shares=shares, amount=amount, price=price, portfolio_class=_required(form, "portfolio_class"), broker=_required(form, "broker"), operation_id=(form.get("operation_id", [""])[0].strip() or None))


def parse_sale_request(form: dict[str, list[str]]) -> RegisterSaleRequest:
    try:
        when = datetime.fromisoformat(_required(form, "datetime"))
        shares = Decimal(_required(form, "shares"))
        amount = Decimal(_required(form, "amount"))
        price = Decimal(_required(form, "price"))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError("Fecha, participaciones, importe o precio no válidos") from exc
    return RegisterSaleRequest(datetime=when, symbol=_required(form, "symbol"), shares=shares, amount=amount, price=price, broker=_required(form, "broker"), operation_id=(form.get("operation_id", [""])[0].strip() or None))


def serve(movements_file: Path, host: str = "127.0.0.1", port: int = 8000, investments_file: Path | None = None, sales_file: Path | None = None, price_provider=None) -> None:
    def make_runtime() -> WebRuntime:
        return build_web_runtime(movements_file, investments_file, sales_file, price_provider)

    runtime = make_runtime()
    app = WebApp(runtime.report())

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal app, runtime
            path = self.path
            if path == "/refresh":
                try:
                    runtime = make_runtime()
                    app = WebApp(runtime.report())
                except Exception as exc:
                    self.send_error(500, f"No se han podido actualizar los datos: {exc}")
                    return
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return
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

        def do_POST(self):
            nonlocal app
            if self.path not in {"/investments", "/sales"}:
                self.send_error(404)
                return
            form = {}
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                form = parse_qs(raw, keep_blank_values=True)
                if self.path == "/investments":
                    request = parse_investment_request(form)
                    runtime.register_investment(request)
                    redirect = "/positions"
                else:
                    request = parse_sale_request(form)
                    runtime.register_sale(request)
                    redirect = "/positions"
                app = WebApp(runtime.report())
            except (ValueError, InvalidOperation) as exc:
                values = {key: values[0] if values else "" for key, values in form.items()}
                if self.path == "/investments":
                    body = app.render_investment_form(str(exc), values).encode("utf-8")
                else:
                    body = app.render_sale_form(str(exc), values).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(303)
            self.send_header("Location", redirect)
            self.end_headers()

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
    serve(Path(args.movements_file), args.host, args.port, Path(args.investments_file), Path(args.sales_file))


if __name__ == "__main__":
    main()
