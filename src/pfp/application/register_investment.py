"""Application use case for registering an investment order."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio


@dataclass(frozen=True, slots=True)
class RegisterInvestmentRequest:
    datetime: datetime
    symbol: str
    shares: Decimal
    amount: Decimal
    price: Decimal
    portfolio_class: str
    broker: str = "Trade Republic"
    operation_id: str | None = None


class RegisterInvestment:
    """Translate an investment-order request into a domain operation."""

    def execute(self, portfolio: Portfolio, request: RegisterInvestmentRequest) -> Investment:
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
