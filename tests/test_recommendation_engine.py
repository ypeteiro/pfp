from decimal import Decimal

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.engine.recommendation_engine import RecommendationEngine


TEST_TARGET_ALLOCATION = {
    "EQUITY": Decimal("75"),
    "FIXED_INCOME": Decimal("20"),
    "GOLD": Decimal("5"),
}


def build_portfolio():
    portfolio = Portfolio()

    portfolio.positions = {
        "EQUITY": Position(
            symbol="EQUITY",
            name="Equity ETF",
            shares=Decimal("10"),
            invested=Decimal("15000"),
            portfolio_class="EQUITY",
        ),
        "BOND": Position(
            symbol="BOND",
            name="Bond ETF",
            shares=Decimal("10"),
            invested=Decimal("4000"),
            portfolio_class="FIXED_INCOME",
        ),
        "GOLD": Position(
            symbol="GOLD",
            name="Gold ETF",
            shares=Decimal("10"),
            invested=Decimal("1000"),
            portfolio_class="GOLD",
        ),
    }

    return portfolio


def engine():
    return RecommendationEngine(TEST_TARGET_ALLOCATION)


def test_recommendation_total_matches_contribution():
    portfolio = build_portfolio()

    recommendation = engine().recommend(
        portfolio,
        Decimal("800"),
    )

    total = sum(order.amount for order in recommendation.orders)
    assert total == Decimal("800")


def test_recommendation_creates_orders_for_target_classes():
    portfolio = build_portfolio()

    recommendation = engine().recommend(portfolio, Decimal("800"))

    assert {order.portfolio_class for order in recommendation.orders} == {
        "EQUITY",
        "FIXED_INCOME",
        "GOLD",
    }


def test_recommendation_uses_existing_asset_for_each_order():
    portfolio = build_portfolio()

    recommendation = engine().recommend(portfolio, Decimal("800"))

    assert {order.symbol for order in recommendation.orders} == {
        "EQUITY",
        "BOND",
        "GOLD",
    }


def test_recommendation_does_not_create_zero_amount_orders():
    portfolio = build_portfolio()

    recommendation = engine().recommend(portfolio, Decimal("800"))

    assert all(order.amount > 0 for order in recommendation.orders)


def test_recommendation_rejects_non_positive_amount():
    portfolio = build_portfolio()
    engine = RecommendationEngine(TEST_TARGET_ALLOCATION)

    for amount in (Decimal("0"), Decimal("-1")):
        try:
            engine.recommend(portfolio, amount)
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError")
