from decimal import Decimal

import pytest

from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio
from pfp.importers.sale_repository import SaleRepository
from pfp.web.server import WebRuntime, parse_sale_request


def form(**overrides):
    values = {
        "datetime": ["2026-08-17T10:30"],
        "symbol": ["VWCE"],
        "shares": ["2"],
        "amount": ["300"],
        "price": ["150"],
        "broker": ["Trade Republic"],
        "operation_id": ["sale-1"],
    }
    values.update({key: [value] for key, value in overrides.items()})
    return values


def portfolio_with_position():
    portfolio = Portfolio(cash=Decimal("400"))
    from datetime import datetime, timezone
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
    return portfolio


def test_parse_sale_request_maps_form_values():
    request = parse_sale_request(form())
    assert request.symbol == "VWCE"
    assert request.shares == Decimal("2")
    assert request.amount == Decimal("300")
    assert request.price == Decimal("150")
    assert request.operation_id == "sale-1"


@pytest.mark.parametrize("field", ["datetime", "symbol", "shares", "amount", "price", "broker"])
def test_parse_sale_request_requires_fields(field):
    values = form()
    values[field] = [""]
    with pytest.raises(ValueError):
        parse_sale_request(values)


def test_parse_sale_request_accepts_missing_optional_operation_id():
    values = form(operation_id="")
    assert parse_sale_request(values).operation_id is None


def test_web_runtime_persists_registered_sale(tmp_path):
    repository = SaleRepository(tmp_path / "sales.csv")
    class FakePriceProvider:
        def get_prices(self, symbols):
            return {symbol: Decimal("150") for symbol in symbols}
    runtime = WebRuntime(portfolio_with_position(), FakePriceProvider(), sale_repository=repository)

    sale = runtime.register_sale(parse_sale_request(form()))

    assert repository.load() == [sale]
    assert runtime.portfolio.cash == Decimal("300")
    assert runtime.portfolio.invested == Decimal("200")


def test_web_runtime_duplicate_sale_does_not_modify_portfolio(tmp_path):
    repository = SaleRepository(tmp_path / "sales.csv")
    runtime = WebRuntime(portfolio_with_position(), object(), sale_repository=repository)
    request = parse_sale_request(form())

    runtime.register_sale(request)
    cash = runtime.portfolio.cash
    invested = runtime.portfolio.invested
    shares = runtime.portfolio.positions["VWCE"].shares

    with pytest.raises(ValueError, match="ya ha sido registrada"):
        runtime.register_sale(request)

    assert runtime.portfolio.cash == cash
    assert runtime.portfolio.invested == invested
    assert runtime.portfolio.positions["VWCE"].shares == shares
    assert len(repository.load()) == 1
