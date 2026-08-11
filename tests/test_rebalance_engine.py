from decimal import Decimal

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.engine.rebalance_engine import RebalanceEngine


def build_portfolio():
    portfolio = Portfolio(cash=Decimal("1000"))
    portfolio.positions = {
        "EQUITY": Position(
            symbol="EQUITY",
            name="Equity ETF",
            shares=Decimal("10"),
            invested=Decimal("12000"),
            average_price=Decimal("1200"),
            portfolio_class="EQUITY",
            market_price=Decimal("1200"),
        ),
        "BOND": Position(
            symbol="BOND",
            name="Bond ETF",
            shares=Decimal("10"),
            invested=Decimal("5000"),
            average_price=Decimal("500"),
            portfolio_class="FIXED_INCOME",
            market_price=Decimal("500"),
        ),
        "GOLD": Position(
            symbol="GOLD",
            name="Gold ETF",
            shares=Decimal("10"),
            invested=Decimal("1000"),
            average_price=Decimal("100"),
            portfolio_class="GOLD",
            market_price=Decimal("100"),
        ),
    }
    return portfolio


def test_rebalance_total_value_includes_cash():
    rebalance = RebalanceEngine().rebalance(build_portfolio())
    assert rebalance.total_value == Decimal("19000")


def test_rebalance_calculates_target_values():
    rebalance = RebalanceEngine().rebalance(build_portfolio())
    allocations = {
        item.portfolio_class: item
        for item in rebalance.allocations
    }
    assert allocations["EQUITY"].target_value == Decimal("14250")
    assert allocations["FIXED_INCOME"].target_value == Decimal("3800")
    assert allocations["GOLD"].target_value == Decimal("950")


def test_rebalance_generates_buy_and_sell_orders():
    rebalance = RebalanceEngine().rebalance(build_portfolio())
    orders = {
        order.portfolio_class: order
        for order in rebalance.orders
    }

    assert orders["EQUITY"].action == "BUY"
    assert orders["EQUITY"].amount == Decimal("2250")
    assert orders["FIXED_INCOME"].action == "SELL"
    assert orders["FIXED_INCOME"].amount == Decimal("1200")
    assert orders["FIXED_INCOME"].shares == Decimal("2.4")
    assert orders["GOLD"].action == "SELL"
    assert orders["GOLD"].amount == Decimal("50")
    assert orders["GOLD"].shares == Decimal("0.5")


def test_rebalance_uses_existing_position_for_orders():
    rebalance = RebalanceEngine().rebalance(build_portfolio())
    assert {order.symbol for order in rebalance.orders} == {
        "EQUITY",
        "BOND",
        "GOLD",
    }


def test_rebalance_rejects_missing_market_price():
    portfolio = build_portfolio()
    portfolio.positions["EQUITY"].market_price = None

    try:
        RebalanceEngine().rebalance(portfolio)
    except ValueError as error:
        assert str(error) == "Market price is not available for EQUITY"
    else:
        raise AssertionError("Expected ValueError")
