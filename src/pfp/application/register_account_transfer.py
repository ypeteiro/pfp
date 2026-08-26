"""Application use case for registering an internal account transfer."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.account_transfer import AccountTransfer
from pfp.domain.portfolio import Portfolio


@dataclass(frozen=True, slots=True)
class RegisterAccountTransferRequest:
    datetime: datetime
    source_account: str
    destination_account: str
    amount: Decimal
    currency: str = "EUR"

    def __post_init__(self) -> None:
        if not isinstance(self.datetime, datetime):
            raise ValueError("Account transfer datetime must be a datetime")
        if not self.source_account.strip():
            raise ValueError("Source account cannot be empty")
        if not self.destination_account.strip():
            raise ValueError("Destination account cannot be empty")
        if self.amount <= 0:
            raise ValueError("Transfer amount must be greater than zero")
        if len(self.currency) != 3 or not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("Currency must be a three-letter uppercase code")


class RegisterAccountTransfer:
    """Register an internal transfer and apply it to the account balances."""

    def execute(self, portfolio: Portfolio, request: RegisterAccountTransferRequest) -> AccountTransfer:
        transfer = AccountTransfer(
            datetime=request.datetime,
            source_account=request.source_account,
            destination_account=request.destination_account,
            amount=request.amount,
            currency=request.currency,
        )
        source = next((account for account in portfolio.accounts if account.id == transfer.source_account), None)
        destination = next((account for account in portfolio.accounts if account.id == transfer.destination_account), None)
        if source is None:
            raise ValueError(f"Cuenta origen desconocida: {transfer.source_account}")
        if destination is None:
            raise ValueError(f"Cuenta destino desconocida: {transfer.destination_account}")
        if source.currency != transfer.currency or destination.currency != transfer.currency:
            raise ValueError("Account transfer currency does not match account currency")
        if source.balance < transfer.amount:
            raise ValueError("Insufficient cash in source account")
        source.balance -= transfer.amount
        destination.balance += transfer.amount
        return transfer
