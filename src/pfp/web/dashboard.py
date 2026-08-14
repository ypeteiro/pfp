"""Dashboard view-model helpers for a future PFP web UI."""

from dataclasses import dataclass
from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport


@dataclass(frozen=True, slots=True)
class DashboardCard:
    label: str
    value: Decimal
    kind: str = "currency"


@dataclass(frozen=True, slots=True)
class DashboardAllocation:
    asset_class: str
    value: Decimal
    weight: Decimal


@dataclass(frozen=True, slots=True)
class DashboardModel:
    cards: tuple[DashboardCard, ...]
    allocation: tuple[DashboardAllocation, ...]


def build_dashboard(report: PortfolioReport) -> DashboardModel:
    cards = (
        DashboardCard("Patrimonio total", report.total_value),
        DashboardCard("Efectivo", report.cash),
        DashboardCard("Cartera invertida", report.market_value),
        DashboardCard("P/L realizado", report.realized_gain_loss),
        DashboardCard("P/L no realizado", report.unrealized_gain_loss),
        DashboardCard("P/L total", report.realized_gain_loss + report.unrealized_gain_loss),
    )
    total = report.market_value
    values = (
        ("RV", report.equity_value),
        ("RF", report.fixed_income_value),
        ("Oro", report.gold_value),
        ("Cripto", report.crypto_value),
    )
    allocation = tuple(
        DashboardAllocation(asset_class, value, value / total if total else Decimal("0"))
        for asset_class, value in values
    )
    return DashboardModel(cards=cards, allocation=allocation)
