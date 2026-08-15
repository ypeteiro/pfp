"""Application use case for registering an investment order."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio


@dataclass(frozen=True, slots=True)
class RegisterInvestmentRequest:
    """Validated input for registering one investment order.

    The application request deliberately mirrors the domain investment data.  Keeping
    validation here gives callers such as the web layer a single, domain-independent
    contract before any portfolio state is changed.
    """

    datetime: datetime
    symbol: str
    shares: Decimal
    amount: Decimal
    price: Decimal
    portfolio_class: str
    broker: str = "Trade Republic"
    operation_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.datetime, datetime):
            raise ValueError("Investment datetime must be a datetime")
        if not self.symbol.strip():
            raise ValueError("Investment symbol cannot be empty")
        if self.shares <= Decimal("0"):
            raise ValueError("Investment shares must be positive")
        if self.amount <= Decimal("0"):
            raise ValueError("Investment amount must be positive")
        if self.price <= Decimal("0"):
            raise ValueError("Investment price must be positive")
        if not self.portfolio_class.strip():
            raise ValueError("Investment portfolio_class cannot be empty")
        if not self.broker.strip():
            raise ValueError("Investment broker cannot be empty")
        if self.operation_id is not None and not self.operation_id.strip():
            raise ValueError("Investment operation_id cannot be empty")


class RegisterInvestment:
    """Register an investment through the portfolio domain API."""

    def execute(self, portfolio: Portfolio, request: RegisterInvestmentRequest) -> Investment:
        """Apply a validated investment request to ``portfolio``.

        The application service owns no portfolio state and knows nothing about HTTP,
        persistence, or presentation.  This makes it safe to reuse from the future web
        form, CLI, or import workflow.
        """
        investment = Investment(
            datetime=request.datetime,
            symbol=request.symbol,
            shares=request.shares,
            amount=request.amount,
            price=request.price,
            portfolio_class=request.portfolio_class,
            broker=request.broker,
            operation_id=request.operation_id,
        )
        portfolio.add_investment(investment)
        return investment
