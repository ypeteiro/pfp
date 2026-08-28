"""Presentation helpers for the PFP dashboard v2."""

from datetime import datetime
from decimal import Decimal
from html import escape

from pfp.excel.allocation_actions import build_allocation_rows
from pfp.reporting.patrimony_series import PatrimonyPoint
from pfp.reporting.portfolio_report import PortfolioReport

ALLOCATION_LABELS = {"RV": "Renta variable", "RF": "Renta fija", "Oro": "Oro", "Cripto": "Criptoactivos"}
ALLOCATION_TIPS = {
    "RV": "Acciones y otros activos de renta variable. Objetivo actual: 75%.",
    "RF": "Bonos, fondos y otros activos de renta fija. Objetivo actual: 20%.",
    "Oro": "Exposición al oro como activo diversificador. Objetivo actual: 5%.",
    "Cripto": "Criptoactivos. Actualmente no tienen una asignación objetivo específica.",
}
METRIC_TIPS = {
    "Patrimonio total": "Efectivo más el valor de mercado de tus posiciones.",
    "Efectivo invertible": "Dinero disponible en cuentas destinadas a inversión. Actualmente corresponde a Trade Republic.",
    "Fondo de seguridad": "Efectivo reservado y excluido del rebalanceo. Actualmente corresponde a ABANCA Ahorro.",
    "Cartera invertida": "Coste de adquisición neto de las posiciones. No incluye el P/L no realizado.",
    "P/L realizado": "Beneficios o pérdidas ya materializados mediante ventas realizadas.",
    "P/L no realizado": "Beneficios o pérdidas de posiciones que todavía mantienes abiertas. Cambian con el precio de mercado.",
    "P/L total": "Suma del P/L realizado y del P/L no realizado.",
}


def dashboard_v2_html(report: PortfolioReport, sort: str = "weight", direction: str = "desc") -> str:
    total = report.market_value
    values = {"RV": report.equity_value, "RF": report.fixed_income_value, "Oro": report.gold_value, "Cripto": report.crypto_value}
    targets = {"RV": Decimal("0.75"), "RF": Decimal("0.20"), "Oro": Decimal("0.05"), "Cripto": Decimal("0")}
    allocation = build_allocation_rows(values, targets, total)
    bars = []
    for row in allocation:
        label = ALLOCATION_LABELS.get(row.asset_class, row.asset_class)
        tip = ALLOCATION_TIPS.get(row.asset_class, "Distribución de esta clase de activo dentro de la cartera.")
        weight = max(0, min(100, float(row.current_weight * 100))) if row.current_weight is not None else 0
        bars.append('<div class="allocation-row">' f'<div class="allocation-label"><span class="allocation-name">{escape(label)} {tooltip(tip)}</span><strong>{pct(row.current_weight)}</strong></div>' f'<div class="bar"><span style="width:{weight:.2f}%"></span></div>' f'<div class="allocation-meta">Objetivo {pct(row.target)} · {escape(row.action)}</div>' '</div>')

    positions = sort_positions(report, sort, direction)
    position_rows = "".join(
        f'<tr><td>{escape(p.ticker or p.isin or p.symbol)}</td><td>{escape(p.name)}</td><td>{pct(p.weight)}</td><td>{euro(p.market_value)}</td><td class="{"positive" if p.gain_loss is not None and p.gain_loss > 0 else "negative" if p.gain_loss is not None and p.gain_loss < 0 else ""}">{euro(p.gain_loss)}</td></tr>'
        for p in positions[:10]
    )
    total_pl = report.realized_gain_loss + report.unrealized_gain_loss
    evolution_html = _evolution_summary(report.patrimony_series)
    consulted_at = report.price_consulted_at or datetime.now().astimezone()
    consulted = consulted_at.strftime("%d/%m/%Y %H:%M")
    price_status = f'<p class="price-status">Precios de mercado consultados: {consulted}</p>'
    return f"""
<section class="dashboard-v2">
  <div class="hero"><div><h1>Tu patrimonio</h1><p class="muted">Una lectura rápida de dónde está tu dinero y cómo se desvía de tu estrategia.</p>{price_status}</div></div>
  <section class="metric-grid">{metric("Patrimonio total", report.total_value)}{metric("Efectivo invertible", report.investable_cash)}{metric("Fondo de seguridad", report.security_fund_cash)}{metric("Cartera invertida", report.invested)}{metric("P/L realizado", report.realized_gain_loss)}{metric("P/L no realizado", report.unrealized_gain_loss)}{metric("P/L total", total_pl, "positive" if total_pl >= 0 else "negative")}</section>
  {evolution_html}
  <section class="two-col"><article class="panel"><div class="panel-heading allocation-panel-heading"><h2>Asignación {tooltip("Distribución actual de tu patrimonio por clase de activo.")}</h2><span>Objetivo 75 / 20 / 5</span></div>{''.join(bars)}</article><article class="panel"><div class="panel-heading"><h2>Posiciones principales</h2><span>{len(report.positions)} activos</span></div><table><thead><tr>{sort_heading("Activo", "symbol", sort, direction)}{sort_heading("Nombre", "name", sort, direction)}{sort_heading("Peso", "weight", sort, direction)}{sort_heading("Valor", "value", sort, direction)}<th>P/L</th></tr></thead><tbody>{position_rows or '<tr><td colspan="5">Sin posiciones</td></tr>'}</tbody></table></article></section>
</section>
"""


