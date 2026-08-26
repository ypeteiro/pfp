from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ExternalCashMovement:
    datetime: datetime
    account_id: str
    amount: Decimal
    currency: str = "EUR"
    description: str | None = None

    def __post_init__(self):
        if not self.account_id:
            raise ValueError("Account id is required")
        if self.amount == 0:
            raise ValueError("Amount must not be zero")
        if len(self.currency) != 3 or not self.currency.isupper():
            raise ValueError("Currency must be a 3-letter uppercase code")
