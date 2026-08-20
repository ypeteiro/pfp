from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.asset_catalog import AssetCatalog
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position


class PortfolioEngine:

    def build(self, movements, prices=None, investments=None, sales=None, opening_balances=None, account_transfers=None):
        portfolio = Portfolio()
        portfolio.movements = movements
        accounts = {}
        account_cash = {}
        unallocated_cash = Decimal("0")

        def account_key(movement):
            return movement.account_id or f"{movement.account_type}:{movement.broker}:{movement.currency}"

        def account_name(movement):
            return movement.account_id or movement.broker

        def ensure_account(account_id, broker, currency):
            if account_id not in accounts:
                accounts[account_id] = Account(name=account_id, broker=broker, currency=currency, account_id=account_id)
                account_cash[account_id] = Decimal("0")
                portfolio.account_positions.setdefault(account_id, {})

        def resolve_operation_account(operation, default_broker):
            if operation.account_id is not None:
                if operation.account_id not in accounts:
                    ensure_account(operation.account_id, operation.broker or default_broker, "EUR")
                return operation.account_id
            matches = [account_id for account_id, account in accounts.items() if account.broker == (operation.broker or default_broker)]
            if len(matches) == 1:
                return matches[0]
            if len(accounts) == 1:
                return next(iter(accounts))
            return None

        for movement in movements:
            key = account_key(movement)
            if key not in accounts:
                accounts[key] = Account(name=account_name(movement), broker=movement.broker, currency=movement.currency, account_id=key)
                account_cash[key] = Decimal("0")
                portfolio.account_positions.setdefault(key, {})

        for movement in movements:
            key = account_key(movement)
            if movement.type in {"TRANSFER_INSTANT_INBOUND", "TRANSFER_INBOUND"}:
                account_cash[key] += movement.amount
            elif movement.type in {"TRANSFER_INSTANT_OUTBOUND", "TRANSFER_OUTBOUND"}:
                account_cash[key] -= abs(movement.amount)
            elif movement.type == "BUY":
                if movement.symbol is None or movement.shares is None or movement.price is None:
                    continue
                asset = AssetCatalog.get_or_create(movement.symbol, movement.name, movement.asset_class)
                cost = abs(movement.amount) + abs(movement.fee) + abs(movement.tax)
                self._apply_buy(portfolio, movement.symbol, asset.name, movement.shares, cost, asset.portfolio_class, allow_insufficient_cash=True)
                self._apply_account_buy(portfolio, key, movement.symbol, asset.name, movement.shares, cost, asset.portfolio_class)
                account_cash[key] -= cost
            elif movement.type == "SELL":
                if movement.symbol is None or movement.shares is None or movement.amount is None:
                    continue
                proceeds = movement.amount + movement.fee + movement.tax
                self._apply_sell(portfolio, movement.symbol, movement.shares, proceeds)
                operation_account = self._resolve_account_position_id(
                    portfolio,
                    key,
                    movement.symbol,
                    movement.shares,
                )
                self._apply_account_sell(portfolio, operation_account, movement.symbol, movement.shares, proceeds)
                account_cash[operation_account] += proceeds

        if opening_balances is not None:
            for opening_balance in opening_balances:
                key = opening_balance.account_id
                ensure_account(key, key, opening_balance.currency)
                account_cash[key] += opening_balance.amount

        if account_transfers is not None:
            for transfer in account_transfers:
                ensure_account(transfer.source_account, transfer.source_account, transfer.currency)
                ensure_account(transfer.destination_account, transfer.destination_account, transfer.currency)
                if accounts[transfer.source_account].currency != transfer.currency:
                    raise ValueError("Transfer currency does not match source account currency")
                if accounts[transfer.destination_account].currency != transfer.currency:
                    raise ValueError("Transfer currency does not match destination account currency")
                if account_cash[transfer.source_account] < transfer.amount:
                    raise ValueError("Transfer exceeds source account cash")
                account_cash[transfer.source_account] -= transfer.amount
                account_cash[transfer.destination_account] += transfer.amount

        if investments is not None:
            for investment in investments:
                self._apply_buy(portfolio, investment.symbol, investment.symbol, investment.shares, investment.amount, investment.portfolio_class, allow_insufficient_cash=True)
                operation_account = resolve_operation_account(investment, "Trade Republic")
                if operation_account is not None:
                    self._apply_account_buy(portfolio, operation_account, investment.symbol, investment.symbol, investment.shares, investment.amount, investment.portfolio_class)
                    account_cash[operation_account] -= investment.amount
                else:
                    unallocated_cash -= investment.amount
        if sales is not None:
            for sale in sales:
                self._apply_sell(portfolio, sale.symbol, sale.shares, sale.amount)
                operation_account = resolve_operation_account(sale, "Trade Republic")
                if operation_account is not None:
                    self._apply_account_sell(
                        portfolio,
                        operation_account,
                        sale.symbol,
                        sale.shares,
                        sale.amount,
                        strict=False,
                    )
                    account_cash[operation_account] += sale.amount
                else:
                    unallocated_cash += sale.amount

        portfolio.invested = sum(position.invested for position in portfolio.positions.values())
        for position in portfolio.positions.values():
            if position.shares:
                position.average_price = position.invested / position.shares
            if prices is not None:
                market_price = prices.get(position.symbol)
                if market_price is not None:
                    position.market_price = market_price
            position.validate()

        for account_positions in portfolio.account_positions.values():
            for position in account_positions.values():
                if prices is not None:
                    market_price = prices.get(position.symbol)
                    if market_price is not None:
                        position.market_price = market_price
                position.validate()

        for key, account in accounts.items():
            account.balance = account_cash[key]
        portfolio.accounts = list(accounts.values())
        portfolio.cash = sum(account_cash.values(), Decimal("0")) + unallocated_cash
        return portfolio

    def apply_investment(self, portfolio, investment):
        self._apply_buy(portfolio, investment.symbol, investment.symbol, investment.shares, investment.amount, investment.portfolio_class)
        account = self._resolve_portfolio_account(portfolio, investment.account_id, investment.broker)
        if account is not None:
            account.balance -= investment.amount
            self._apply_account_buy(portfolio, account.account_id, investment.symbol, investment.symbol, investment.shares, investment.amount, investment.portfolio_class)
        portfolio.invested = sum(position.invested for position in portfolio.positions.values())
        portfolio.positions[investment.symbol].validate()
        return portfolio

    def apply_sale(self, portfolio, sale):
        self._apply_sell(portfolio, sale.symbol, sale.shares, sale.amount)
        account = self._resolve_portfolio_account(portfolio, sale.account_id, sale.broker)
        if account is not None:
            account.balance += sale.amount
            self._apply_account_sell(portfolio, account.account_id, sale.symbol, sale.shares, sale.amount)
        portfolio.invested = sum(position.invested for position in portfolio.positions.values())
        portfolio.positions[sale.symbol].validate()
        return portfolio

    @staticmethod
    def _resolve_portfolio_account(portfolio, account_id, broker):
        if account_id is not None:
            for account in portfolio.accounts:
                if account.account_id == account_id:
                    return account
            raise ValueError(f"Account not found: {account_id}")
        matches = [account for account in portfolio.accounts if account.broker == broker]
        if len(matches) == 1:
            return matches[0]
        if len(portfolio.accounts) == 1:
            return portfolio.accounts[0]
        return None

    @staticmethod
    def _resolve_account_position_id(portfolio, account_id, symbol, shares):
        positions = portfolio.account_positions.get(account_id, {})
        if symbol in positions and positions[symbol].shares >= shares:
            return account_id
        candidates = []
        for candidate_id, candidate_positions in portfolio.account_positions.items():
            position = candidate_positions.get(symbol)
            if position is not None and position.shares >= shares:
                candidates.append(candidate_id)
        if len(candidates) == 1:
            return candidates[0]
        return account_id

    @staticmethod
    def _apply_account_buy(portfolio, account_id, symbol, name, shares, amount, portfolio_class=None):
        positions = portfolio.account_positions.setdefault(account_id, {})
        shares = Decimal(str(shares))
        amount = Decimal(str(amount))
        position = positions.get(symbol)
        if position is None:
            positions[symbol] = Position(symbol, name, shares, amount, amount / shares, portfolio_class)
            return
        position.shares += shares
        position.invested += amount
        position.average_price = position.invested / position.shares
        if portfolio_class is not None:
            position.portfolio_class = portfolio_class
        position.validate()

    @staticmethod
    def _apply_account_sell(portfolio, account_id, symbol, shares, amount, strict=True):
        positions = portfolio.account_positions.setdefault(account_id, {})
        shares = Decimal(str(shares))
        amount = Decimal(str(amount))
        position = positions.get(symbol)
        if position is None or position.shares < shares:
            if strict:
                raise ValueError(f"Insufficient account shares for {symbol}")
            return
        cost_basis = position.average_price * shares
        position.shares -= shares
        position.invested -= cost_basis
        if position.shares == 0:
            position.invested = Decimal("0")
            position.average_price = Decimal("0")
        else:
            position.average_price = position.invested / position.shares
        position.validate()
        if position.shares == 0:
            del positions[symbol]

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
