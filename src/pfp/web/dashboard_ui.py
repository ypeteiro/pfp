"""Presentation helpers for the PFP dashboard v2."""

from decimal import Decimal
from html import escape

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.excel.allocation_actions import build_allocation_rows
from pfp.reporting.patrimony_evolution import PatrimonyEvolution
from pfp.reporting.portfolio_report import PortfolioReport


ALLOCATION_LABELS = {
    "RV": "Renta variable",
    "RF": "Renta fija",
    "Oro": "Oro",
    "Cripto": "Criptoactivos",
}

ALLOCATION_TIPS = {
    "RV": "Acciones y otros activos de renta variable. Objetivo actual: 75%.",
    "RF": "Bonos, fondos y otros activos de renta fija. Objetivo actual: 20%.",
    "Oro": "Exposición al oro como activo diversificador. Objetivo actual: 5%.",
    "Cripto": "Criptoactivos. Actualmente no tienen una asignación objetivo específica.",
}

METRIC_TIPS = {
    "Patrimonio total": "Efectivo más el valor de mercado de tus posiciones.",
    "Efectivo": "Dinero disponible que todavía no está invertido en posiciones.",
    "Cartera invertida": "Capital invertido neto en las posiciones. No incluye el P/L no realizado.",
    "P/L realizado": "Beneficios o pérdidas ya materializados mediante ventas realizadas.",
    "P/L no realizado": "Beneficios o pérdidas de posiciones que todavía mantienes abiertas. Cambian con el precio de mercado.",
    "P/L total": "Suma del P/L realizado y del P/L no realizado.",
}


def dashboard_v2_html(report: PortfolioReport) -> str:
    total = report.market_value
    values = {"RV": report.equity_value, "RF": report.fixed_income_value, "Oro": report.gold_value, "Cripto": report.crypto_value}
    targets = {"RV": Decimal("0.75"), "RF": Decimal("0.20"), "Oro": Decimal("0.05"), "Cripto": Decimal("0")}
    allocation = build_allocation_rows(values, targets, total)
    bars = []
    for row in allocation:
        label = ALLOCATION_LABELS.get(row.asset_class, row.asset_class)
        tip = ALLOCATION_TIPS.get(row.asset_class, "Distribución de esta clase de activo dentro de la cartera.")
        weight = max(0, min(100, float(row.current_weight * 100))) if row.current_weight is not None else 0
        bars.append(
            '<div class="allocation-row">'
            f'<div class="allocation-label"><span class="allocation-name">{escape(label)} {tooltip(tip)}</span><strong>{pct(row.current_weight)}</strong></div>'
            f'<div class="bar"><span style="width:{weight:.2f}%"></span></div>'
            f'<div class="allocation-meta">Objetivo {pct(row.target)} · {escape(row.action)}</div>'
            '</div>'
        )

    positions = sorted(report.positions, key=lambda p: p.market_value or Decimal("0"), reverse=True)
    position_rows = "".join(
        f'<tr><td>{escape(p.ticker or p.isin or p.symbol)}</td><td>{escape(p.name)}</td><td>{pct(p.weight)}</td><td>{euro(p.market_value)}</td><td>{euro(p.gain_loss)}</td></tr>'
        for p in positions[:10]
    )
    total_pl = report.realized_gain_loss + report.unrealized_gain_loss
    evolution = _evolution_from_report(report)
    evolution_html = _evolution_summary(evolution)
    return f"""
<section class="dashboard-v2">
  <div class="hero"><div><p class="eyebrow">PFP · Vista general</p><h1>Tu patrimonio</h1><p class="muted">Una lectura rápida de dónde está tu dinero y cómo se desvía de tu estrategia.</p></div><div class="hero-value">{euro(report.total_value)}</div></div>
  <section class="metric-grid">{metric("Patrimonio total", report.total_value)}{metric("Efectivo", report.cash)}{metric("Cartera invertida", report.market_value)}{metric("P/L realizado", report.realized_gain_loss)}{metric("P/L no realizado", report.unrealized_gain_loss)}{metric("P/L total", total_pl, "positive" if total_pl >= 0 else "negative")}</section>
  {evolution_html}
  <section class="two-col"><article class="panel"><div class="panel-heading"><h2>Asignación {tooltip("Distribución actual de tu patrimonio por clase de activo.")}</h2><span>Objetivo 75 / 20 / 5</span></div>{''.join(bars)}</article><article class="panel"><div class="panel-heading"><h2>Posiciones principales</h2><span>{len(report.positions)} activos</span></div><table><thead><tr><th>Activo</th><th>Nombre</th><th>Peso</th><th>Valor</th><th>P/L</th></tr></thead><tbody>{position_rows or '<tr><td colspan="5">Sin posiciones</td></tr>'}</tbody></table></article></section>
</section>
"""


def _evolution_from_report(report: PortfolioReport) -> PatrimonyEvolution:
    flows = []
    for movement in report.movements:
        movement_type = movement.type.upper().strip()
        if movement_type not in {FlowType.CONTRIBUTION.value, FlowType.WITHDRAWAL.value}:
            continue
        flows.append(CapitalFlow(movement.datetime, abs(movement.amount), FlowType(movement_type), movement.transaction_id))
    return PatrimonyEvolution.from_capital_flows(flows)


def _evolution_summary(evolution: PatrimonyEvolution) -> str:
    if not evolution.points:
        return '<section class="panel patrimony-evolution"><div class="panel-heading"><h2>Evolución patrimonial</h2>{}</div><p class="muted">Sin aportaciones o retiradas históricas clasificadas todavía.</p></section>'.format(tooltip("Muestra cómo evoluciona el capital neto aportado a lo largo del tiempo."))
    last = evolution.points[-1]
    tone = "positive" if last.net_flow >= 0 else "negative"
    return f'<section class="panel patrimony-evolution"><div class="panel-heading"><h2>Evolución patrimonial {tooltip("Muestra la evolución de los movimientos de capital registrados.")}</h2><span>{len(evolution.points)} movimientos de capital</span></div><div class="evolution-summary"><div><span>Capital neto aportado</span><strong>{euro(last.cumulative_contributed)}</strong></div><div><span>Aportaciones</span><strong>{euro(evolution.total_contributions)}</strong></div><div><span>Retiradas</span><strong>{euro(evolution.total_withdrawals)}</strong></div><div><span>Último flujo</span><strong class="{tone}">{euro(last.net_flow)}</strong></div></div></section>'


def metric(label: str, value: Decimal, tone: str = "") -> str:
    tip = METRIC_TIPS.get(label)
    return f'<article class="metric {tone}"><div class="metric-label"><span>{escape(label)}</span>{tooltip(tip) if tip else ""}</div><strong>{euro(value)}</strong></article>'


def tooltip(text: str) -> str:
    return f'<span class="tooltip" tabindex="0" aria-label="Más información">ⓘ<span class="tooltip-content">{escape(text)}</span></span>'


def euro(value: Decimal | None) -> str:
    if value is None: return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: Decimal | None) -> str:
    if value is None: return "—"
    return f"{value * 100:.2f}%".replace(".", ",")
