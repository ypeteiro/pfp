from datetime import datetime, timezone
from decimal import Decimal

import pytest

from pfp.application.register_sale import RegisterSale, RegisterSaleRequest
from pfp.domain.portfolio import Portfolio


def request(**overrides):
    values = {
        "datetime": datetime(2026, 8, 17, 10, 30, tzinfo=timezone.utc),
        "symbol": "VWCE",
        "shares": Decimal("2"),
        "amount": Decimal("300"),
        "price": Decimal("150"),
        "broker": "Trade Republic",
        "operation_id": "sale-1",
    }
    values.update(overrides)
    return RegisterSaleRequest(**values)


def test_register_sale_updates_portfolio_and_returns_sale():
    portfolio = Portfolio(cash=Decimal("400"))
    from pfp.domain.investment import Investment
    portfolio.add_investment(
        Investment(
            datetime=datetime(2026, 8, 1, tzinfo=timezone.utc),
            symbol="VWCE",
            shares=Decimal("4"),
            amount=Decimal("400"),
            price=Decimal("100"),
            portfolio_class="Renta Variable",
        )
    )

    sale = RegisterSale().execute(portfolio, request())

    assert sale.symbol == "VWCE"
    assert portfolio.cash == Decimal("300")
    assert portfolio.invested == Decimal("200")
    assert portfolio.positions["VWCE"].shares == Decimal("2")
    assert portfolio.realized_gain_loss == Decimal("100")


def test_register_sale_rejects_unknown_position():
    with pytest.raises(ValueError, match="unknown position"):
        RegisterSale().execute(Portfolio(cash=Decimal("100")), request())


def test_register_sale_request_validates_input():
    with pytest.raises(ValueError, match="Sale shares"):
        request(shares=Decimal("0"))
    with pytest.raises(ValueError, match="Sale operation_id"):
        request(operation_id=" ")
