"""HTTP server for the PFP web application."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from pfp.application.register_account_transfer import RegisterAccountTransfer, RegisterAccountTransferRequest
from pfp.application.register_external_cash_movement import RegisterExternalCashMovement, RegisterExternalCashMovementRequest
from pfp.application.register_investment import RegisterInvestment, RegisterInvestmentRequest
from pfp.application.register_sale import RegisterSale, RegisterSaleRequest
from pfp.cli import DEFAULT_INVESTMENTS_FILE, DEFAULT_SALES_FILE, load_portfolio
from pfp.domain.asset import Asset
from pfp.domain.asset_catalog import AssetCatalog
from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.domain.portfolio import Portfolio
from pfp.domain.account_reconciliation_record import AccountReconciliationRecord
from pfp.engine.account_reconciliation_engine import AccountReconciliationEngine
from pfp.importers.account_opening_balance_repository import AccountOpeningBalanceRepository
from pfp.importers.account_reconciliation_repository import AccountReconciliationRepository
from pfp.importers.account_transfer_repository import AccountTransferRepository
from pfp.importers.asset_repository import AssetRepository
from pfp.importers.external_cash_movement_repository import ExternalCashMovementRepository
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository
from pfp.importers.trade_republic import TradeRepublicImporter
from pfp.market.price_provider import CompositePriceProvider
from pfp.market.yahoo_historical import YahooFinanceHistoricalPriceProvider
from pfp.reporting.patrimony_history import PatrimonyHistory
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.app import WebApp
from pfp.web.rebalance_ui import rebalance_html

DEFAULT_ASSETS_FILE = Path("data/assets.csv")
DEFAULT_RECONCILIATIONS_FILE = Path("data/accounts/reconciliation_history.csv")
DEFAULT_EXTERNAL_CASH_MOVEMENTS_FILE = Path("data/accounts/external_cash_movements.csv")
DEFAULT_ACCOUNT_TRANSFERS_FILE = Path("data/accounts/account_transfers.csv")
DEFAULT_OPENING_BALANCES_FILE = Path("data/accounts/opening_balances.csv")


def dashboard_html(report: PortfolioReport) -> str:
    return WebApp(report).render("/")


def _load_assets(asset_repository: AssetRepository) -> None:
    for asset in asset_repository.load():
        AssetCatalog.register(asset)


def _value_portfolio(portfolio: Portfolio, price_provider) -> Portfolio:
    prices = price_provider.get_prices(list(portfolio.positions.keys()))
    for symbol, position in portfolio.positions.items():
        position.market_price = prices.get(symbol)
    for positions in portfolio.account_positions.values():
        for symbol, position in positions.items():
            position.market_price = prices.get(symbol)
    return portfolio


def _history_datetime(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def _trade_republic_cash_movements(movements_file: Path) -> list[ExternalCashMovement]:
    """Convert Trade Republic cash transfers into historical cash movements."""
    flows = TradeRepublicImporter().load_capital_flows(movements_file)
    return [
        ExternalCashMovement(
            datetime=_history_datetime(flow.datetime),
            account_id="Trade Republic",
            amount=flow.signed_amount,
            currency="EUR",
            description="Trade Republic capital flow",
        )
        for flow in flows
    ]


def _build_patrimony_series(
    portfolio,
    investments,
    sales,
    external_movements,
    account_transfers,
    historical_price_provider,
    trade_republic_movements=(),
):
    dates = {_history_datetime(movement.datetime) for movement in portfolio.movements}
    dates.update(_history_datetime(investment.datetime) for investment in investments)
    dates.update(_history_datetime(sale.datetime) for sale in sales)
    dates.update(_history_datetime(movement.datetime) for movement in external_movements)
    dates.update(_history_datetime(movement.datetime) for movement in trade_republic_movements)
    dates.update(_history_datetime(transfer.datetime) for transfer in account_transfers)
    opening_balances = AccountOpeningBalanceRepository(DEFAULT_OPENING_BALANCES_FILE).load()
    dates.update(datetime.combine(item.date, datetime.min.time()) for item in opening_balances)
    if not dates:
        return ()
    return PatrimonyHistory.build(
        sorted(dates),
        opening_cash=sum((item.amount for item in opening_balances), Decimal("0")),
        external_cash_movements=[*external_movements, *trade_republic_movements],
        movements=tuple(portfolio.movements),
        investments=investments,
        sales=sales,
        account_transfers=account_transfers,
        price_provider=historical_price_provider,
    )


def build_web_report(
    movements_file: Path,
    investments_file: Path | None = None,
    sales_file: Path | None = None,
    price_provider=None,
    assets_file: Path | None = None,
    historical_price_provider=None,
) -> PortfolioReport:
    investments_file = investments_file or Path(DEFAULT_INVESTMENTS_FILE)
    sales_file = sales_file or Path(DEFAULT_SALES_FILE)
    assets_file = assets_file or DEFAULT_ASSETS_FILE
    price_provider = price_provider or CompositePriceProvider()
    historical_price_provider = historical_price_provider or YahooFinanceHistoricalPriceProvider()
    _load_assets(AssetRepository(assets_file))
    investments = InvestmentRepository(investments_file).load()
    sales = SaleRepository(sales_file).load()
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    external_movements = ExternalCashMovementRepository(DEFAULT_EXTERNAL_CASH_MOVEMENTS_FILE).load()
    trade_republic_movements = _trade_republic_cash_movements(movements_file)
    for movement in external_movements:
        RegisterExternalCashMovement().execute(
            portfolio,
            RegisterExternalCashMovementRequest(
                movement.datetime,
                movement.account_id,
                movement.amount,
                movement.currency,
                movement.description,
            ),
        )
    portfolio = _value_portfolio(portfolio, price_provider)
    account_transfers = AccountTransferRepository(DEFAULT_ACCOUNT_TRANSFERS_FILE).load()
    patrimony_series = _build_patrimony_series(
        portfolio,
        investments,
        sales,
        external_movements,
        account_transfers,
        historical_price_provider,
        trade_republic_movements,
    )
    return PortfolioReport.from_portfolio(
        portfolio,
        price_consulted_at=datetime.now().astimezone(),
        patrimony_series=patrimony_series,
    )


@dataclass(slots=True)
class WebRuntime:
    portfolio: Portfolio
    price_provider: object
    investment_repository: InvestmentRepository | None = None
    sale_repository: SaleRepository | None = None
    asset_repository: AssetRepository | None = None
    external_cash_movement_repository: ExternalCashMovementRepository | None = None
    account_transfer_repository: AccountTransferRepository | None = None
    historical_price_provider: object | None = None

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

    def register_asset(self, asset: Asset):
        if self.asset_repository is None:
            raise RuntimeError("Asset repository is not configured")
        AssetCatalog.register(asset)
        self.asset_repository.save(asset)
        return asset

    def register_external_cash_movement(self, request: RegisterExternalCashMovementRequest):
        if self.external_cash_movement_repository is None:
            raise RuntimeError("External cash movement repository is not configured")
        movement = RegisterExternalCashMovement().execute(self.portfolio, request)
        self.external_cash_movement_repository.save(movement)
        return movement

    def register_account_transfer(self, request: RegisterAccountTransferRequest):
        if self.account_transfer_repository is None:
            raise RuntimeError("Account transfer repository is not configured")
        transfer = RegisterAccountTransfer().execute(self.portfolio, request)
        self.account_transfer_repository.save(transfer)
        return transfer

    def report(self) -> PortfolioReport:
        _value_portfolio(self.portfolio, self.price_provider)
        investments = self.investment_repository.load() if self.investment_repository is not None else ()
        sales = self.sale_repository.load() if self.sale_repository is not None else ()
        external_movements = self.external_cash_movement_repository.load() if self.external_cash_movement_repository is not None else ()
        account_transfers = self.account_transfer_repository.load() if self.account_transfer_repository is not None else ()
        historical_provider = self.historical_price_provider or YahooFinanceHistoricalPriceProvider()
        trade_republic_movements = [
            ExternalCashMovement(
                datetime=_history_datetime(movement.datetime),
                account_id="Trade Republic",
                amount=movement.amount,
                currency=movement.currency,
                description=movement.description,
            )
            for movement in self.portfolio.movements
            if movement.category == "CASH" and movement.type.upper().endswith(("_INBOUND", "_OUTBOUND"))
        ]
        patrimony_series = _build_patrimony_series(
            self.portfolio,
            investments,
            sales,
            external_movements,
            account_transfers,
            historical_provider,
            trade_republic_movements,
        )
        return PortfolioReport.from_portfolio(
            self.portfolio,
            price_consulted_at=datetime.now().astimezone(),
            patrimony_series=patrimony_series,
        )


def build_web_runtime(
    movements_file: Path,
    investments_file: Path | None = None,
    sales_file: Path | None = None,
    price_provider=None,
    assets_file: Path | None = None,
    historical_price_provider=None,
) -> WebRuntime:
    investments_file = investments_file or Path(DEFAULT_INVESTMENTS_FILE)
    sales_file = sales_file or Path(DEFAULT_SALES_FILE)
    assets_file = assets_file or DEFAULT_ASSETS_FILE
    asset_repository = AssetRepository(assets_file)
    _load_assets(asset_repository)
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    external_cash_movement_repository = ExternalCashMovementRepository(DEFAULT_EXTERNAL_CASH_MOVEMENTS_FILE)
    for movement in external_cash_movement_repository.load():
        RegisterExternalCashMovement().execute(
            portfolio,
            RegisterExternalCashMovementRequest(
                movement.datetime,
                movement.account_id,
                movement.amount,
                movement.currency,
                movement.description,
            ),
        )
    return WebRuntime(
        portfolio,
        price_provider or CompositePriceProvider(),
        InvestmentRepository(investments_file),
        SaleRepository(sales_file),
        asset_repository,
        external_cash_movement_repository,
        AccountTransferRepository(DEFAULT_ACCOUNT_TRANSFERS_FILE),
        historical_price_provider,
    )


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
    return RegisterInvestmentRequest(
        datetime=when,
        symbol=_required(form, "symbol"),
        shares=shares,
        amount=amount,
        price=price,
        portfolio_class=_required(form, "portfolio_class"),
        broker=_required(form, "broker"),
        operation_id=(form.get("operation_id", [""])[0].strip() or None),
    )


def parse_sale_request(form: dict[str, list[str]]) -> RegisterSaleRequest:
    try:
        when = datetime.fromisoformat(_required(form, "datetime"))
        shares = Decimal(_required(form, "shares"))
        amount = Decimal(_required(form, "amount"))
        price = Decimal(_required(form, "price"))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError("Fecha, participaciones, importe o precio no válidos") from exc
    return RegisterSaleRequest(
        datetime=when,
        symbol=_required(form, "symbol"),
        shares=shares,
        amount=amount,
        price=price,
        broker=_required(form, "broker"),
        operation_id=(form.get("operation_id", [""])[0].strip() or None),
    )


def parse_asset_request(form: dict[str, list[str]]) -> Asset:
    return Asset(
        symbol=_required(form, "symbol"),
        name=_required(form, "name"),
        portfolio_class=_required(form, "portfolio_class"),
        isin=(form.get("isin", [""])[0].strip() or None),
        ticker=(form.get("ticker", [""])[0].strip() or None),
    )


def parse_reconciliation_request(form: dict[str, list[str]]):
    try:
        expected_balance = Decimal(_required(form, "expected_balance"))
    except InvalidOperation as exc:
        raise ValueError("El saldo esperado no es válido") from exc
    if expected_balance < 0:
        raise ValueError("El saldo esperado no puede ser negativo")
    return _required(form, "account_id"), expected_balance


def parse_account_adjustment_request(form: dict[str, list[str]]):
    try:
        when = datetime.fromisoformat(_required(form, "datetime"))
        target_balance = Decimal(_required(form, "target_balance"))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError("Fecha o saldo no válidos") from exc
    if target_balance < 0:
        raise ValueError("El saldo no puede ser negativo")
    return _required(form, "account_id"), target_balance, when, (form.get("description", [""])[0].strip() or "Ajuste manual de saldo")


def parse_account_transfer_request(form: dict[str, list[str]]) -> RegisterAccountTransferRequest:
    try:
        when = datetime.fromisoformat(_required(form, "datetime"))
        amount = Decimal(_required(form, "amount"))
    except (ValueError, InvalidOperation) as exc:
        raise ValueError("Fecha o importe no válidos") from exc
    return RegisterAccountTransferRequest(
        datetime=when,
        source_account=_required(form, "source_account"),
        destination_account=_required(form, "destination_account"),
        amount=amount,
        currency=(form.get("currency", ["EUR"])[0].strip() or "EUR").upper(),
    )


def serve(
    movements_file: Path,
    host: str = "127.0.0.1",
    port: int = 8000,
    investments_file: Path | None = None,
    sales_file: Path | None = None,
    assets_file: Path | None = None,
    price_provider=None,
    reconciliations_file: Path | None = None,
) -> None:
    def make_runtime() -> WebRuntime:
        return build_web_runtime(movements_file, investments_file, sales_file, price_provider, assets_file)

    runtime = make_runtime()
    reconciliation_repository = AccountReconciliationRepository(reconciliations_file or DEFAULT_RECONCILIATIONS_FILE)
    app = WebApp(runtime.report(), AssetCatalog.all(), tuple(reconciliation_repository.load()), tuple(runtime.portfolio.accounts))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal app, runtime, reconciliation_repository
            path = self.path
            if path == "/refresh":
                try:
                    runtime = make_runtime()
                    reconciliation_repository = AccountReconciliationRepository(reconciliations_file or DEFAULT_RECONCILIATIONS_FILE)
                    app = WebApp(runtime.report(), AssetCatalog.all(), tuple(reconciliation_repository.load()), tuple(runtime.portfolio.accounts))
                except Exception as exc:
                    self.send_error(500, f"No se han podido actualizar los datos: {exc}")
                    return
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return
            if path == "/rebalance" or path.startswith("/rebalance?"):
                query = parse_qs(path.split("?", 1)[1] if "?" in path else "")
                account_id = query.get("account_id", [None])[0]
                try:
                    body = app._layout(rebalance_html(runtime.portfolio, account_id), "/rebalance").encode("utf-8")
                except ValueError as exc:
                    self.send_error(400, str(exc))
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
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
            allowed = {"/investments", "/sales", "/assets", "/reconcile", "/accounts/adjust", "/account-transfers"}
            if self.path not in allowed:
                self.send_error(404)
                return
            form = {}
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                form = parse_qs(raw, keep_blank_values=True)
                if self.path == "/investments":
                    runtime.register_investment(parse_investment_request(form))
                elif self.path == "/sales":
                    runtime.register_sale(parse_sale_request(form))
                elif self.path == "/assets":
                    runtime.register_asset(parse_asset_request(form))
                elif self.path == "/accounts/adjust":
                    account_id, target_balance, when, description = parse_account_adjustment_request(form)
                    account = next((item for item in runtime.portfolio.accounts if item.id == account_id), None)
                    if account is None:
                        raise ValueError(f"Cuenta desconocida: {account_id}")
                    delta = target_balance - account.balance
                    if delta != 0:
                        runtime.register_external_cash_movement(RegisterExternalCashMovementRequest(when, account_id, delta, account.currency, description))
                elif self.path == "/account-transfers":
                    runtime.register_account_transfer(parse_account_transfer_request(form))
                else:
                    account_id, expected_balance = parse_reconciliation_request(form)
                    account = next((item for item in runtime.portfolio.accounts if item.id == account_id), None)
                    if account is None:
                        raise ValueError(f"Cuenta desconocida: {account_id}")
                    reconciliation = AccountReconciliationEngine.reconcile(account, expected_balance)
                    record = AccountReconciliationRecord(
                        datetime=datetime.now(timezone.utc),
                        account_id=reconciliation.account_id,
                        expected_balance=reconciliation.expected_balance,
                        calculated_balance=reconciliation.calculated_balance,
                        difference=reconciliation.difference,
                        status="RECONCILED" if reconciliation.is_reconciled else "MISMATCH",
                    )
                    reconciliation_repository.save(record)
                    app = WebApp(runtime.report(), AssetCatalog.all(), tuple(reconciliation_repository.load()), tuple(runtime.portfolio.accounts), reconciliation)
                    body = app.render_reconciliation_form(account_id=account_id).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                app = WebApp(runtime.report(), AssetCatalog.all(), tuple(reconciliation_repository.load()), tuple(runtime.portfolio.accounts))
                redirect = "/accounts" if self.path in {"/accounts/adjust", "/account-transfers"} else ("/positions" if self.path != "/assets" else "/assets")
            except (ValueError, InvalidOperation) as exc:
                values = {key: values[0] if values else "" for key, values in form.items()}
                if self.path == "/investments":
                    body = app.render_investment_form(str(exc), values).encode("utf-8")
                elif self.path == "/sales":
                    body = app.render_sale_form(str(exc), values).encode("utf-8")
                elif self.path == "/reconcile":
                    body = app.render_reconciliation_form(str(exc), values, values.get("account_id")).encode("utf-8")
                elif self.path in {"/accounts/adjust", "/account-transfers"}:
                    body = app.render(path="/accounts").encode("utf-8")
                else:
                    body = app.render_asset_form(str(exc), values).encode("utf-8")
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
    parser.add_argument("--assets-file", default=str(DEFAULT_ASSETS_FILE))
    parser.add_argument("--reconciliations-file", default=str(DEFAULT_RECONCILIATIONS_FILE))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(
        Path(args.movements_file),
        args.host,
        args.port,
        Path(args.investments_file),
        Path(args.sales_file),
        Path(args.assets_file),
        reconciliations_file=Path(args.reconciliations_file),
    )


if __name__ == "__main__":
    main()
