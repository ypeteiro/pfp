from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AccountOpeningBalance:
    account_id: str
    date: date
    amount: Decimal
    currency: str = "EUR"

    def __post_init__(self) -> None:
        if not self.account_id.strip():
            raise ValueError("Account id cannot be empty")
        if self.amount < 0:
            raise ValueError("Opening balance cannot be negative")
        if len(self.currency) != 3 or not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("Currency must be a three-letter uppercase code")
