from datetime import datetime, timezone
from decimal import Decimal

from pfp.application.register_investment import RegisterInvestmentRequest
from pfp.application.register_sale import RegisterSaleRequest
from pfp.domain.asset import Asset
from pfp.domain.portfolio import Portfolio
from pfp.importers.asset_repository import AssetRepository
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository
from pfp.web.server import WebRuntime


class StubPriceProvider:
    def get_prices(self, symbols):
        return {symbol: Decimal("120") for symbol in symbols}


def test_web_runtime_supports_new_asset_buy_and_partial_sale(tmp_path):
    assets_file = tmp_path / "assets.csv"
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

    asset_repository = AssetRepository(assets_file)
    investment_repository = InvestmentRepository(investments_file)
    sale_repository = SaleRepository(sales_file)
    portfolio = Portfolio(cash=Decimal("1000"))
    runtime = WebRuntime(
        portfolio=portfolio,
        price_provider=StubPriceProvider(),
        investment_repository=investment_repository,
        sale_repository=sale_repository,
        asset_repository=asset_repository,
    )

    asset = Asset(
        symbol="NEWSTOCK",
        name="New Stock Holdings",
        portfolio_class="EQUITY",
        isin="XX0000000001",
        ticker="NEW",
    )
    runtime.register_asset(asset)
    runtime.register_investment(
        RegisterInvestmentRequest(
            datetime=datetime(2026, 8, 19, tzinfo=timezone.utc),
            symbol="NEWSTOCK",
            shares=Decimal("4"),
            amount=Decimal("400"),
            price=Decimal("100"),
            portfolio_class="EQUITY",
            broker="Trade Republic",
            operation_id="buy-newstock",
        )
    )
    runtime.register_sale(
        RegisterSaleRequest(
            datetime=datetime(2026, 8, 20, tzinfo=timezone.utc),
            symbol="NEWSTOCK",
            shares=Decimal("1"),
            amount=Decimal("150"),
            price=Decimal("150"),
            broker="Trade Republic",
            operation_id="sell-newstock-partial",
        )
    )

    position = portfolio.positions["NEWSTOCK"]
    assert position.shares == Decimal("3")
    assert position.invested == Decimal("300")
    assert position.average_price == Decimal("100")
    assert portfolio.cash == Decimal("750")
    assert portfolio.invested == Decimal("300")
    assert portfolio.realized_gain_loss == Decimal("50")
    assert portfolio.unrealized_gain_loss == Decimal("60")

    persisted_assets = asset_repository.load()
    persisted_investments = investment_repository.load()
    persisted_sales = sale_repository.load()
    assert persisted_assets == [asset]
    assert len(persisted_investments) == 1
    assert persisted_investments[0].symbol == "NEWSTOCK"
    assert len(persisted_sales) == 1
    assert persisted_sales[0].symbol == "NEWSTOCK"
    assert persisted_sales[0].shares == Decimal("1")
