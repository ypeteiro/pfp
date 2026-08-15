from datetime import datetime
from decimal import Decimal

import pytest

from pfp.application.register_investment import RegisterInvestment, RegisterInvestmentRequest
from pfp.domain.portfolio import Portfolio


WHEN = datetime(2026, 8, 15, 10, 0)


def request(**overrides) -> RegisterInvestmentRequest:
    values = {
        "datetime": WHEN,
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


def test_register_investment_adds_to_existing_position():
    portfolio = Portfolio(cash=Decimal("1000"))
    RegisterInvestment().execute(portfolio, request())

    RegisterInvestment().execute(
        portfolio,
        request(shares=Decimal("1"), amount=Decimal("150"), price=Decimal("150")),
    )

    position = portfolio.positions["VWCE"]
    assert position.shares == Decimal("3")
    assert position.invested == Decimal("400")
    assert position.average_price == Decimal("400") / Decimal("3")
    assert portfolio.cash == Decimal("600")
    assert portfolio.invested == Decimal("400")


def test_register_investment_preserves_operation_metadata():
    portfolio = Portfolio(cash=Decimal("1000"))

    investment = RegisterInvestment().execute(
        portfolio,
        request(broker="Trade Republic", operation_id="order-123"),
    )

    assert investment.broker == "Trade Republic"
    assert investment.operation_id == "order-123"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("symbol", "", "Investment symbol cannot be empty"),
        ("shares", Decimal("0"), "Investment shares must be positive"),
        ("amount", Decimal("0"), "Investment amount must be positive"),
        ("price", Decimal("0"), "Investment price must be positive"),
        ("portfolio_class", "", "Investment portfolio_class cannot be empty"),
        ("broker", "", "Investment broker cannot be empty"),
        ("operation_id", "", "Investment operation_id cannot be empty"),
    ],
)
def test_register_investment_request_rejects_invalid_values(field, value, message):
    with pytest.raises(ValueError, match=message):
        request(**{field: value})


def test_register_investment_request_rejects_invalid_datetime():
    with pytest.raises(ValueError, match="Investment datetime must be a datetime"):
        request(datetime="2026-08-15T10:00:00")


def test_register_investment_rejects_insufficient_cash_without_mutating_portfolio():
    portfolio = Portfolio(cash=Decimal("100"))

    with pytest.raises(ValueError, match="Investment exceeds portfolio cash"):
        RegisterInvestment().execute(portfolio, request(amount=Decimal("101")))

    assert portfolio.cash == Decimal("100")
    assert portfolio.invested == Decimal("0")
    assert portfolio.positions == {}
