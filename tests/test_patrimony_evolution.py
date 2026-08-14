from datetime import datetime
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.reporting.patrimony_evolution import PatrimonyEvolution


def test_patrimony_evolution_accumulates_contributions_and_withdrawals():
    flows = [
        CapitalFlow(datetime(2026, 2, 1), Decimal("800"), FlowType.CONTRIBUTION, "b"),
        CapitalFlow(datetime(2026, 1, 1), Decimal("1000"), FlowType.CONTRIBUTION, "a"),
        CapitalFlow(datetime(2026, 3, 1), Decimal("200"), FlowType.WITHDRAWAL, "c"),
    ]
    evolution = PatrimonyEvolution.from_capital_flows(flows)

    assert evolution.total_contributions == Decimal("1800")
    assert evolution.total_withdrawals == Decimal("200")
    assert evolution.net_contributions == Decimal("1600")
    assert [p.cumulative_contributed for p in evolution.points] == [Decimal("1000"), Decimal("1800"), Decimal("1600")]
