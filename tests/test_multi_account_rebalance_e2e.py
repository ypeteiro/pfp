from decimal import Decimal
from pathlib import Path

from pfp.cli import load_portfolio
from pfp.engine.rebalance_engine import RebalanceEngine


MOVEMENTS_FILE = Path("tests/fixtures/trade_republic.csv")


def _prices(symbols):
    return {
        "IE00BK5BQT80": Decimal("100"),
        "IE00BG47KH54": Decimal("25"),
        "IE00B4ND3602": Decimal("75"),
        "IE00BKM4GZ66": Decimal("46"),
        "IE00B03HD191": Decimal("64"),
        "IE00B4L5Y983": Decimal("129"),
        "IE00B5BMR087": Decimal("724"),
        "IE000I1Q42S9": Decimal("4.34"),
        "BTC": Decimal("55000"),
    }


def test_real_trade_republic_fixture_builds_account_scoped_portfolio():
    portfolio = load_portfolio(MOVEMENTS_FILE, None, None)

    assert [account.account_id for account in portfolio.accounts] == ["Trade Republic"]
    assert "Trade Republic" in portfolio.account_positions
    assert portfolio.account_positions["Trade Republic"]


def test_real_trade_republic_fixture_rebalance_is_scoped_to_trade_republic():
    portfolio = load_portfolio(MOVEMENTS_FILE, None, None)
    for position in portfolio.positions.values():
        position.market_price = _prices([position.symbol]).get(position.symbol)

    rebalance = RebalanceEngine().rebalance(portfolio, account_id="Trade Republic")

    assert rebalance.rebalanceable_value > 0
    assert rebalance.orders
    assert all(order.account_id == "Trade Republic" for order in rebalance.orders)


def test_real_trade_republic_fixture_rebalance_is_stable_when_recalculated():
    portfolio = load_portfolio(MOVEMENTS_FILE, None, None)
    for position in portfolio.positions.values():
        position.market_price = _prices([position.symbol]).get(position.symbol)

    engine = RebalanceEngine()
    first = engine.rebalance(portfolio, account_id="Trade Republic")
    second = engine.rebalance(portfolio, account_id="Trade Republic")

    assert first.orders == second.orders
    assert first.rebalanceable_value == second.rebalanceable_value
