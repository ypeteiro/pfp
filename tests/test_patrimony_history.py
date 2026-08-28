from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.reporting.historical_prices import MappingHistoricalPriceProvider
from pfp.reporting.patrimony_history import PatrimonyHistory


def _movement(when, movement_type, amount, symbol=None, shares=None, price=None):
    return SimpleNamespace(
        datetime=when,
        account_type="DEFAULT",
        broker="Trade Republic",
        currency="EUR",
        type=movement_type,
        amount=Decimal(amount),
        fee=Decimal("0"),
        tax=Decimal("0"),
        symbol=symbol,
        shares=Decimal(shares) if shares is not None else None,
        price=Decimal(price) if price is not None else None,
        name="Test ETF" if symbol else None,
        asset_class="ETF" if symbol else None,
    )


def test_patrimony_history_reconstructs_patrimony_and_invested_cost():
    first = datetime(2026, 7, 1)
    second = datetime(2026, 8, 1)
    movements = [
        _movement(first, "TRANSFER_INSTANT_INBOUND", "1000"),
        _movement(second, "BUY", "800", "TEST", "8", "100"),
    ]
    flows = [CapitalFlow(first, Decimal("1000"), FlowType.CONTRIBUTION, "in-1")]
    prices = {
        first: {},
        second: {"TEST": Decimal("120")},
    }

    snapshots = PatrimonyHistory.build(
        [first, second],
        movements=movements,
        capital_flows=flows,
        price_provider=MappingHistoricalPriceProvider(prices),
    )

    assert snapshots[0].patrimony == Decimal("1000")
    assert snapshots[0].invested_cost == Decimal("0")
    assert snapshots[1].cash == Decimal("200")
    assert snapshots[1].invested_cost == Decimal("800")
    assert snapshots[1].market_value == Decimal("960")
    assert snapshots[1].patrimony == Decimal("1160")
    assert snapshots[1].cumulative_contributed == Decimal("1000")
    assert snapshots[1].investment_gain == Decimal("160")
