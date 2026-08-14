from decimal import Decimal

from pfp.excel.dashboard_model import build_dashboard
from pfp.reporting.portfolio_report import PortfolioReport


def _report():
    return PortfolioReport(
        cash=Decimal("670"),
        invested=Decimal("1000"),
        market_value=Decimal("1200"),
        total_value=Decimal("1870"),
        realized_gain_loss=Decimal("20"),
        unrealized_gain_loss=Decimal("30"),
        equity_value=Decimal("900"),
        fixed_income_value=Decimal("200"),
        gold_value=Decimal("100"),
        crypto_value=Decimal("0"),
        positions=(),
        accounts=(),
        movements=(),
    )


def test_dashboard_separates_cash_from_invested_portfolio():
    dashboard = build_dashboard(_report())
    values = {metric.label: metric.value for metric in dashboard.metrics}
    assert values["Patrimonio total"] == Decimal("1870")
    assert values["Efectivo"] == Decimal("670")
    assert values["Cartera invertida"] == Decimal("1200")
    assert values["P/L total"] == Decimal("50")


def test_dashboard_allocation_weights_use_market_value():
    dashboard = build_dashboard(_report())
    weights = {item.asset_class: item.weight for item in dashboard.allocation}
    assert weights["RV"] == Decimal("0.75")
    assert weights["RF"] == Decimal("0.1666666666666666666666666667")
    assert weights["Oro"] == Decimal("0.08333333333333333333333333333")
    assert weights["Cripto"] == Decimal("0")


def test_dashboard_allocation_handles_zero_market_value():
    report = _report().__class__(
        cash=Decimal("100"),
        invested=Decimal("0"),
        market_value=Decimal("0"),
        total_value=Decimal("100"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("0"),
        fixed_income_value=Decimal("0"),
        gold_value=Decimal("0"),
        crypto_value=Decimal("0"),
        positions=(),
        accounts=(),
        movements=(),
    )
    dashboard = build_dashboard(report)
    assert all(item.weight == Decimal("0") for item in dashboard.allocation)
