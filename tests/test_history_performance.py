from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.domain.snapshot import PortfolioSnapshot
from pfp.engine.history_engine import HistoryEngine


def _snapshot(day, value):
    return PortfolioSnapshot(
        datetime=datetime(2026, 8, day, tzinfo=timezone.utc),
        total_value=Decimal(value),
        cash=Decimal("0"),
        invested_cost=Decimal("0"),
        market_value=Decimal(value),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("0"),
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
    )


def test_time_weighted_return_ignores_contribution():
    history = HistoryEngine().build(
        [_snapshot(10, "20000"), _snapshot(11, "20850")],
        [
            CapitalFlow(
                datetime=datetime(2026, 8, 11, 12, tzinfo=timezone.utc),
                amount=Decimal("800"),
                flow_type=FlowType.CONTRIBUTION,
            )
        ],
    )

    assert history.time_weighted_return == Decimal("0.0025")
    assert history.time_weighted_return_percent == Decimal("0.2500")


def test_time_weighted_return_handles_withdrawal():
    history = HistoryEngine().build(
        [_snapshot(10, "20000"), _snapshot(11, "19100")],
        [
            CapitalFlow(
                datetime=datetime(2026, 8, 11, 12, tzinfo=timezone.utc),
                amount=Decimal("1000"),
                flow_type=FlowType.WITHDRAWAL,
            )
        ],
    )

    assert history.time_weighted_return == Decimal("0.005")
    assert history.time_weighted_return_percent == Decimal("0.500")


def test_time_weighted_return_compounds_multiple_periods():
    history = HistoryEngine().build(
        [
            _snapshot(10, "10000"),
            _snapshot(11, "10500"),
            _snapshot(12, "11500"),
        ],
        [
            CapitalFlow(
                datetime=datetime(2026, 8, 11, 12, tzinfo=timezone.utc),
                amount=Decimal("500"),
                flow_type=FlowType.CONTRIBUTION,
            )
        ],
    )

    assert history.points[1].time_weighted_return == Decimal("0")
    assert history.points[2].time_weighted_return == Decimal("0.09523809523809523809523809524")
