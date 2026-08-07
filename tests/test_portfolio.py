from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.portfolio import Portfolio


def test_portfolio_can_contain_accounts():
    account = Account(
        name="Trade Republic",
        broker="Trade Republic",
        currency="EUR",
        balance=Decimal("3603.39"),
    )

    portfolio = Portfolio(
        accounts=[account],
    )

    assert len(portfolio.accounts) == 1
    assert portfolio.accounts[0].name == "Trade Republic"
    assert portfolio.accounts[0].balance == Decimal("3603.39")