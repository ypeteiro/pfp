from datetime import datetime
from decimal import Decimal

from pfp.domain.account_transfer import AccountTransfer
from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.domain.investment import Investment
from pfp.domain.sale import Sale
from pfp.reporting.patrimony_history import PatrimonyHistory


D1 = datetime(2026, 1, 1, 10)
D2 = datetime(2026, 1, 2, 10)
D3 = datetime(2026, 1, 3, 10)
D4 = datetime(2026, 1, 4, 10)
D5 = datetime(2026, 1, 5, 10)


def test_external_contribution_increases_cash_and_contributed_capital():
    snapshots = PatrimonyHistory.build(
        [D1, D2],
        external_cash_movements=[ExternalCashMovement(D2, "abanca", Decimal("1000"))],
    )

    assert snapshots[0].patrimony == Decimal("0")
    assert snapshots[1].cash == Decimal("1000")
    assert snapshots[1].patrimony == Decimal("1000")
    assert snapshots[1].cumulative_contributed == Decimal("1000")
    assert snapshots[1].investment_gain == Decimal("0")


def test_investment_purchase_changes_cash_into_market_value_without_changing_patrimony():
    snapshots = PatrimonyHistory.build(
        [D1, D2, D3],
        opening_cash=Decimal("1000"),
        investments=[Investment(D2, "VWCE", Decimal("10"), Decimal("1000"), Decimal("100"), "EQUITY")],
        prices={D2: {"VWCE": Decimal("100")}, D3: {"VWCE": Decimal("110")}},
    )

    assert snapshots[1].cash == Decimal("0")
    assert snapshots[1].market_value == Decimal("1000")
    assert snapshots[1].patrimony == Decimal("1000")
    assert snapshots[2].market_value == Decimal("1100")
    assert snapshots[2].patrimony == Decimal("1100")
    assert snapshots[2].investment_gain == Decimal("1100")


def test_withdrawal_reduces_patrimony_and_contributed_capital():
    snapshots = PatrimonyHistory.build(
        [D1, D2],
        opening_cash=Decimal("1000"),
        external_cash_movements=[ExternalCashMovement(D2, "abanca", Decimal("-300"))],
    )

    assert snapshots[1].cash == Decimal("700")
    assert snapshots[1].patrimony == Decimal("700")
    assert snapshots[1].cumulative_contributed == Decimal("-300")


def test_internal_transfer_does_not_change_consolidated_patrimony():
    snapshots = PatrimonyHistory.build(
        [D1, D2],
        opening_cash=Decimal("1000"),
        account_transfers=[AccountTransfer(D2, "abanca", "trade_republic", Decimal("300"), "EUR")],
    )

    assert snapshots[0].patrimony == Decimal("1000")
    assert snapshots[1].patrimony == Decimal("1000")


def test_sale_replaces_market_value_with_cash_without_creating_gain():
    snapshots = PatrimonyHistory.build(
        [D1, D2, D3],
        opening_cash=Decimal("1000"),
        investments=[Investment(D2, "VWCE", Decimal("10"), Decimal("1000"), Decimal("100"), "EQUITY")],
        sales=[Sale(D3, "VWCE", Decimal("10"), Decimal("1200"), Decimal("120"))],
        prices={D2: {"VWCE": Decimal("100")}, D3: {"VWCE": Decimal("120")}},
    )

    assert snapshots[1].patrimony == Decimal("1000")
    assert snapshots[2].cash == Decimal("1200")
    assert snapshots[2].market_value == Decimal("0")
    assert snapshots[2].patrimony == Decimal("1200")
    assert snapshots[2].investment_gain == Decimal("1200")


def test_complete_history_separates_contributions_from_investment_performance():
    snapshots = PatrimonyHistory.build(
        [D1, D2, D3, D4, D5],
        opening_cash=Decimal("0"),
        external_cash_movements=[
            ExternalCashMovement(D1, "abanca", Decimal("1000"), description="Primera aportación"),
            ExternalCashMovement(D4, "abanca", Decimal("500"), description="Segunda aportación"),
            ExternalCashMovement(D5, "abanca", Decimal("-200"), description="Retirada"),
        ],
        investments=[
            Investment(D2, "VWCE", Decimal("10"), Decimal("1000"), Decimal("100"), "EQUITY"),
        ],
        prices={
            D2: {"VWCE": Decimal("100")},
            D3: {"VWCE": Decimal("120")},
            D4: {"VWCE": Decimal("120")},
            D5: {"VWCE": Decimal("130")},
        },
        account_transfers=[
            AccountTransfer(D3, "abanca", "trade_republic", Decimal("300"), "EUR"),
        ],
    )

    assert snapshots[0].patrimony == Decimal("1000")
    assert snapshots[0].cumulative_contributed == Decimal("1000")
    assert snapshots[0].investment_gain == Decimal("0")

    assert snapshots[1].patrimony == Decimal("1000")
    assert snapshots[1].cumulative_contributed == Decimal("1000")
    assert snapshots[1].investment_gain == Decimal("0")

    assert snapshots[2].patrimony == Decimal("1200")
    assert snapshots[2].cumulative_contributed == Decimal("1000")
    assert snapshots[2].investment_gain == Decimal("200")

    assert snapshots[3].patrimony == Decimal("1700")
    assert snapshots[3].cumulative_contributed == Decimal("1500")
    assert snapshots[3].investment_gain == Decimal("200")

    assert snapshots[4].patrimony == Decimal("1600")
    assert snapshots[4].cumulative_contributed == Decimal("1300")
    assert snapshots[4].investment_gain == Decimal("300")
