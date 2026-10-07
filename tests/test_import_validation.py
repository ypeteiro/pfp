from datetime import datetime
from decimal import Decimal

from pfp.domain.movement import Movement
from pfp.importers.validation import validate_movements


def _movement(*, shares: Decimal | None, price: Decimal | None = Decimal("100")) -> Movement:
    return Movement(
        datetime=datetime(2026, 1, 1),
        date=datetime(2026, 1, 1),
        account_type="BROKER",
        broker="Trade Republic",
        category="INVESTMENT",
        type="SELL",
        asset_class="EQUITY",
        name="Test asset",
        symbol="TEST",
        shares=shares,
        price=price,
        amount=Decimal("-100"),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description=None,
        transaction_id="tx-1",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )


def test_validate_movements_allows_negative_shares_for_sell():
    issues = validate_movements([_movement(shares=Decimal("-0.329554"))])

    assert issues == ()


def test_validate_movements_rejects_negative_price():
    issues = validate_movements([_movement(shares=Decimal("-1"), price=Decimal("-100"))])

    assert [issue.code for issue in issues] == ["NEGATIVE_PRICE"]
