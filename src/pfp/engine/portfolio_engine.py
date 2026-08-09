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

                # Trade Republic reports BUY amounts as negative.
                # Cash therefore decreases by the absolute purchase amount.
                portfolio.cash += movement.amount

                position.invested += abs(movement.amount)

            elif movement.type == "SELL":

                if movement.symbol is None:
                    continue

                if movement.shares is None:
                    continue

                if movement.amount is None:
                    continue

                symbol = movement.symbol

                if symbol not in portfolio.positions:
                    continue

                position = portfolio.positions[symbol]

                if position.shares <= 0:
                    continue

                average_price = position.invested / position.shares
                invested_reduction = average_price * movement.shares

                position.shares -= movement.shares
                position.invested -= invested_reduction

                # Trade Republic reports SELL amounts as positive.
                portfolio.cash += movement.amount

        portfolio.invested = sum(
            position.invested
            for position in portfolio.positions.values()
        )

        for account in portfolio.accounts:
            account.balance = portfolio.cash

        for position in portfolio.positions.values():

            if position.shares:
                position.average_price = (
                    position.invested / position.shares
                )

        return portfolio
