from datetime import datetime
from decimal import Decimal

import pytest

from pfp.application.register_investment import RegisterInvestment, RegisterInvestmentRequest
from pfp.domain.portfolio import Portfolio


def request(**overrides) -> RegisterInvestmentRequest:
    values = {
        "datetime": datetime(2026, 8, 15, 10, 0),
        "symbol": "VWCE",
        "shares": Decimal("2"),
        "amount": Decimal("250"),
        "price": Decimal("125"),
        "portfolio_class": "RV",
    }
    values.update(overrides)
    return RegisterInvestmentRequest(**values)


def test_register_investment_delegates_to_portfolio():
    portfolio = Portfolio(cash=Decimal("1000"))

    investment = RegisterInvestment().execute(portfolio, request())

    assert investment.symbol == "VWCE"
    assert portfolio.cash == Decimal("750")
    assert portfolio.invested == Decimal("250")
    assert portfolio.positions["VWCE"].shares == Decimal("2")


def test_register_investment_preserves_operation_metadata():
    portfolio = Portfolio(cash=Decimal("1000"))

    investment = RegisterInvestment().execute(
        portfolio,
        request(broker="Trade Republic", operation_id="order-123"),
    )

    assert investment.broker == "Trade Republic"
    assert investment.operation_id == "order-123"


def test_register_investment_rejects_insufficient_cash():
    portfolio = Portfolio(cash=Decimal("100"))

    with pytest.raises(ValueError, match="Investment exceeds portfolio cash"):
        RegisterInvestment().execute(portfolio, request(amount=Decimal("101")))

    assert portfolio.cash == Decimal("100")
    assert portfolio.invested == Decimal("0")
    assert portfolio.positions == {}
