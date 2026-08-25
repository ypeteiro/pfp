from html import escape


def reconciliation_html(accounts=(), selected_account_id=None, error=None, values=None, result=None):
    values = values or {}
    selected = selected_account_id or (accounts[0].id if accounts else "")
    options = "".join(
        f'<option value="{escape(account.id)}"{" selected" if account.id == selected else ""}>{escape(account.id)}</option>'
        for account in accounts
    )
    if not options:
        options = '<option value="">No hay cuentas disponibles</option>'

    error_html = f'<div class="form-error">{escape(error)}</div>' if error else ""
    result_html = ""
    if result is not None:
        status = "RECONCILED" if result.is_reconciled else "MISMATCH"
        css = "positive" if result.is_reconciled else "negative"
        result_html = f'''<div class="panel reconciliation-result">
  <div class="panel-heading"><h2>Resultado</h2><strong class="{css}">{status}</strong></div>
  <table><tbody>
    <tr><th>Cuenta</th><td>{escape(result.account_id)}</td></tr>
    <tr><th>Saldo esperado</th><td>{result.expected_balance:.2f} €</td></tr>
    <tr><th>Saldo calculado</th><td>{result.calculated_balance:.2f} €</td></tr>
    <tr><th>Diferencia</th><td class="{css}">{result.difference:.2f} €</td></tr>
  </tbody></table>
</div>'''

    return f'''<h1>Conciliación</h1>
<div class="panel">
  <p class="muted">Introduce el saldo real/esperado de la cuenta para compararlo con el saldo calculado por PFP.</p>
  {error_html}
  <form class="investment-form" method="post" action="/reconcile">
    <label>Cuenta<select name="account_id">{options}</select></label>
    <label>Saldo esperado<input name="expected_balance" inputmode="decimal" value="{escape(values.get("expected_balance", ""))}" placeholder="0.00" required></label>
    <div class="form-actions"><button type="submit">Conciliar</button></div>
  </form>
</div>
{result_html}'''
