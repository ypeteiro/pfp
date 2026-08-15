from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.domain.snapshot import PortfolioSnapshot
from pfp.engine.history_engine import HistoryEngine


def _snapshot(day, value):
    return _snapshot_at(datetime(2026, 8, day, tzinfo=timezone.utc), value)


def _snapshot_at(timestamp, value):
    return PortfolioSnapshot(
        datetime=timestamp,
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


def test_history_orders_snapshots_and_calculates_changes():
    history = HistoryEngine().build([
        _snapshot(12, "10200"),
        _snapshot(10, "10000"),
        _snapshot(11, "10100"),
    ])

    assert [point.snapshot.datetime.day for point in history.points] == [10, 11, 12]
    assert [point.change for point in history.points] == [
        Decimal("0"), Decimal("100"), Decimal("100")
    ]
    assert history.total_change == Decimal("200")
    assert history.total_change_percent == Decimal("2")


def test_history_empty():
    history = HistoryEngine().build([])

    assert history.points == ()
    assert history.initial_value == Decimal("0")
    assert history.current_value == Decimal("0")
    assert history.total_change == Decimal("0")
    assert history.total_change_percent == Decimal("0")
    assert history.cumulative_capital_flow == Decimal("0")
    assert history.total_performance == Decimal("0")


def test_history_handles_zero_previous_value():
    history = HistoryEngine().build([
        _snapshot(10, "0"),
        _snapshot(11, "100"),
    ])

    assert history.points[1].change == Decimal("100")
    assert history.points[1].change_percent == Decimal("0")


def test_history_excludes_contributions_from_performance():
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

    point = history.points[1]

    assert point.capital_flow == Decimal("800")
    assert point.cumulative_capital_flow == Decimal("800")
    assert point.performance == Decimal("50")
    assert point.performance_percent == Decimal("0.25")
    assert history.total_performance == Decimal("50")


def test_history_includes_withdrawals_in_net_capital_flow():
    history = HistoryEngine().build(
        [_snapshot(10, "20000"), _snapshot(12, "19400")],
        [
            CapitalFlow(
                datetime=datetime(2026, 8, 11, tzinfo=timezone.utc),
                amount=Decimal("1000"),
                flow_type=FlowType.WITHDRAWAL,
            )
        ],
    )

    point = history.points[1]

    assert point.capital_flow == Decimal("-1000")
    assert point.cumulative_capital_flow == Decimal("-1000")
    assert point.performance == Decimal("400")


def test_history_exposes_xirr_for_single_annual_contribution():
    history = HistoryEngine().build(
        [
            _snapshot_at(datetime(2026, 1, 1, tzinfo=timezone.utc), "1000"),
            _snapshot_at(datetime(2027, 1, 1, tzinfo=timezone.utc), "1100"),
        ],
        [
            CapitalFlow(
                datetime=datetime(2026, 1, 1, tzinfo=timezone.utc),
                amount=Decimal("1000"),
                flow_type=FlowType.CONTRIBUTION,
            )
        ],
    )

    assert history.xirr is not None
    assert abs(history.xirr - Decimal("0.10")) < Decimal("1E-20")
    assert abs(history.xirr_percent - Decimal("10")) < Decimal("1E-18")


def test_history_xirr_accounts_for_withdrawal():
    history = HistoryEngine().build(
        [
            _snapshot_at(datetime(2026, 1, 1, tzinfo=timezone.utc), "1000"),
            _snapshot_at(datetime(2026, 7, 1, tzinfo=timezone.utc), "500"),
        ],
        [
            CapitalFlow(
                datetime=datetime(2026, 1, 1, tzinfo=timezone.utc),
                amount=Decimal("1000"),
                flow_type=FlowType.CONTRIBUTION,
            ),
            CapitalFlow(
                datetime=datetime(2026, 4, 1, tzinfo=timezone.utc),
                amount=Decimal("600"),
                flow_type=FlowType.WITHDRAWAL,
            ),
        ],
    )

    assert history.xirr is not None
    assert history.xirr < Decimal("0")


def test_history_xirr_is_none_without_capital_flows():
    history = HistoryEngine().build(
        [_snapshot(1, "1000"), _snapshot(2, "1100")]
    )

    assert history.xirr is None
    assert history.xirr_percent is None
