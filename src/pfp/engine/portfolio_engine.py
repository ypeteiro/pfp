from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position


class PortfolioEngine:

    def build(self, movements):

        portfolio = Portfolio()
        portfolio.movements = movements

        accounts = {}

        for movement in movements:
            if movement.account_type not in accounts:
                accounts[movement.account_type] = Account(
                    name=movement.broker,
                    broker=movement.broker,
                    currency=movement.currency,
                )

        portfolio.accounts = list(accounts.values())

        for movement in movements:

            if movement.type == "TRANSFER_INSTANT_INBOUND":
                portfolio.cash += movement.amount

            elif movement.type == "BUY":

                if movement.symbol is None:
                    continue

                if movement.shares is None:
                    continue

                if movement.price is None:
                    continue

                symbol = movement.symbol

                if symbol not in portfolio.positions:
                    portfolio.positions[symbol] = Position(
                        symbol=symbol,
                        name=movement.name or symbol,
                        shares=Decimal("0"),
                        invested=Decimal("0"),
                    )

                position = portfolio.positions[symbol]

                position.shares += movement.shares
                position.invested += abs(movement.amount)

        portfolio.invested = sum(
            position.invested
            for position in portfolio.positions.values()
        )

        portfolio.cash -= portfolio.invested

        for account in portfolio.accounts:
            account.balance = portfolio.cash

        for position in portfolio.positions.values():
            if position.shares:
                position.average_price = (
                    position.invested / position.shares
                )

        return portfolio