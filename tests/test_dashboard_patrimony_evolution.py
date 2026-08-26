from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.dashboard_ui import _evolution_from_report


def _report(*movements):
    return PortfolioReport(
        cash=Decimal("0"),
        invested=Decimal("0"),
        market_value=Decimal("0"),
        total_value=Decimal("0"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("0"),
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
        positions=(),
        movements=tuple(movements),
    )


def _movement(datetime_value, movement_type, amount, category="CASH"):
    return SimpleNamespace(
        datetime=datetime_value,
        type=movement_type,
        amount=Decimal(amount),
        category=category,
        transaction_id=f"tx-{datetime_value.isoformat()}-{movement_type}",
    )


def test_dashboard_evolution_maps_trade_republic_inbound_transfers_to_contributions():
    report = _report(
        _movement(datetime(2026, 7, 29), "TRANSFER_INSTANT_INBOUND", "1000"),
        _movement(datetime(2026, 8, 3), "TRANSFER_INSTANT_INBOUND", "500"),
        _movement(datetime(2026, 8, 3), "TRANSFER_INSTANT_INBOUND", "4000"),
    )

    evolution = _evolution_from_report(report)

    assert evolution.total_contributions == Decimal("5500")
    assert evolution.total_withdrawals == Decimal("0")
    assert evolution.net_contributions == Decimal("5500")
    assert [point.cumulative_contributed for point in evolution.points] == [
        Decimal("1000"),
        Decimal("1500"),
        Decimal("5500"),
    ]


def test_dashboard_evolution_maps_trade_republic_outbound_transfers_to_withdrawals():
    report = _report(
        _movement(datetime(2026, 7, 29), "TRANSFER_INSTANT_INBOUND", "1000"),
        _movement(datetime(2026, 8, 10), "TRANSFER_INSTANT_OUTBOUND", "250"),
    )

    evolution = _evolution_from_report(report)

    assert evolution.total_contributions == Decimal("1000")
    assert evolution.total_withdrawals == Decimal("250")
    assert evolution.net_contributions == Decimal("750")
    assert [point.cumulative_contributed for point in evolution.points] == [
        Decimal("1000"),
        Decimal("750"),
    ]
