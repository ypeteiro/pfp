from decimal import Decimal

from pfp.domain.investment import Investment


class InvestmentEngine:

    def create(
        self,
        symbol,
        shares,
        amount,
        portfolio_class,
        datetime,
        broker="Trade Republic",
        account_id=None,
    ):
        shares = Decimal(str(shares))
        amount = Decimal(str(amount))

        if not symbol:
            raise ValueError(
                "Symbol must not be empty"
            )

        if shares <= 0:
            raise ValueError(
                "Shares must be greater than zero"
            )

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero"
            )

        if not portfolio_class:
            raise ValueError(
                "Portfolio class must not be empty"
            )

        price = amount / shares

        return Investment(
            datetime=datetime,
            symbol=symbol,
            shares=shares,
            amount=amount,
            price=price,
            portfolio_class=portfolio_class,
            broker=broker,
            account_id=account_id,
        )
