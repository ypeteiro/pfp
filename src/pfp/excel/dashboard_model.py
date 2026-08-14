"""Presentation model for the PFP dashboard."""

from dataclasses import dataclass
from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport


@dataclass(frozen=True, slots=True)
class DashboardMetric:
    label: str
    value: Decimal


@dataclass(frozen=True, slots=True)
class DashboardAllocation:
    asset_class: str
    value: Decimal
    weight: Decimal


@dataclass(frozen=True, slots=True)
class DashboardModel:
    metrics: tuple[DashboardMetric, ...]
    allocation: tuple[DashboardAllocation, ...]


def build_dashboard(report: PortfolioReport) -> DashboardModel:
    total_invested_value = report.market_value
    allocation_values = (
        ("RV", report.equity_value),
        ("RF", report.fixed_income_value),
        ("Oro", report.gold_value),
        ("Cripto", report.crypto_value),
    )
    allocation = tuple(
        DashboardAllocation(
            asset_class=asset_class,
            value=value,
            weight=value / total_invested_value if total_invested_value else Decimal("0"),
        )
        for asset_class, value in allocation_values
    )
    metrics = (
        DashboardMetric("Patrimonio total", report.total_value),
        DashboardMetric("Efectivo", report.cash),
        DashboardMetric("Cartera invertida", report.market_value),
        DashboardMetric("Capital invertido", report.invested),
        DashboardMetric("P/L realizado", report.realized_gain_loss),
        DashboardMetric("P/L no realizado", report.unrealized_gain_loss),
        DashboardMetric(
            "P/L total",
            report.realized_gain_loss + report.unrealized_gain_loss,
        ),
    )
    return DashboardModel(metrics=metrics, allocation=allocation)
