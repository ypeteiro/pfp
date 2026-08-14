"""Presentation helpers for the movements view."""

from decimal import Decimal
from html import escape

from pfp.reporting.portfolio_report import MovementReport, PortfolioReport


def movements_html(report: PortfolioReport) -> str:
    movements = sorted(report.movements, key=lambda m: m.datetime, reverse=True)
    total = sum((m.amount for m in movements), Decimal("0"))
    fees = sum((m.fee for m in movements), Decimal("0"))
    taxes = sum((m.tax for m in movements), Decimal("0"))
    purchases = sum((abs(m.amount) for m in movements if is_purchase(m)), Decimal("0"))
    sales = sum((abs(m.amount) for m in movements if is_sale(m)), Decimal("0"))
    rows = "".join(movement_row(m) for m in movements)
    if not rows:
        rows = '<tr><td colspan="10">Sin movimientos</td></tr>'
    return f'''<h1>Movimientos</h1><p class="muted">Histórico de operaciones importadas, ordenado de más reciente a más antiguo.</p>
<section class="metric-grid movement-metrics">{metric("Movimientos", Decimal(len(movements)), "count")}{metric("Compras", purchases)}{metric("Ventas", sales)}{metric("Comisiones", fees)}{metric("Impuestos", taxes)}</section>
<section class="panel movements-panel"><div class="panel-heading"><h2>Histórico</h2><span>Flujo neto {euro(total)}</span></div><div class="table-scroll"><table><thead><tr><th>Fecha</th><th>Categoría</th><th>Tipo</th><th>Activo</th><th>Participaciones</th><th>Precio</th><th>Importe</th><th>Comisión</th><th>Impuesto</th><th>Descripción</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''


def movement_row(m: MovementReport) -> str:
    tone = "positive" if m.amount > 0 else "negative" if m.amount < 0 else ""
    return f'''<tr><td>{escape(m.datetime.strftime("%d/%m/%Y %H:%M"))}</td><td>{escape(m.category or "—")}</td><td>{escape(m.type or "—")}</td><td><strong>{escape(m.symbol or "—")}</strong><small>{escape(m.name or "")}</small></td><td>{decimal_or_dash(m.shares)}</td><td>{euro(m.price)}</td><td class="{tone}">{euro(m.amount)}</td><td>{euro(m.fee)}</td><td>{euro(m.tax)}</td><td>{escape(m.description or "—")}</td></tr>'''


def is_purchase(m: MovementReport) -> bool:
    text = f"{m.category} {m.type}".upper()
    return "BUY" in text or "COMPRA" in text


def is_sale(m: MovementReport) -> bool:
    text = f"{m.category} {m.type}".upper()
    return "SELL" in text or "VENTA" in text


def metric(label: str, value: Decimal, tone: str = "") -> str:
    display = str(int(value)) if tone == "count" else euro(value)
    return f'<article class="metric {tone}"><span>{escape(label)}</span><strong>{display}</strong></article>'


def decimal_or_dash(value: Decimal | None) -> str:
    return "—" if value is None else str(value)


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