def sort_positions(report: PortfolioReport, sort: str, direction: str):
    key_map = {
        "symbol": lambda p: (p.ticker or p.isin or p.symbol or "").lower(),
        "name": lambda p: (p.name or "").lower(),
        "weight": lambda p: p.weight if p.weight is not None else Decimal("-1"),
        "value": lambda p: p.market_value if p.market_value is not None else Decimal("-1"),
    }
    key = key_map.get(sort, key_map["weight"])
    return sorted(report.positions, key=key, reverse=direction != "asc")


def sort_heading(label: str, field: str, current: str, direction: str) -> str:
    next_direction = "asc" if current == field and direction != "asc" else "desc"
    arrow = "↑" if current == field and direction == "asc" else "↓" if current == field else "↕"
    return f'<th><a class="sortable-heading" href="/?sort={field}&direction={next_direction}">{label}<span class="sort-arrow">{arrow}</span></a></th>'


def _evolution_summary(points: tuple[PatrimonyPoint, ...]) -> str:
    if not points:
        return '<section class="panel patrimony-evolution"><div class="panel-heading"><h2>Evolución patrimonial</h2></div><p class="muted">Todavía no hay suficientes datos históricos para mostrar la evolución.</p></section>'

    width, height = 980, 420
    left, right, top, bottom = 86, 150, 26, 64
    plot_width = width - left - right
    plot_height = height - top - bottom
    series = (
        ("patrimony", "Patrimonio", [point.patrimony for point in points], "#2563eb", 4, ""),
        ("contributed", "Capital aportado", [point.cumulative_contributed for point in points], "#64748b", 3, "stroke-dasharray:8 6"),
        ("invested", "Capital invertido", [point.invested_cost for point in points], "#059669", 3, "stroke-dasharray:2 5"),
    )
    all_values = [value for _, _, values, _, _, _ in series for value in values]
    minimum = min(Decimal("0"), min(all_values))
    maximum = max(Decimal("1"), max(all_values))
    span = maximum - minimum or Decimal("1")

    if len(points) == 1:
        xs = [left + plot_width / 2]
    else:
        xs = [left + index * plot_width / (len(points) - 1) for index in range(len(points))]

    def y_for(value: Decimal) -> float:
        return top + plot_height - float((value - minimum) / span) * plot_height

    def polyline(values: list[Decimal]) -> str:
        return " ".join(f"{x:.1f},{y_for(value):.1f}" for x, value in zip(xs, values))

    ticks = []
    for index in range(5):
        ratio = Decimal(index) / Decimal(4)
        value = maximum - ratio * span
        y = y_for(value)
        ticks.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" style="stroke:#e5e7eb;stroke-width:1" />'
            f'<text x="{left-12}" y="{y+4:.1f}" text-anchor="end" style="fill:#64748b;font-size:12px">{escape(euro(value))}</text>'
        )

    label_count = min(7, len(points))
    label_indexes = sorted({round(index * (len(points) - 1) / (label_count - 1)) for index in range(label_count)}) if label_count > 1 else [0]
    date_labels = []
    for index in label_indexes:
        x = xs[index]
        date = points[index].datetime.strftime("%d/%m/%y")
        date_labels.append(
            f'<line x1="{x:.1f}" y1="{height-bottom}" x2="{x:.1f}" y2="{height-bottom+7}" style="stroke:#94a3b8;stroke-width:1" />'
            f'<text x="{x:.1f}" y="{height-20}" text-anchor="middle" style="fill:#475569;font-size:12px">{escape(date)}</text>'
        )

    lines = []
    for key, label, values, stroke, stroke_width, extra_style in series:
        lines.append(
            f'<polyline points="{polyline(values)}" fill="none" style="stroke:{stroke};stroke-width:{stroke_width};stroke-linecap:round;stroke-linejoin:round;{extra_style}" />'
        )

    points_svg = []
    for index, point in enumerate(points):
        title = escape(
            f'{point.datetime.strftime("%d/%m/%Y")}: Patrimonio {euro(point.patrimony)} · '
            f'Aportado {euro(point.cumulative_contributed)} · Capital invertido {euro(point.invested_cost)}'
        )
        for key, _, value, stroke, _, _ in (
            ("patrimony", "Patrimonio", point.patrimony, "#2563eb", 4, ""),
            ("contributed", "Capital aportado", point.cumulative_contributed, "#64748b", 3, ""),
            ("invested", "Capital invertido", point.invested_cost, "#059669", 3, ""),
        ):
            points_svg.append(
                f'<circle cx="{xs[index]:.1f}" cy="{y_for(value):.1f}" r="4" style="fill:white;stroke:{stroke};stroke-width:2"><title>{title}</title></circle>'
            )

    last = points[-1]
    label_offsets = {"patrimony": -18, "invested": 0, "contributed": 18}
    end_labels = []
    for key, label, value, stroke in (
        ("patrimony", "Patrimonio", last.patrimony, "#2563eb"),
        ("invested", "Capital invertido", last.invested_cost, "#059669"),
        ("contributed", "Capital aportado", last.cumulative_contributed, "#64748b"),
    ):
        y = y_for(value) + label_offsets[key]
        end_labels.append(
            f'<line x1="{xs[-1]+6:.1f}" y1="{y_for(value):.1f}" x2="{width-right+8}" y2="{y:.1f}" style="stroke:{stroke};stroke-width:1.5" />'
            f'<text x="{width-right+14}" y="{y+4:.1f}" style="fill:{stroke};font-size:12px;font-weight:600">{escape(label)} · {escape(euro(value))}</text>'
        )

    legend = (
        '<div style="display:flex;flex-wrap:wrap;gap:18px;margin:10px 0 16px;font-size:13px">'
        '<span style="color:#2563eb;font-weight:600">━━ Patrimonio</span>'
        '<span style="color:#64748b;font-weight:600">┄┄ Capital aportado</span>'
        '<span style="color:#059669;font-weight:600">··· Capital invertido</span>'
        '</div>'
    )
    gain_tone = "positive" if last.investment_gain >= 0 else "negative"
    svg = (
        f'<div class="patrimony-chart-wrap" style="overflow-x:auto">'
        f'<svg class="patrimony-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Evolución temporal del patrimonio, capital aportado y capital invertido">'
        f'{"".join(ticks)}'
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" style="stroke:#94a3b8;stroke-width:1" />'
        f'{"".join(date_labels)}{"".join(lines)}{"".join(points_svg)}{"".join(end_labels)}'
        '</svg></div>'
    )
    return f'<section class="panel patrimony-evolution"><div class="panel-heading"><div><h2>Evolución patrimonial {tooltip("Patrimonio = efectivo + valor de mercado. Capital aportado = aportaciones netas. Capital invertido = coste de las posiciones.")}</h2><p class="muted evolution-description">La línea continua es tu patrimonio. La discontinua es lo que has aportado. La punteada es el capital destinado a comprar tus inversiones.</p></div><span>{len(points)} puntos históricos</span></div>{svg}{legend}<div class="evolution-summary"><div><span>Patrimonio actual</span><strong>{euro(last.patrimony)}</strong></div><div><span>Capital aportado</span><strong>{euro(last.cumulative_contributed)}</strong></div><div><span>Capital invertido</span><strong>{euro(last.invested_cost)}</strong></div><div><span>Rendimiento acumulado</span><strong class="{gain_tone}">{euro(last.investment_gain)}</strong></div></div></section>'


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
