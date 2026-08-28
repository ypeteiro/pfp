from datetime import datetime
from decimal import Decimal

from pfp.reporting.patrimony_history import PatrimonySnapshot
from pfp.reporting.patrimony_series import PatrimonySeries


D1 = datetime(2026, 1, 1, 10)
D2 = datetime(2026, 1, 2, 10)


def test_build_exposes_chart_values_in_history_order():
    snapshots = (
        PatrimonySnapshot(D1, Decimal("100"), Decimal("0"), Decimal("100"), Decimal("100"), Decimal("100"), Decimal("0")),
        PatrimonySnapshot(D2, Decimal("50"), Decimal("100"), Decimal("150"), Decimal("200"), Decimal("100"), Decimal("100")),
    )

    points = PatrimonySeries.build(snapshots)

    assert [(point.datetime, point.patrimony, point.cumulative_contributed, point.investment_gain, point.market_value) for point in points] == [
        (D1, Decimal("100"), Decimal("100"), Decimal("0"), Decimal("100")),
        (D2, Decimal("200"), Decimal("100"), Decimal("100"), Decimal("150")),
    ]


def test_build_empty_history_returns_empty_series():
    assert PatrimonySeries.build(()) == ()
