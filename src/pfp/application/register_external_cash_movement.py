"""Application use case for registering an external cash movement."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.domain.portfolio import Portfolio
from pfp.engine.portfolio_engine import PortfolioEngine


@dataclass(frozen=True, slots=True)
class RegisterExternalCashMovementRequest:
    datetime: datetime
    account_id: str
    amount: Decimal
    currency: str = "EUR"
    description: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.datetime, datetime):
            raise ValueError("External cash movement datetime must be a datetime")
        if not self.account_id.strip():
            raise ValueError("External cash movement account_id cannot be empty")
        if self.amount == Decimal("0"):
            raise ValueError("External cash movement amount must not be zero")
        if len(self.currency) != 3 or not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("Currency must be a three-letter uppercase code")


class RegisterExternalCashMovement:
    """Register an external cash movement through the portfolio domain API."""

    def execute(
        self,
        portfolio: Portfolio,
        request: RegisterExternalCashMovementRequest,
    ) -> ExternalCashMovement:
        movement = ExternalCashMovement(
            datetime=request.datetime,
            account_id=request.account_id,
            amount=request.amount,
            currency=request.currency,
            description=request.description,
        )
        PortfolioEngine().apply_external_cash_movement(portfolio, movement)
        return movement
