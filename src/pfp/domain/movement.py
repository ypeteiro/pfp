from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class Movement:
    datetime: datetime
    date: datetime
    account_type: str
    broker: str
    category: str
    type: str
    asset_class: str | None
    name: str | None
    symbol: str | None
    shares: Decimal | None
    price: Decimal | None
    amount: Decimal
    fee: Decimal
    tax: Decimal
    currency: str
    original_amount: Decimal | None
    original_currency: str | None
    fx_rate: Decimal | None
    description: str | None
    transaction_id: str
    counterparty_name: str | None
    counterparty_iban: str | None
    payment_reference: str | None
    mcc_code: str | None