from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class AccountTransfer:
    datetime: datetime
    source_account: str
    destination_account: str
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.source_account.strip():
            raise ValueError("Source account cannot be empty")
        if not self.destination_account.strip():
            raise ValueError("Destination account cannot be empty")
        if self.source_account == self.destination_account:
            raise ValueError("Source and destination accounts must differ")
        if self.amount <= 0:
            raise ValueError("Transfer amount must be greater than zero")
        if len(self.currency) != 3 or not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("Currency must be a three-letter uppercase code")
