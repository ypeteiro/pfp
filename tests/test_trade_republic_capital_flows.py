from datetime import datetime, timezone
from decimal import Decimal

from pfp.domain.movement import Movement
from pfp.domain.capital_flow import FlowType
from pfp.importers.trade_republic import TradeRepublicImporter


def _movement(movement_type, amount, category="CASH"):
    return Movement(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        date=datetime(2026, 8, 10),
        account_type="DEFAULT",
        broker="Trade Republic",
        category=category,
        type=movement_type,
        asset_class=None,
        name=None,
        symbol=None,
        shares=None,
        price=None,
        amount=Decimal(str(amount)),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description=None,
        transaction_id=f"tx-{movement_type}",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )


def test_extracts_inbound_transfer_as_contribution():
    flows = TradeRepublicImporter.capital_flows_from_movements(
        [_movement("TRANSFER_INSTANT_INBOUND", "1000")]
    )

    assert len(flows) == 1
    assert flows[0].flow_type == FlowType.CONTRIBUTION
    assert flows[0].amount == Decimal("1000")
    assert flows[0].signed_amount == Decimal("1000")


def test_extracts_outbound_transfer_as_withdrawal():
    flows = TradeRepublicImporter.capital_flows_from_movements(
        [_movement("TRANSFER_INSTANT_OUTBOUND", "250")]
    )

    assert len(flows) == 1
    assert flows[0].flow_type == FlowType.WITHDRAWAL
    assert flows[0].amount == Decimal("250")
    assert flows[0].signed_amount == Decimal("-250")


def test_ignores_non_cash_movements():
    flows = TradeRepublicImporter.capital_flows_from_movements(
        [_movement("TRANSFER_INSTANT_INBOUND", "1000", category="INVESTMENT")]
    )

    assert flows == []


def test_ignores_cash_movements_that_are_not_capital_flows():
    flows = TradeRepublicImporter.capital_flows_from_movements(
        [_movement("INTEREST_PAYMENT", "5")]
    )

    assert flows == []
