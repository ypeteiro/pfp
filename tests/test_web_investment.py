from decimal import Decimal
from pathlib import Path

import pytest

from pfp.domain.portfolio import Portfolio
from pfp.importers.investment_repository import InvestmentRepository
from pfp.web.server import WebRuntime, parse_investment_request


def form(**overrides):
    values = {
        "datetime": ["2026-08-17T10:30"],
        "symbol": ["VWCE"],
        "shares": ["2"],
        "amount": ["250"],
        "price": ["125"],
        "portfolio_class": ["RV"],
        "broker": ["Trade Republic"],
        "operation_id": ["order-1"],
    }
    values.update({key: [value] for key, value in overrides.items()})
    return values


def test_parse_investment_request_maps_form_values():
    request = parse_investment_request(form())
    assert request.symbol == "VWCE"
    assert request.shares == Decimal("2")
    assert request.amount == Decimal("250")
    assert request.price == Decimal("125")
    assert request.portfolio_class == "RV"
    assert request.operation_id == "order-1"


@pytest.mark.parametrize("field", ["datetime", "symbol", "shares", "amount", "price", "portfolio_class", "broker"])
def test_parse_investment_request_requires_fields(field):
    values = form()
    values[field] = [""]
    with pytest.raises(ValueError):
        parse_investment_request(values)


def test_parse_investment_request_accepts_missing_optional_operation_id():
    values = form()
    values["operation_id"] = [""]
    request = parse_investment_request(values)
    assert request.operation_id is None


def test_web_runtime_report_reflects_in_memory_investment():
    class FakePriceProvider:
        def get_prices(self, symbols):
            return {"VWCE": Decimal("130")} if symbols == ["VWCE"] else {}

    portfolio = Portfolio(cash=Decimal("1000"))
    runtime = WebRuntime(portfolio, FakePriceProvider())

    from pfp.application.register_investment import RegisterInvestment
    RegisterInvestment().execute(
        portfolio,
        parse_investment_request(form()),
    )

    report = runtime.report()
    assert report.cash == Decimal("750")
    assert report.invested == Decimal("250")
    assert report.positions[0].symbol == "VWCE"
    assert report.positions[0].market_value == Decimal("260")


def test_web_runtime_persists_registered_investment(tmp_path):
    repository = InvestmentRepository(tmp_path / "investments.csv")

    class FakePriceProvider:
        def get_prices(self, symbols):
            return {symbol: Decimal("130") for symbol in symbols}

    portfolio = Portfolio(cash=Decimal("1000"))
    runtime = WebRuntime(portfolio, FakePriceProvider(), repository)

    investment = runtime.register_investment(parse_investment_request(form()))

    assert repository.load() == [investment]
    assert portfolio.invested == Decimal("250")
