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


def _build_patrimony_series(portfolio, investments, sales, external_movements, account_transfers, historical_price_provider):
    dates = {movement.datetime for movement in portfolio.movements}
    dates.update(investment.datetime for investment in investments)
    dates.update(sale.datetime for sale in sales)
    dates.update(movement.datetime for movement in external_movements)
    dates.update(transfer.datetime for transfer in account_transfers)
    opening_balances = AccountOpeningBalanceRepository(DEFAULT_OPENING_BALANCES_FILE).load()
    dates.update(datetime.combine(item.date, datetime.min.time()) for item in opening_balances)
    if not dates:
        return ()
    return PatrimonyHistory.build(
        sorted(dates),
        opening_cash=sum((item.amount for item in opening_balances), Decimal("0")),
        external_cash_movements=external_movements,
        investments=investments,
        sales=sales,
        account_transfers=account_transfers,
        price_provider=historical_price_provider,
    )


def build_web_report(movements_file: Path, investments_file: Path | None = None, sales_file: Path | None = None, price_provider=None, assets_file: Path | None = None, historical_price_provider=None) -> PortfolioReport:
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
    account_transfers = AccountTransferRepository(DEFAULT_ACCOUNT_TRANSFERS_FILE).load()
    for movement in external_movements:
        RegisterExternalCashMovement().execute(portfolio, RegisterExternalCashMovementRequest(movement.datetime, movement.account_id, movement.amount, movement.currency, movement.description))
    portfolio = _value_portfolio(portfolio, price_provider)
    patrimony_series = _build_patrimony_series(portfolio, investments, sales, external_movements, account_transfers, historical_price_provider)
    return PortfolioReport.from_portfolio(portfolio, price_consulted_at=datetime.now().astimezone(), patrimony_series=patrimony_series)


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
        patrimony_series = _build_patrimony_series(self.portfolio, investments, sales, external_movements, account_transfers, historical_provider)
        return PortfolioReport.from_portfolio(self.portfolio, price_consulted_at=datetime.now().astimezone(), patrimony_series=patrimony_series)


def build_web_runtime(movements_file: Path, investments_file: Path | None = None, sales_file: Path | None = None, price_provider=None, assets_file: Path | None = None, historical_price_provider=None) -> WebRuntime:
    investments_file = investments_file or Path(DEFAULT_INVESTMENTS_FILE)
    sales_file = sales_file or Path(DEFAULT_SALES_FILE)
    assets_file = assets_file or DEFAULT_ASSETS_FILE
    asset_repository = AssetRepository(assets_file)
    _load_assets(asset_repository)
    portfolio = load_portfolio(movements_file, investments_file, sales_file)
    external_cash_movement_repository = ExternalCashMovementRepository(DEFAULT_EXTERNAL_CASH_MOVEMENTS_FILE)
    for movement in external_cash_movement_repository.load():
        RegisterExternalCashMovement().execute(portfolio, RegisterExternalCashMovementRequest(movement.datetime, movement.account_id, movement.amount, movement.currency, movement.description))
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
