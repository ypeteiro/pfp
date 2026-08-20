from decimal import Decimal
from pathlib import Path

from pfp.cli import run_invest, run_invest_order, run_sell
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository


MOVEMENTS_FILE = Path("data/imports/trade_republic.csv")


def test_run_invest_persists_account_identity(tmp_path):
    investments_file = tmp_path / "investments.csv"

    run_invest(
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        portfolio_class="EQUITY",
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        account_id="ABANCA_AHORRO",
    )

    investment = InvestmentRepository(investments_file).load()[0]
    assert investment.account_id == "ABANCA_AHORRO"


def test_run_invest_order_persists_account_identity(tmp_path):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

    class StubPriceProvider:
        def get_prices(self, symbols):
            return {"IE00BG47KH54": Decimal("120")}

    run_invest_order(
        symbol="IE00BG47KH54",
        amount=Decimal("300"),
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        price_provider=StubPriceProvider(),
        sales_file=sales_file,
        account_id="ABANCA_AHORRO",
    )

    investment = InvestmentRepository(investments_file).load()[0]
    assert investment.account_id == "ABANCA_AHORRO"


def test_run_invest_order_is_idempotent_for_same_operation_id(tmp_path):
    investments_file = tmp_path / "investments.csv"
    sales_file = tmp_path / "sales.csv"

    class StubPriceProvider:
        def get_prices(self, symbols):
            return {"IE00BG47KH54": Decimal("120")}

    kwargs = dict(
        symbol="IE00BG47KH54",
        amount=Decimal("300"),
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        price_provider=StubPriceProvider(),
        sales_file=sales_file,
        account_id="Trade Republic",
        operation_id="rebalance:Trade Republic:IE00BG47KH54:BUY",
    )

    run_invest_order(**kwargs)
    run_invest_order(**kwargs)

    investments = InvestmentRepository(investments_file).load()
    assert len(investments) == 1
    assert investments[0].operation_id == kwargs["operation_id"]


def test_run_sell_persists_account_identity(tmp_path):
    sales_file = tmp_path / "sales.csv"
    investments_file = tmp_path / "investments.csv"

    run_sell(
        symbol="IE00B4L5Y983",
        shares=Decimal("0.1"),
        amount=Decimal("150"),
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        sales_file=sales_file,
        account_id="ABANCA_AHORRO",
    )

    sale = SaleRepository(sales_file).load()[0]
    assert sale.account_id == "ABANCA_AHORRO"
