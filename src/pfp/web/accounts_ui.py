from __future__ import annotations

from decimal import Decimal

from pfp.reporting.portfolio_report import PortfolioReport


def _money(value: Decimal | None) -> str:
    if value is None:
        return "N/D"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def _account_row(account) -> str:
    category = "Efectivo invertible" if account.is_investable else "Fondo de seguridad"
    market_value = account.market_value if account.market_value is not None else Decimal("0")
    total = account.total_value
    return f'''<tr>
<td><strong>{account.name}</strong><small>{account.broker} · {account.currency}</small></td>
<td>{category}</td>
<td>{_money(account.balance)}</td>
<td>{_money(account.invested)}</td>
<td>{_money(market_value if account.market_value is not None else None)}</td>
<td><strong>{_money(total)}</strong></td>
</tr>'''


def _account_options(accounts, selected: str | None = None) -> str:
    return "".join(
        f'<option value="{account.account_id}"{" selected" if account.account_id == selected else ""}>{account.name} ({account.currency})</option>'
        for account in accounts
    )


def accounts_html(report: PortfolioReport) -> str:
    investable = [account for account in report.accounts if account.is_investable]
    security = [account for account in report.accounts if not account.is_investable]

    investable_cash = sum((account.balance for account in investable), Decimal("0"))
    security_cash = sum((account.balance for account in security), Decimal("0"))
    accounts = list(report.accounts)
    options = _account_options(accounts)

    def section(title: str, accounts: list) -> str:
        rows = "".join(_account_row(account) for account in accounts)
        if not rows:
            rows = '<tr><td colspan="6" class="muted">No hay cuentas en esta categoría.</td></tr>'
        return f'''<section class="panel accounts-section">
<div class="panel-heading"><h2>{title}</h2><span>{len(accounts)} cuenta{'s' if len(accounts) != 1 else ''}</span></div>
<div class="table-scroll"><table><thead><tr><th>Cuenta</th><th>Tipo</th><th>Efectivo</th><th>Coste invertido</th><th>Valor mercado</th><th>Patrimonio</th></tr></thead><tbody>{rows}</tbody></table></div>
</section>'''

    return f'''<div class="accounts-page">
<h1>Cuentas</h1>
<p class="muted">Consulta y modifica el efectivo de tus cuentas y registra traspasos entre ellas.</p>
<div class="metric-grid">
<div class="metric"><div class="metric-label">Efectivo invertible</div><strong>{_money(investable_cash)}</strong></div>
<div class="metric"><div class="metric-label">Fondo de seguridad</div><strong>{_money(security_cash)}</strong></div>
<div class="metric"><div class="metric-label">Efectivo total</div><strong>{_money(report.cash)}</strong></div>
<div class="metric"><div class="metric-label">Patrimonio total</div><strong>{_money(report.total_value)}</strong></div>
</div>
<section class="panel accounts-section">
<div class="panel-heading"><h2>Modificar saldo</h2><span>Se registra como movimiento externo para conservar el histórico.</span></div>
<form method="post" action="/accounts/adjust" class="investment-form">
<label>Cuenta<select name="account_id" required>{options}</select></label>
<label>Saldo actual que quieres establecer<input name="target_balance" type="number" step="0.01" min="0" required></label>
<label>Fecha y hora<input name="datetime" type="datetime-local" required></label>
<label>Descripción<input name="description" value="Ajuste manual de saldo"></label>
<div class="form-actions"><button type="submit">Guardar saldo</button></div>
</form>
</section>
<section class="panel accounts-section">
<div class="panel-heading"><h2>Traspaso entre cuentas</h2><span>El patrimonio total no cambia.</span></div>
<form method="post" action="/account-transfers" class="investment-form">
<label>Cuenta origen<select name="source_account" required>{options}</select></label>
<label>Cuenta destino<select name="destination_account" required>{options}</select></label>
<label>Importe<input name="amount" type="number" step="0.01" min="0.01" required></label>
<label>Fecha y hora<input name="datetime" type="datetime-local" required></label>
<div class="form-actions"><button type="submit">Registrar traspaso</button></div>
</form>
</section>
{section("Efectivo invertible", investable)}
{section("Fondo de seguridad", security)}
</div>'''
