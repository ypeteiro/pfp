"""Presentation helpers for the PFP dashboard v2."""

from decimal import Decimal
from html import escape

from pfp.excel.allocation_actions import build_allocation_rows
from pfp.reporting.portfolio_report import PortfolioReport


def dashboard_v2_html(report: PortfolioReport) -> str:
    total = report.market_value
    values = {
        "RV": report.equity_value,
        "RF": report.fixed_income_value,
        "Oro": report.gold_value,
        "Cripto": report.crypto_value,
    }
    targets = {"RV": Decimal("0.75"), "RF": Decimal("0.20"), "Oro": Decimal("0.05"), "Cripto": Decimal("0")}
    allocation = build_allocation_rows(values, targets, total)

    bars = []
    for row in allocation:
        bars.append(
            '<div class="allocation-row">'
            f'<div class="allocation-label"><span>{escape(row.asset_class)}</span><span>{pct(row.current_weight)}</span></div>'
            f'<div class="bar"><span style="width:{max(0, min(100, float(row.current_weight * 100))):.2f}%"></span></div>'
            f'<div class="allocation-meta">Objetivo {pct(row.target)} · {escape(row.action)}</div>'
            '</div>'
        )

    positions = sorted(report.positions, key=lambda p: p.market_value or Decimal("0"), reverse=True)
    position_rows = "".join(
        f'<tr><td>{escape(p.ticker or p.isin or p.symbol)}</td><td>{escape(p.name)}</td><td>{pct(p.weight)}</td><td>{euro(p.market_value)}</td><td>{euro(p.gain_loss)}</td></tr>'
        for p in positions[:10]
    )

    total_pl = report.realized_gain_loss + report.unrealized_gain_loss
    return f"""
<section class="dashboard-v2">
  <div class="hero"><div><p class="eyebrow">PFP · Vista general</p><h1>Tu patrimonio</h1><p class="muted">Una lectura rápida de dónde está tu dinero y cómo se desvía de tu estrategia.</p></div><div class="hero-value">{euro(report.total_value)}</div></div>
  <section class="metric-grid">
    {metric("Patrimonio total", report.total_value)}
    {metric("Efectivo", report.cash)}
    {metric("Cartera invertida", report.market_value)}
    {metric("P/L realizado", report.realized_gain_loss)}
    {metric("P/L no realizado", report.unrealized_gain_loss)}
    {metric("P/L total", total_pl, "positive" if total_pl >= 0 else "negative")}
  </section>
  <section class="two-col">
    <article class="panel"><div class="panel-heading"><h2>Asignación</h2><span>Objetivo 75 / 20 / 5</span></div>{''.join(bars)}</article>
    <article class="panel"><div class="panel-heading"><h2>Posiciones principales</h2><span>{len(report.positions)} activos</span></div><table><thead><tr><th>Activo</th><th>Nombre</th><th>Peso</th><th>Valor</th><th>P/L</th></tr></thead><tbody>{position_rows or '<tr><td colspan="5">Sin posiciones</td></tr>'}</tbody></table></article>
  </section>
</section>
"""


def metric(label: str, value: Decimal, tone: str = "") -> str:
    return f'<article class="metric {tone}"><span>{escape(label)}</span><strong>{euro(value)}</strong></article>'


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%".replace(".", ",")
