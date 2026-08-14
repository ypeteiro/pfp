"""Presentation helpers for the allocation view."""

from decimal import Decimal
from html import escape

from pfp.excel.allocation_actions import AllocationRow, build_allocation_rows
from pfp.reporting.portfolio_report import PortfolioReport

TARGETS = {"RV": Decimal("0.75"), "RF": Decimal("0.20"), "GOLD": Decimal("0.05"), "CRYPTO": Decimal("0")}
LABELS = {"RV": "Renta variable", "RF": "Renta fija", "GOLD": "Oro", "CRYPTO": "Cripto"}


def allocation_html(report: PortfolioReport) -> str:
    values = {"RV": report.equity_value, "RF": report.fixed_income_value, "GOLD": report.gold_value, "CRYPTO": report.crypto_value}
    rows = build_allocation_rows(values, TARGETS, report.market_value)
    total = report.market_value
    recommendation = _recommendation(rows, total)
    table_rows = "".join(_row(row, total) for row in rows)
    return f'''<h1>Asignación</h1><p class="muted">Compara tu cartera actual con el objetivo estratégico y cuantifica el rebalanceo necesario.</p>
<section class="panel allocation-recommendation"><h2>Qué haría ahora</h2><p>{recommendation}</p></section>
<section class="panel"><div class="panel-heading"><h2>Asignación objetivo vs actual</h2><span>{euro(total)} de cartera</span></div><div class="table-scroll"><table><thead><tr><th>Clase</th><th>Objetivo</th><th>Actual</th><th>Desviación</th><th>Valor actual</th><th>Valor objetivo</th><th>Ajuste</th><th>Acción</th></tr></thead><tbody>{table_rows}</tbody></table></div></section>'''


def _row(row: AllocationRow, total: Decimal) -> str:
    target_value = total * row.target
    adjustment = target_value - row.current_value
    tone = "positive" if row.action == "Aumentar" else "negative" if row.action == "Reducir" else ""
    return f'<tr><td><strong>{escape(LABELS.get(row.asset_class, row.asset_class))}</strong><small>{escape(row.asset_class)}</small></td><td>{pct(row.target)}</td><td>{pct(row.current_weight)}</td><td class="{tone}">{pct(row.deviation)}</td><td>{euro(row.current_value)}</td><td>{euro(target_value)}</td><td class="{tone}">{euro(adjustment)}</td><td class="{tone}">{row.action}</td></tr>'


def _recommendation(rows: tuple[AllocationRow, ...], total: Decimal) -> str:
    relevant = [row for row in rows if row.action != "Mantener"]
    if not relevant:
        return "La cartera está dentro del margen de rebalanceo del 2% en todas las clases. No haría cambios solo para corregir pequeñas desviaciones."
    increases = sorted((row for row in relevant if row.action == "Aumentar"), key=lambda row: abs(row.deviation), reverse=True)
    reductions = sorted((row for row in relevant if row.action == "Reducir"), key=lambda row: abs(row.deviation), reverse=True)
    parts = []
    if increases:
        parts.append("Priorizaría " + ", ".join(LABELS.get(row.asset_class, row.asset_class) for row in increases) + ".")
    if reductions:
        parts.append("Reduciría exposición a " + ", ".join(LABELS.get(row.asset_class, row.asset_class) for row in reductions) + ".")
    return " ".join(parts)


def euro(value: Decimal | None) -> str:
    if value is None: return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: Decimal | None) -> str:
    if value is None: return "—"
    return f"{value * 100:.2f}%".replace(".", ",")
