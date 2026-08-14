from pathlib import Path
from decimal import Decimal

from pfp.cli import load_portfolio, run_invest, run_invest_order, run_recommend, run_sell
from pfp.engine.recommendation_engine import RecommendationEngine
from pfp.importers.investment_repository import InvestmentRepository
from pfp.importers.sale_repository import SaleRepository


MOVEMENTS_FILE = Path("data/imports/trade_republic.csv")


def test_run_invest_persists_investment(tmp_path):
    investments_file = tmp_path / "investments.csv"

    run_invest(
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        portfolio_class="EQUITY",
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
    )

    investments = InvestmentRepository(investments_file).load()

    assert len(investments) == 1
    investment = investments[0]
    assert investment.symbol == "TEST"
    assert investment.shares == Decimal("2")
    assert investment.amount == Decimal("200")
    assert investment.price == Decimal("100")
    assert investment.portfolio_class == "EQUITY"
    assert investment.broker == "Trade Republic"


def test_run_invest_uses_utc_datetime(tmp_path):
    investments_file = tmp_path / "investments.csv"

    run_invest(
        symbol="TEST",
        shares=Decimal("1"),
        amount=Decimal("100"),
        portfolio_class="EQUITY",
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
    )

    investments = InvestmentRepository(investments_file).load()

    assert len(investments) == 1
    investment = investments[0]
    assert investment.datetime.tzinfo is not None
    assert investment.datetime.utcoffset() is not None


def test_run_invest_order_uses_current_price_and_persists(tmp_path):
    investments_file = tmp_path / "investments.csv"

    class StubPriceProvider:
        def get_prices(self, symbols):
            assert symbols == ["IE00BG47KH54"]
            return {"IE00BG47KH54": Decimal("120")}

    run_invest_order(
        symbol="IE00BG47KH54",
        amount=Decimal("300"),
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        price_provider=StubPriceProvider(),
    )

    investments = InvestmentRepository(investments_file).load()

    assert len(investments) == 1
    investment = investments[0]
    assert investment.symbol == "IE00BG47KH54"
    assert investment.amount == Decimal("300")
    assert investment.price == Decimal("120")
    assert investment.shares == Decimal("2.5")
    assert investment.portfolio_class == "FIXED_INCOME"


def test_run_invest_order_rejects_unknown_symbol(tmp_path):
    investments_file = tmp_path / "investments.csv"

    class StubPriceProvider:
        def get_prices(self, symbols):
            return {"UNKNOWN": Decimal("100")}

    try:
        run_invest_order(
            symbol="UNKNOWN",
            amount=Decimal("100"),
            movements_file=MOVEMENTS_FILE,
            investments_file=investments_file,
            price_provider=StubPriceProvider(),
        )
    except ValueError as error:
        assert str(error) == "Symbol is not present in portfolio"
    else:
        raise AssertionError("Expected ValueError")


def test_recommendation_order_can_be_executed_as_investment(tmp_path):
    investments_file = tmp_path / "investments.csv"

    portfolio = load_portfolio(MOVEMENTS_FILE, investments_file)
    recommendation = RecommendationEngine().recommend(
        portfolio,
        Decimal("300"),
    )
    order = recommendation.orders[0]

    class StubPriceProvider:
        def get_prices(self, symbols):
            return {order.symbol: Decimal("120")}

    run_invest_order(
        symbol=order.symbol,
        amount=order.amount,
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        price_provider=StubPriceProvider(),
    )

    investments = InvestmentRepository(investments_file).load()

    assert len(investments) == 1
    assert investments[0].symbol == order.symbol
    assert investments[0].amount == order.amount
    assert investments[0].portfolio_class == order.portfolio_class


def test_run_recommend_prints_executable_invest_order(tmp_path, capsys):
    investments_file = tmp_path / "investments.csv"

    portfolio = load_portfolio(MOVEMENTS_FILE, investments_file)
    recommendation = RecommendationEngine().recommend(
        portfolio,
        Decimal("300"),
    )

    run_recommend(
        Decimal("300"),
        MOVEMENTS_FILE,
        investments_file,
    )

    output = capsys.readouterr().out

    for order in recommendation.orders:
        assert (
            "python -m pfp invest-order "
            f"{order.symbol} "
            f"{order.amount:.2f} "
            f"{MOVEMENTS_FILE} "
            f"--investments-file {investments_file}"
        ) in output


def test_run_sell_persists_sale_and_updates_portfolio(tmp_path):
    sales_file = tmp_path / "sales.csv"
    investments_file = tmp_path / "investments.csv"

    before = load_portfolio(MOVEMENTS_FILE, investments_file, sales_file)
    before_position = before.positions["IE00B4L5Y983"]

    run_sell(
        symbol="IE00B4L5Y983",
        shares=Decimal("0.1"),
        amount=Decimal("150"),
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        sales_file=sales_file,
    )

    sales = SaleRepository(sales_file).load()
    assert len(sales) == 1
    assert sales[0].symbol == "IE00B4L5Y983"
    assert sales[0].shares == Decimal("0.1")
    assert sales[0].amount == Decimal("150")
    assert sales[0].price == Decimal("1500")
    assert sales[0].datetime.tzinfo is not None

    after = load_portfolio(MOVEMENTS_FILE, investments_file, sales_file)
    after_position = after.positions["IE00B4L5Y983"]
    assert after_position.shares == before_position.shares - Decimal("0.1")
    assert after.cash == before.cash + Decimal("150")


def test_run_sell_rejects_more_shares_than_position(tmp_path):
    sales_file = tmp_path / "sales.csv"
    investments_file = tmp_path / "investments.csv"
    portfolio = load_portfolio(MOVEMENTS_FILE, investments_file, sales_file)
    position = portfolio.positions["IE00B4L5Y983"]

    try:
        run_sell(
            symbol="IE00B4L5Y983",
            shares=position.shares + Decimal("0.1"),
            amount=Decimal("150"),
            movements_file=MOVEMENTS_FILE,
            investments_file=investments_file,
            sales_file=sales_file,
        )
    except ValueError as error:
        assert str(error) == "Insufficient shares"
    else:
        raise AssertionError("Expected ValueError")


def test_run_invest_with_same_operation_id_is_idempotent(tmp_path):
    investments_file = tmp_path / "investments.csv"

    for _ in range(2):
        run_invest(
            symbol="TEST",
            shares=Decimal("2"),
            amount=Decimal("200"),
            portfolio_class="EQUITY",
            movements_file=MOVEMENTS_FILE,
            investments_file=investments_file,
            operation_id="rebalance-1",
        )

    investments = InvestmentRepository(investments_file).load()
    assert len(investments) == 1
    assert investments[0].operation_id == "rebalance-1"
