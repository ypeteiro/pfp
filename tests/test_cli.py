from pathlib import Path
from decimal import Decimal

from pfp.cli import run_invest, run_invest_order
from pfp.engine.recommendation_engine import RecommendationEngine
from pfp.importers.investment_repository import (
    InvestmentRepository,
)
from pfp.cli import load_portfolio


MOVEMENTS_FILE = Path(
    "data/imports/trade_republic.csv"
)


def test_run_invest_persists_investment(
    tmp_path,
):
    investments_file = (
        tmp_path / "investments.csv"
    )

    run_invest(
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        portfolio_class="EQUITY",
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
    )

    repository = InvestmentRepository(
        investments_file
    )

    investments = repository.load()

    assert len(investments) == 1

    investment = investments[0]

    assert investment.symbol == "TEST"
    assert investment.shares == Decimal("2")
    assert investment.amount == Decimal("200")
    assert investment.price == Decimal("100")
    assert investment.portfolio_class == "EQUITY"
    assert investment.broker == "Trade Republic"


def test_run_invest_uses_utc_datetime(
    tmp_path,
):
    investments_file = (
        tmp_path / "investments.csv"
    )

    run_invest(
        symbol="TEST",
        shares=Decimal("1"),
        amount=Decimal("100"),
        portfolio_class="EQUITY",
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
    )

    repository = InvestmentRepository(
        investments_file
    )

    investments = repository.load()

    assert len(investments) == 1

    investment = investments[0]

    assert investment.datetime.tzinfo is not None
    assert (
        investment.datetime.utcoffset()
        is not None
    )


def test_run_invest_order_uses_current_price_and_persists(
    tmp_path,
):
    investments_file = (
        tmp_path / "investments.csv"
    )

    class StubPriceProvider:
        def get_prices(self, symbols):
            assert symbols == ["IE00BG47KH54"]
            return {
                "IE00BG47KH54": Decimal("120")
            }

    run_invest_order(
        symbol="IE00BG47KH54",
        amount=Decimal("300"),
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        price_provider=StubPriceProvider(),
    )

    investments = InvestmentRepository(
        investments_file
    ).load()

    assert len(investments) == 1
    investment = investments[0]

    assert investment.symbol == "IE00BG47KH54"
    assert investment.amount == Decimal("300")
    assert investment.price == Decimal("120")
    assert investment.shares == Decimal("2.5")
    assert investment.portfolio_class == "FIXED_INCOME"


def test_run_invest_order_rejects_unknown_symbol(
    tmp_path,
):
    investments_file = (
        tmp_path / "investments.csv"
    )

    class StubPriceProvider:
        def get_prices(self, symbols):
            return {
                "UNKNOWN": Decimal("100")
            }

    try:
        run_invest_order(
            symbol="UNKNOWN",
            amount=Decimal("100"),
            movements_file=MOVEMENTS_FILE,
            investments_file=investments_file,
            price_provider=StubPriceProvider(),
        )
    except ValueError as error:
        assert str(error) == (
            "Symbol is not present in portfolio"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_recommendation_order_can_be_executed_as_investment(
    tmp_path,
):
    investments_file = (
        tmp_path / "investments.csv"
    )

    portfolio = load_portfolio(
        MOVEMENTS_FILE,
        investments_file,
    )

    recommendation = RecommendationEngine().recommend(
        portfolio,
        Decimal("300"),
    )

    order = recommendation.orders[0]

    class StubPriceProvider:
        def get_prices(self, symbols):
            return {
                order.symbol: Decimal("120")
            }

    run_invest_order(
        symbol=order.symbol,
        amount=order.amount,
        movements_file=MOVEMENTS_FILE,
        investments_file=investments_file,
        price_provider=StubPriceProvider(),
    )

    investments = InvestmentRepository(
        investments_file
    ).load()

    assert len(investments) == 1
    assert investments[0].symbol == order.symbol
    assert investments[0].amount == order.amount
    assert investments[0].portfolio_class == order.portfolio_class
