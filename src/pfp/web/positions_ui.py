"""Presentation helpers for the positions view."""

from decimal import Decimal
from html import escape

from pfp.reporting.portfolio_report import PortfolioReport


def positions_html(report: PortfolioReport) -> str:
    total = report.market_value
    positions = sorted(report.positions, key=lambda p: p.market_value or Decimal("0"), reverse=True)
    rows = []
    for p in positions:
        value = p.market_value
        weight = p.weight if p.weight is not None else (value / total if value is not None and total else None)
        gain = p.gain_loss
        # gain_loss is an absolute amount; divide by invested capital to obtain P/L %.
        gain_pct = (gain / p.invested) if gain is not None and p.invested else None
        tone = "positive" if gain is not None and gain > 0 else "negative" if gain is not None and gain < 0 else ""
        rows.append(
            f'<tr><td><strong>{escape(p.ticker or p.symbol or p.isin)}</strong><small>{escape(p.isin or "")}</small></td>'
            f'<td>{escape(p.name)}</td><td>{escape(p.portfolio_class or "—")}</td><td>{p.shares}</td>'
            f'<td>{euro(p.invested)}</td><td>{euro(p.market_price)}</td><td>{euro(value)}</td>'
            f'<td>{pct(weight)}</td><td class="{tone}">{euro(gain)}<small>{pct(gain_pct)}</small></td></tr>'
        )
    return '<h1>Posiciones</h1><p class="muted">Detalle de cada activo, ordenado por peso en cartera.</p><section class="panel positions-panel"><table><thead><tr><th>Activo</th><th>Nombre</th><th>Clase</th><th>Participaciones</th><th>Invertido</th><th>Precio</th><th>Valor</th><th>Peso</th><th>P/L</th></tr></thead><tbody>' + ''.join(rows or ['<tr><td colspan="9">Sin posiciones</td></tr>']) + '</tbody></table></section>'


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%".replace(".", ",")
