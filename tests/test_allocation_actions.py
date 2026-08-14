from decimal import Decimal

from pfp.excel.allocation_actions import build_allocation_rows


def test_allocation_actions_classifies_deviation():
    rows = build_allocation_rows(
        values={"RV": Decimal("700"), "RF": Decimal("200"), "GOLD": Decimal("100")},
        targets={"RV": Decimal("0.75"), "RF": Decimal("0.20"), "GOLD": Decimal("0.05")},
        total=Decimal("1000"),
    )
    assert rows[0].current_weight == Decimal("0.7")
    assert rows[0].action == "Aumentar"
    assert rows[1].action == "Mantener"
    assert rows[2].action == "Reducir"


def test_allocation_actions_handles_zero_total():
    rows = build_allocation_rows(
        values={"RV": Decimal("0")},
        targets={"RV": Decimal("0.75")},
        total=Decimal("0"),
    )
    assert rows[0].current_weight == Decimal("0")
    assert rows[0].action == "Aumentar"
