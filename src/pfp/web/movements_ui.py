"""Presentation helpers for the movements view."""

from decimal import Decimal
from html import escape

from pfp.reporting.portfolio_report import MovementReport, PortfolioReport


def movements_html(report: PortfolioReport, broker: str = "", category: str = "", movement_type: str = "", asset_class: str = "", search: str = "", date_from: str = "", date_to: str = "") -> str:
    movements = [m for m in report.movements if matches_filters(m, broker, category, movement_type, asset_class, search, date_from, date_to)]
    movements.sort(key=lambda m: m.datetime, reverse=True)
    total = sum((m.amount for m in movements), Decimal("0"))
    fees = sum((m.fee for m in movements), Decimal("0"))
    taxes = sum((m.tax for m in movements), Decimal("0"))
    purchases = sum((abs(m.amount) for m in movements if is_purchase(m)), Decimal("0"))
    sales = sum((abs(m.amount) for m in movements if is_sale(m)), Decimal("0"))
    rows = "".join(movement_row(m) for m in movements) or '<tr><td colspan="12">Sin movimientos con los filtros seleccionados</td></tr>'
    brokers = sorted({m.broker for m in report.movements if m.broker})
    categories = sorted({m.category for m in report.movements if m.category})
    types = sorted({m.type for m in report.movements if m.type})
    asset_classes = sorted({m.asset_class for m in report.movements if m.asset_class})
    return f'''<h1>Movimientos</h1><p class="muted">Histórico de operaciones importadas, ordenado de más reciente a más antiguo.</p>
<section class="panel movement-filters">{filter_form(brokers, categories, types, asset_classes, broker, category, movement_type, asset_class, search, date_from, date_to)}</section>
<section class="metric-grid movement-metrics">{metric("Movimientos", Decimal(len(movements)), "count")}{metric("Compras", purchases)}{metric("Ventas", sales)}{metric("Comisiones", fees)}{metric("Impuestos", taxes)}</section>
<section class="panel movements-panel"><div class="panel-heading"><h2>Histórico</h2><span>Flujo neto {euro(total)}</span></div><div class="table-scroll"><table><thead><tr><th>Fecha</th><th>Broker</th><th>Categoría</th><th>Tipo</th><th>Activo</th><th>Participaciones</th><th>Precio</th><th>Importe</th><th>Comisión</th><th>Impuesto</th><th>Divisa</th><th>Descripción / ID</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''


def filter_form(brokers, categories, types, asset_classes, broker, category, movement_type, asset_class, search, date_from, date_to) -> str:
    active = any((broker, category, movement_type, asset_class, search, date_from, date_to))
    reset = '<a class="filter-reset" href="/movements">Limpiar</a>' if active else ''
    return f'''<form class="movement-filter-form" method="get" action="/movements">
<label>Broker<select name="broker"><option value="">Todos</option>{options(brokers, broker)}</select></label>
<label>Categoría<select name="category"><option value="">Todas</option>{options(categories, category)}</select></label>
<label>Tipo<select name="type"><option value="">Todos</option>{options(types, movement_type)}</select></label>
<label>Clase<select name="asset_class"><option value="">Todas</option>{options(asset_classes, asset_class)}</select></label>
<label>Desde<input type="date" name="date_from" value="{escape(date_from)}"></label>
<label>Hasta<input type="date" name="date_to" value="{escape(date_to)}"></label>
<label class="filter-search">Buscar<input type="search" name="search" value="{escape(search)}" placeholder="Activo, descripción o ID"></label>
<button type="submit">Filtrar</button>{reset}
</form>'''


def options(values, selected) -> str:
    return "".join(f'<option value="{escape(str(value))}"{" selected" if str(value) == selected else ""}>{escape(str(value))}</option>' for value in values)


def matches_filters(m: MovementReport, broker, category, movement_type, asset_class, search, date_from, date_to) -> bool:
    if broker and m.broker != broker: return False
    if category and m.category != category: return False
    if movement_type and m.type != movement_type: return False
    if asset_class and m.asset_class != asset_class: return False
    if date_from and m.datetime.date().isoformat() < date_from: return False
    if date_to and m.datetime.date().isoformat() > date_to: return False
    if search:
        haystack = " ".join(str(value or "") for value in (m.symbol, m.name, m.description, m.transaction_id, m.category, m.type)).casefold()
        if search.casefold() not in haystack: return False
    return True


def movement_row(m: MovementReport) -> str:
    tone = "positive" if m.amount > 0 else "negative" if m.amount < 0 else ""
    detail = escape(m.description or "—")
    if m.transaction_id: detail += f'<small>ID: {escape(m.transaction_id)}</small>'
    return f'''<tr><td>{escape(m.datetime.strftime("%d/%m/%Y %H:%M"))}</td><td>{escape(m.broker or "—")}</td><td>{escape(m.category or "—")}</td><td>{escape(m.type or "—")}</td><td><strong>{escape(m.symbol or "—")}</strong><small>{escape(m.name or "")}</small></td><td>{decimal_or_dash(m.shares)}</td><td>{euro(m.price)}</td><td class="{tone}">{euro(m.amount)}</td><td>{euro(m.fee)}</td><td>{euro(m.tax)}</td><td>{escape(m.currency or "—")}</td><td>{detail}</td></tr>'''


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
    if value is None: return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
