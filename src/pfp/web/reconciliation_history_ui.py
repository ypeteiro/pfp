from html import escape


def reconciliation_history_html(records=(), account_id=None):
    accounts = sorted({record.account_id for record in records})
    selected = account_id or (accounts[0] if accounts else "")
    history = [record for record in records if record.account_id == selected]

    options = ''.join(
        f'<option value="{escape(account)}"{" selected" if account == selected else ""}>{escape(account)}</option>'
        for account in accounts
    )
    if not options:
        options = '<option value="">Sin cuentas con historial</option>'

    rows = ''.join(
        '<tr>'
        f'<td>{record.datetime:%Y-%m-%d %H:%M:%S}</td>'
        f'<td>{record.expected_balance:.2f} €</td>'
        f'<td>{record.calculated_balance:.2f} €</td>'
        f'<td class="{"positive" if record.difference == 0 else "negative"}">{record.difference:.2f} €</td>'
        f'<td>{escape(record.status)}</td>'
        '</tr>'
        for record in reversed(history)
    )
    if not rows:
        rows = '<tr><td colspan="5" class="muted">No hay registros de conciliación para esta cuenta.</td></tr>'

    return f'''<h1>Historial de conciliación</h1>
<div class="panel">
  <form class="history-filter" method="get" action="/reconciliation-history">
    <label for="account_id">Cuenta</label>
    <select id="account_id" name="account_id" onchange="this.form.submit()">{options}</select>
    <noscript><button type="submit">Mostrar</button></noscript>
  </form>
</div>
<div class="panel" style="margin-top:18px">
  <div class="panel-heading"><h2>{escape(selected) if selected else 'Historial'}</h2><span>{len(history)} registro(s)</span></div>
  <div class="table-scroll"><table>
    <thead><tr><th>Fecha</th><th>Esperado</th><th>Calculado</th><th>Diferencia</th><th>Estado</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</div>'''
