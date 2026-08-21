from decimal import Decimal

import pytest

from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.engine.rebalance_engine import RebalanceEngine


def test_rebalance_scopes_positions_and_cash_to_selected_account():
    portfolio = Portfolio(cash=Decimal("0"))
    portfolio.accounts = [
        Account(name="Trade Republic", broker="Trade Republic", account_id="Trade Republic", balance=Decimal("1000")),
        Account(name="Other", broker="Other", account_id="Other", balance=Decimal("9000")),
    ]
    portfolio.account_positions = {
        "Trade Republic": {
            "EQUITY": Position("EQUITY", "Equity", Decimal("10"), Decimal("1000"), Decimal("100"), "EQUITY", Decimal("100")),
        },
        "Other": {
            "BOND": Position("BOND", "Bond", Decimal("80"), Decimal("8000"), Decimal("100"), "FIXED_INCOME", Decimal("100")),
        },
    }
    portfolio.positions = {
        "EQUITY": portfolio.account_positions["Trade Republic"]["EQUITY"],
        "BOND": portfolio.account_positions["Other"]["BOND"],
    }

    rebalance = RebalanceEngine().rebalance(portfolio, account_id="Trade Republic")

    assert rebalance.rebalanceable_value == Decimal("2000")
    assert all(order.symbol == "EQUITY" for order in rebalance.orders)
    assert all(order.symbol != "BOND" for order in rebalance.orders)


def test_rebalance_rejects_unknown_account():
    portfolio = Portfolio(cash=Decimal("0"))
    portfolio.accounts = [
        Account(name="Trade Republic", broker="Trade Republic", account_id="Trade Republic", balance=Decimal("1000")),
    ]

    with pytest.raises(ValueError, match="Rebalance account not found: Missing"):
        RebalanceEngine().rebalance(portfolio, account_id="Missing")
