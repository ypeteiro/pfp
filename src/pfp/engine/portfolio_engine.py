from decimal import Decimal

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position


class PortfolioEngine:

    def build(self, movements):

        portfolio = Portfolio()

        portfolio.movements = movements

        for movement in movements:

            movement_type = movement.type.upper()

            if movement_type == "TRANSFER_INSTANT_INBOUND":

                portfolio.cash += movement.amount

                continue

            if movement_type != "BUY":
                continue

            symbol = movement.symbol

            if not symbol or str(symbol) == "nan":
                continue

            if symbol not in portfolio.positions:

                portfolio.positions[symbol] = Position(
                    symbol=symbol,
                    name=movement.name,
                )

            position = portfolio.positions[symbol]

            invested = -movement.amount

            position.shares += movement.shares

            position.invested += invested

            portfolio.invested += invested

            portfolio.cash -= invested

            position.average_price = (
                position.invested / position.shares
            )

        return portfolio