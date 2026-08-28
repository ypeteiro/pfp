from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.reporting.patrimony_history import PatrimonyHistory


D1 = datetime(2026, 8, 1, 10)
D2 = datetime(2026, 8, 2, 10)


def _movement(when, movement_type, amount, shares=None, price=None):
    return SimpleNamespace(
        datetime=when,
        account_id="Trade Republic",
        account_type="DEFAULT",
        broker="Trade Republic",
        currency="EUR",
        type=movement_type,
        amount=Decimal(amount),
        fee=Decimal("-1") if movement_type == "BUY" else Decimal("0"),
        tax=Decimal("0"),
        symbol="VWCE" if movement_type == "BUY" else None,
        name="VWCE",
        asset_class="ETF",
        shares=Decimal(shares) if shares is not None else None,
        price=Decimal(price) if price is not None else None,
    )


def test_history_uses_trade_republic_buy_movements_for_invested_cost_and_market_value():
    movements = (
        _movement(D1, "TRANSFER_INSTANT_INBOUND", "1000"),
        _movement(D2, "BUY", "600", shares="10", price="60"),
    )
    contributions = (ExternalCashMovement(D1, "Trade Republic", Decimal("1000")),)

    snapshots = PatrimonyHistory.build(
        [D1, D2],
        movements=movements,
        capital_movements=contributions,
        prices={D1: {}, D2: {"VWCE": Decimal("70")}},
    )

    assert snapshots[0].cash == Decimal("1000")
    assert snapshots[0].invested_cost == Decimal("0")
    assert snapshots[0].market_value == Decimal("0")
    assert snapshots[1].cash == Decimal("399")
    assert snapshots[1].invested_cost == Decimal("601")
    assert snapshots[1].market_value == Decimal("700")
    assert snapshots[1].patrimony == Decimal("1099")
    assert snapshots[1].cumulative_contributed == Decimal("1000")
    assert snapshots[1].investment_gain == Decimal("99")
