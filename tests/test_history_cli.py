from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.domain.snapshot import PortfolioSnapshot
from pfp.engine.history_engine import HistoryEngine


def _snapshot(day, value):
    return PortfolioSnapshot(
        datetime=datetime(2026, 8, day, tzinfo=timezone.utc),
        total_value=Decimal(str(value)),
        cash=Decimal("0"),
        invested_cost=Decimal("0"),
        market_value=Decimal(str(value)),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal(str(value)),
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
    )


def test_history_engine_distinguishes_capital_flow_from_performance():
    history = HistoryEngine().build(
        [_snapshot(10, "20000"), _snapshot(11, "20850")],
        [
            CapitalFlow(
                datetime=datetime(2026, 8, 11, tzinfo=timezone.utc),
                amount=Decimal("800"),
                flow_type=FlowType.CONTRIBUTION,
            )
        ],
    )

    point = history.points[-1]

    assert point.capital_flow == Decimal("800")
    assert point.cumulative_capital_flow == Decimal("800")
    assert point.performance == Decimal("50")
    assert point.performance_percent == Decimal("0.25")
    assert history.total_performance == Decimal("50")


def test_history_engine_accounts_for_withdrawal():
    history = HistoryEngine().build(
        [_snapshot(10, "20000"), _snapshot(11, "19100")],
        [
            CapitalFlow(
                datetime=datetime(2026, 8, 11, tzinfo=timezone.utc),
                amount=Decimal("1000"),
                flow_type=FlowType.WITHDRAWAL,
            )
        ],
    )

    assert history.points[-1].capital_flow == Decimal("-1000")
    assert history.points[-1].performance == Decimal("100")
