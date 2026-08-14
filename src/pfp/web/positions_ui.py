"""Presentation helpers for the positions view."""

from decimal import Decimal
from html import escape

from pfp.reporting.portfolio_report import PortfolioReport


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
        rows.append(
            f'<tr><td><strong>{escape(p.ticker or p.symbol or p.isin)}</strong><small>{escape(p.isin or "")}</small></td>'
            f'<td>{escape(p.name)}</td><td>{escape(p.portfolio_class or "—")}</td><td>{p.shares}</td>'
            f'<td>{euro(p.invested)}</td><td>{euro(p.market_price)}</td><td>{euro(value)}</td>'
            f'<td>{pct(weight)}</td><td class="{tone}">{euro(gain)}<small>{pct(gain_pct)}</small></td></tr>'
        )
    headers = (
        '<th>Activo</th>'
        f'{sort_heading("Nombre", "name", sort, direction)}'
        '<th>Clase</th><th>Participaciones</th><th>Invertido</th><th>Precio</th>'
        f'{sort_heading("Valor", "value", sort, direction)}'
        f'{sort_heading("Peso", "weight", sort, direction)}'
        '<th>P/L</th>'
    )
    empty = '<tr><td colspan="9">Sin posiciones</td></tr>'
    return '<h1>Posiciones</h1><p class="muted">Detalle de cada activo. Haz clic en Nombre, Valor o Peso para ordenar.</p><section class="panel positions-panel"><div class="table-scroll"><table><thead><tr>' + headers + '</tr></thead><tbody>' + ''.join(rows or [empty]) + '</tbody></table></div></section>'


def sort_positions(report: PortfolioReport, sort: str, direction: str):
    key_map = {
        "name": lambda p: (p.name or "").lower(),
        "weight": lambda p: p.weight if p.weight is not None else Decimal("-1"),
        "value": lambda p: p.market_value if p.market_value is not None else Decimal("-1"),
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