from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.asset_catalog import AssetCatalog
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position


class PortfolioEngine:

    def build(self, movements, prices=None, investments=None, sales=None):
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
                if movement.symbol is None or movement.shares is None or movement.price is None:
                    continue
                asset = AssetCatalog.get_or_create(movement.symbol, movement.name, movement.asset_class)
                self._apply_buy(
                    portfolio,
                    movement.symbol,
                    asset.name,
                    movement.shares,
                    abs(movement.amount) + abs(movement.fee) + abs(movement.tax),
                    asset.portfolio_class,
                )
            elif movement.type == "SELL":
                if movement.symbol is None or movement.shares is None or movement.amount is None:
                    continue
                self._apply_sell(
                    portfolio,
                    movement.symbol,
                    movement.shares,
                    movement.amount + movement.fee + movement.tax,
                )
        if investments is not None:
            for investment in investments:
                self._apply_buy(
                    portfolio,
                    investment.symbol,
                    investment.symbol,
                    investment.shares,
                    investment.amount,
                    investment.portfolio_class,
                    allow_insufficient_cash=True,
                )
        if sales is not None:
            for sale in sales:
                self._apply_sell(
                    portfolio,
                    sale.symbol,
                    sale.shares,
                    sale.amount,
                )
        portfolio.invested = sum(position.invested for position in portfolio.positions.values())
        for position in portfolio.positions.values():
            if position.shares:
                position.average_price = position.invested / position.shares
            if prices is not None:
                market_price = prices.get(position.symbol)
                if market_price is not None:
                    position.market_price = market_price
            position.validate()
        for account in portfolio.accounts:
            account.balance = portfolio.cash
        return portfolio

    def apply_investment(self, portfolio, investment):
        self._apply_buy(portfolio, investment.symbol, investment.symbol, investment.shares, investment.amount, investment.portfolio_class)
        portfolio.invested = sum(position.invested for position in portfolio.positions.values())
        portfolio.positions[investment.symbol].validate()
        return portfolio

    def apply_sale(self, portfolio, sale):
        self._apply_sell(portfolio, sale.symbol, sale.shares, sale.amount)
        portfolio.invested = sum(position.invested for position in portfolio.positions.values())
        portfolio.positions[sale.symbol].validate()
        return portfolio

    def _apply_buy(self, portfolio, symbol, name, shares, amount, portfolio_class=None, allow_insufficient_cash=False):
        shares = Decimal(str(shares))
        amount = Decimal(str(amount))
        if shares <= 0:
            raise ValueError("Shares must be greater than zero")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if not allow_insufficient_cash and portfolio.cash < amount:
            raise ValueError("Insufficient cash")
        if symbol not in portfolio.positions:
            portfolio.positions[symbol] = Position(symbol=symbol, name=name, shares=Decimal("0"), invested=Decimal("0"), portfolio_class=portfolio_class)
        position = portfolio.positions[symbol]
        position.shares += shares
        position.invested += amount
        if portfolio_class is not None:
            position.portfolio_class = portfolio_class
        portfolio.cash -= amount
        if position.shares:
            position.average_price = position.invested / position.shares
        position.validate()

    def _apply_sell(self, portfolio, symbol, shares, amount):
        shares = Decimal(str(shares))
        amount = Decimal(str(amount))
        if shares <= 0:
            raise ValueError("Shares must be greater than zero")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if symbol not in portfolio.positions:
            raise ValueError("Symbol is not present in portfolio")
        position = portfolio.positions[symbol]
        if position.shares <= 0:
            raise ValueError("Position has no shares")
        if shares > position.shares:
            raise ValueError("Insufficient shares")
        average_price = position.invested / position.shares
        invested_reduction = average_price * shares
        position.shares -= shares
        position.invested -= invested_reduction
        portfolio.cash += amount
        portfolio.realized_gain_loss += amount - invested_reduction
        if position.shares:
            position.average_price = position.invested / position.shares
        else:
            position.shares = Decimal("0")
            position.invested = Decimal("0")
            position.average_price = Decimal("0")
        position.validate()
