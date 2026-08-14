"""Presentation helpers for patrimony evolution."""

from decimal import Decimal
from html import escape

from pfp.reporting.patrimony_evolution import PatrimonyEvolution


def patrimony_evolution_html(evolution: PatrimonyEvolution) -> str:
    points = evolution.points
    if not points:
        return '<section class="panel"><h2>Evolución patrimonial</h2><p class="muted">Sin datos históricos suficientes.</p></section>'
    maximum = max((p.cumulative_contributed for p in points), default=Decimal("0"))
    rows = "".join(
        f'<tr><td>{p.datetime.strftime("%d/%m/%Y")}</td><td>{euro(p.cumulative_contributed)}</td><td>{euro(p.contribution)}</td><td>{euro(p.withdrawal)}</td><td>{euro(p.net_flow)}</td></tr>'
        for p in points
    )
    first, last = points[0], points[-1]
    change = last.cumulative_contributed - first.cumulative_contributed
    chart = "".join(
        f'<span style="height:{chart_height(p.cumulative_contributed, maximum)}%" title="{escape(p.datetime.strftime("%d/%m/%Y"))}: {euro(p.cumulative_contributed)}"></span>'
        for p in points
    )
    return f'''<section class="panel patrimony-evolution"><div class="panel-heading"><h2>Evolución patrimonial</h2><span>{len(points)} puntos</span></div>
<div class="evolution-summary"><div><span>Capital neto aportado</span><strong>{euro(last.cumulative_contributed)}</strong></div><div><span>Aportaciones</span><strong>{euro(evolution.total_contributions)}</strong></div><div><span>Retiradas</span><strong>{euro(evolution.total_withdrawals)}</strong></div><div><span>Variación</span><strong class="{'positive' if change >= 0 else 'negative'}">{euro(change)}</strong></div></div>
<div class="evolution-chart" role="img" aria-label="Evolución del capital neto aportado"><div class="chart-line">{chart}</div></div>
<div class="table-scroll"><table><thead><tr><th>Fecha</th><th>Capital neto</th><th>Aportación</th><th>Retirada</th><th>Flujo neto</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''


def chart_height(value: Decimal, maximum: Decimal) -> str:
    if maximum <= 0:
        return "0"
    percent = value / maximum * Decimal("100")
    return f"{max(4, min(100, float(percent))):.2f}"


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
