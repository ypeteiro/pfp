from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.dashboard import build_dashboard


def test_dashboard_separates_total_cash_and_invested():
    report = PortfolioReport(
        cash=Decimal("500"),
        invested=Decimal("1000"),
        market_value=Decimal("900"),
        total_value=Decimal("1400"),
        realized_gain_loss=Decimal("50"),
        unrealized_gain_loss=Decimal("-100"),
        equity_value=Decimal("675"),
        fixed_income_value=Decimal("180"),
        gold_value=Decimal("45"),
        crypto_value=Decimal("0"),
        positions=(),
        accounts=(),
        movements=(),
    )
    dashboard = build_dashboard(report)
    values = {card.label: card.value for card in dashboard.cards}
    assert values["Patrimonio total"] == Decimal("1400")
    assert values["Efectivo"] == Decimal("500")
    assert values["Cartera invertida"] == Decimal("900")
    assert values["P/L total"] == Decimal("-50")


def test_dashboard_allocation_weights_use_invested_portfolio():
    report = PortfolioReport(
        cash=Decimal("100"),
        invested=Decimal("1000"),
        market_value=Decimal("1000"),
        total_value=Decimal("1100"),
        realized_gain_loss=Decimal("0"),
        unrealized_gain_loss=Decimal("0"),
        equity_value=Decimal("750"),
        fixed_income_value=Decimal("200"),
        gold_value=Decimal("50"),
        crypto_value=Decimal("0"),
        positions=(),
        accounts=(),
        movements=(),
    )
    dashboard = build_dashboard(report)
    weights = {row.asset_class: row.weight for row in dashboard.allocation}
    assert weights["RV"] == Decimal("0.75")
    assert weights["RF"] == Decimal("0.20")
    assert weights["Oro"] == Decimal("0.05")
