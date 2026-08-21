from pathlib import Path
from decimal import Decimal

from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.trade_republic import TradeRepublicImporter


CSV_FILE = Path("tests/fixtures/trade_republic.csv")


def test_trade_republic_fixture_has_25000_eur_of_external_contributions():
    importer = TradeRepublicImporter()

    flows = importer.load_capital_flows(CSV_FILE)

    contributions = [flow for flow in flows if flow.flow_type.value == "CONTRIBUTION"]
    withdrawals = [flow for flow in flows if flow.flow_type.value == "WITHDRAWAL"]

    assert len(contributions) == 7
    assert sum((flow.amount for flow in contributions), Decimal("0")) == Decimal("25000")
    assert withdrawals == []
    assert len({flow.transaction_id for flow in contributions}) == len(contributions)


def test_trade_republic_cash_reconciles_contributions_less_trading_cash_outflows():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)

    contributions = sum(
        (movement.amount for movement in movements
         if movement.category == "CASH" and movement.type.endswith("INBOUND")),
        Decimal("0"),
    )
    trading_cash_outflows = sum(
        (abs(movement.amount) + abs(movement.fee) + abs(movement.tax)
         for movement in movements if movement.category == "TRADING" and movement.type == "BUY"),
        Decimal("0"),
    )

    portfolio = PortfolioEngine().build(movements)

    assert contributions == Decimal("25000")
    assert trading_cash_outflows == Decimal("21406.61")
    assert portfolio.cash == contributions - trading_cash_outflows
    assert portfolio.invested == trading_cash_outflows
    assert portfolio.cash + portfolio.invested == contributions


def test_trade_republic_total_value_reconciles_without_double_counting_fees():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    portfolio = PortfolioEngine().build(movements)

    for position in portfolio.positions.values():
        position.market_price = position.average_price

    assert portfolio.market_value == portfolio.invested
    assert portfolio.total_value == Decimal("25000")
    assert portfolio.unrealized_gain_loss == Decimal("0")
