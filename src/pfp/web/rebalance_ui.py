from __future__ import annotations

from decimal import Decimal
from html import escape
from urllib.parse import quote

from pfp.engine.rebalance_engine import RebalanceEngine


def _money(value: Decimal) -> str:
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def rebalance_html(portfolio, account_id: str | None = None) -> str:
    accounts = [account for account in portfolio.accounts if account.id]
    selected = account_id or (accounts[0].id if accounts else None)
    options = "".join(
        f'<option value="{escape(account.id, quote=True)}"{" selected" if account.id == selected else ""}>{escape(account.name)} · {escape(account.broker)}</option>'
        for account in accounts
    )
    if selected is None:
        return '<h1>Rebalanceo</h1><section class="panel"><p class="muted">No hay cuentas disponibles para rebalancear.</p></section>'

    result = RebalanceEngine().rebalance(portfolio, account_id=selected)
    rows = "".join(
        f'<tr><td>{escape(order.action)}</td><td><strong>{escape(order.symbol)}</strong><small>{escape(order.asset_name)}</small></td><td>{escape(order.portfolio_class)}</td><td>{_money(order.amount)}</td><td>{order.shares if order.shares is not None else "—"}</td></tr>'
        for order in result.orders
    )
    if not rows:
        rows = '<tr><td colspan="5" class="muted">No hay órdenes que ejecutar.</td></tr>'

    return f'''<div class="rebalance-page">
<h1>Rebalanceo</h1>
<p class="muted">Vista previa del rebalanceo exclusivamente sobre la cuenta seleccionada. Calcular no ejecuta ninguna operación.</p>
<section class="panel">
<form method="get" action="/rebalance" class="investment-form">
<label>Cuenta<select name="account_id">{options}</select></label>
<div class="form-actions"><button type="submit">Calcular rebalanceo</button></div>
</form>
</section>
<div class="metric-grid">
<div class="metric"><div class="metric-label">Cuenta seleccionada</div><strong>{escape(selected)}</strong></div>
<div class="metric"><div class="metric-label">Valor rebalanceable</div><strong>{_money(result.rebalanceable_value)}</strong></div>
<div class="metric"><div class="metric-label">Órdenes</div><strong>{len(result.orders)}</strong></div>
<div class="metric"><div class="metric-label">Valor total cartera</div><strong>{_money(result.total_value)}</strong></div>
</div>
<section class="panel"><div class="panel-heading"><h2>Órdenes propuestas</h2><span>Solo vista previa</span></div><div class="table-scroll"><table><thead><tr><th>Acción</th><th>Activo</th><th>Clase</th><th>Importe</th><th>Participaciones</th></tr></thead><tbody>{rows}</tbody></table></div></section>
</div>'''
