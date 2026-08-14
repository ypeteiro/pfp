"""Presentation helpers for patrimony evolution."""

from decimal import Decimal
from html import escape

from pfp.reporting.patrimony_evolution import PatrimonyEvolution


def patrimony_evolution_html(evolution: PatrimonyEvolution) -> str:
    points = evolution.points
    if not points:
        return '<section class="panel"><h2>Evolución patrimonial</h2><p class="muted">Sin datos históricos suficientes.</p></section>'

    rows = "".join(
        f'<tr><td>{p.datetime.strftime("%d/%m/%Y")}</td><td>{euro(p.net_capital)}</td><td>{euro(p.total_contributions)}</td><td>{euro(p.total_withdrawals)}</td><td>{euro(p.net_flow)}</td></tr>'
        for p in points
    )
    first = points[0]
    last = points[-1]
    change = last.net_capital - first.net_capital
    return f'''<section class="panel patrimony-evolution"><div class="panel-heading"><h2>Evolución patrimonial</h2><span>{len(points)} puntos</span></div>
<div class="evolution-summary"><div><span>Capital neto</span><strong>{euro(last.net_capital)}</strong></div><div><span>Aportaciones</span><strong>{euro(last.total_contributions)}</strong></div><div><span>Retiradas</span><strong>{euro(last.total_withdrawals)}</strong></div><div><span>Variación</span><strong class="{'positive' if change >= 0 else 'negative'}">{euro(change)}</strong></div></div>
<div class="evolution-chart" role="img" aria-label="Evolución del capital neto aportado"><div class="chart-line">{''.join(f'<span style="height:{chart_height(p.net_capital, last.net_capital)}%" title="{escape(p.datetime.strftime("%d/%m/%Y"))}: {euro(p.net_capital)}"></span>' for p in points)}</div></div>
<div class="table-scroll"><table><thead><tr><th>Fecha</th><th>Capital neto</th><th>Aportaciones acumuladas</th><th>Retiradas acumuladas</th><th>Flujo neto</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''


def chart_height(value: Decimal, maximum: Decimal) -> str:
    if maximum <= 0:
        return "0"
    return f"{max(4, min(100, float(value / maximum * Decimal("100")))):.2f}"


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
