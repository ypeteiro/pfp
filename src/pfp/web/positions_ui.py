"""Presentation helpers for the positions view."""

from datetime import date
from decimal import Decimal
from html import escape

from pfp.reporting.portfolio_report import PortfolioReport

YAHOO_SYMBOLS = {
    "BTC", "IE00BK5BQT80", "IE00B4L5Y983", "IE00BG47KH54",
    "IE00BKM4GZ66", "IE00B5BMR087", "IE00B4ND3602", "IE000I1Q42S9",
}
VANGUARD_SYMBOLS = {"IE00B03HD191"}


def positions_html(report: PortfolioReport, sort: str = "weight", direction: str = "desc") -> str:
    total = report.market_value
    positions = sort_positions(report, sort, direction)
    rows = []
    for p in positions:
        value = p.market_value
        weight = p.weight if p.weight is not None else (value / total if value is not None and total else None)
        gain = p.gain_loss
        gain_pct = (gain / p.invested) if gain is not None and p.invested else None
        tone = "positive" if gain is not None and gain > 0 else "negative" if gain is not None and gain < 0 else ""
        price = euro(p.market_price)
        if p.market_price is not None:
            price += price_tooltip(p.symbol)
        rows.append(
            f'<tr><td><strong>{escape(p.ticker or p.symbol or p.isin)}</strong><small>{escape(p.isin or "")}</small></td>'
            f'<td>{escape(p.name)}</td><td>{escape(p.portfolio_class or "—")}</td><td>{p.shares}</td>'
            f'<td>{euro(p.invested)}</td><td>{price}</td><td>{euro(value)}</td>'
            f'<td>{pct(weight)}</td><td class="{tone}">{euro(gain)}<small>{pct(gain_pct)}</small></td></tr>'
        )
    headers = (
        f'{sort_heading("Activo", "symbol", sort, direction)}'
        f'{sort_heading("Nombre", "name", sort, direction)}'
        f'{sort_heading("Clase", "class", sort, direction)}'
        f'{sort_heading("Participaciones", "shares", sort, direction)}'
        f'{sort_heading("Invertido", "invested", sort, direction)}'
        f'{sort_heading("Precio", "price", sort, direction)}'
        f'{sort_heading("Valor", "value", sort, direction)}'
        f'{sort_heading("Peso", "weight", sort, direction)}'
        f'{sort_heading("P/L", "gain", sort, direction)}'
    )
    empty = '<tr><td colspan="9">Sin posiciones</td></tr>'
    return '<h1>Posiciones</h1><p class="muted">Detalle de cada activo. Haz clic en cualquier columna para ordenar.</p><section class="panel positions-panel"><div class="table-scroll"><table><thead><tr>' + headers + '</tr></thead><tbody>' + ''.join(rows or [empty]) + '</tbody></table></div></section>'


def price_tooltip(symbol: str) -> str:
    if symbol in VANGUARD_SYMBOLS:
        source = "Vanguard"
    elif symbol in YAHOO_SYMBOLS:
        source = "Yahoo Finance"
    else:
        source = "Proveedor de precios"
    consulted = date.today().strftime("%d/%m/%Y")
    text = f"Fuente: {source}. Fecha de consulta: {consulted}. Último precio disponible obtenido por PFP."
    return f'<span class="tooltip price-tooltip" tabindex="0" aria-label="Información del precio">ⓘ<span class="tooltip-content">{escape(text)}</span></span>'


def sort_positions(report: PortfolioReport, sort: str, direction: str):
    symbol = lambda p: (p.ticker or p.symbol or p.isin or "").lower()
    key_map = {
        "symbol": lambda p: (symbol(p),),
        "name": lambda p: ((p.name or "").lower(), symbol(p)),
        "class": lambda p: ((p.portfolio_class or "").lower(), symbol(p)),
        "shares": lambda p: (p.shares, symbol(p)),
        "invested": lambda p: (p.invested, symbol(p)),
        "price": lambda p: (p.market_price if p.market_price is not None else Decimal("-1"), symbol(p)),
        "value": lambda p: (p.market_value if p.market_value is not None else Decimal("-1"), symbol(p)),
        "weight": lambda p: (p.weight if p.weight is not None else Decimal("-1"), symbol(p)),
        "gain": lambda p: (p.gain_loss if p.gain_loss is not None else Decimal("-1"), symbol(p)),
    }
    key = key_map.get(sort, key_map["weight"])
    return sorted(report.positions, key=key, reverse=direction != "asc")


def sort_heading(label: str, field: str, current: str, direction: str) -> str:
    next_direction = "asc" if current == field and direction != "asc" else "desc"
    arrow = "↑" if current == field and direction == "asc" else "↓" if current == field else "↕"
    return f'<th><a class="sortable-heading" href="/positions?sort={field}&direction={next_direction}">{label}<span class="sort-arrow">{arrow}</span></a></th>'


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%".replace(".", ",")
