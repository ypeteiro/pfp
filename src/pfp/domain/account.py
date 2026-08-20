from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class Account:
    name: str
    broker: str
    currency: str = "EUR"
    balance: Decimal = Decimal("0")
    account_id: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Account name cannot be empty")
        if not self.broker.strip():
            raise ValueError("Account broker cannot be empty")
        if self.account_id is not None and not self.account_id.strip():
            raise ValueError("Account id cannot be empty")
        if len(self.currency) != 3 or not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("Currency must be a three-letter uppercase code")

    @property
    def id(self) -> str:
        """Stable account identity within a portfolio."""
        return self.account_id or self.name
