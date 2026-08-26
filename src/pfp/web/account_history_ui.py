from __future__ import annotations

from decimal import Decimal


def _money(value: Decimal) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def account_history_html(accounts, external_cash_movements, account_transfers) -> str:
    account_names = {account.id: account.name for account in accounts}
    for account in accounts:
        account_names.setdefault(account.id, account.name)

    sections = []
    for account in sorted(accounts, key=lambda item: (item.broker, item.name)):
        events = []
        for movement in external_cash_movements:
            if movement.account_id == account.id:
                events.append((movement.datetime, "Movimiento externo", movement.description or "Movimiento externo", movement.amount))
        for transfer in account_transfers:
            if transfer.source_account == account.id:
                events.append((transfer.datetime, "Traspaso enviado", f"A {account_names.get(transfer.destination_account, transfer.destination_account)}", -transfer.amount))
            elif transfer.destination_account == account.id:
                events.append((transfer.datetime, "Traspaso recibido", f"De {account_names.get(transfer.source_account, transfer.source_account)}", transfer.amount))
        events.sort(key=lambda event: event[0], reverse=True)
        rows = []
        for when, kind, description, amount in events:
            amount_class = "positive" if amount > 0 else "negative"
            rows.append(
                f'<tr><td>{when.strftime("%d/%m/%Y %H:%M")}</td><td>{kind}</td><td>{description}</td><td class="{amount_class}"><strong>{_money(amount)}</strong></td></tr>'
            )
        if not rows:
            rows.append('<tr><td colspan="4" class="muted">No hay movimientos registrados.</td></tr>')
        sections.append(
            f'''<section class="panel accounts-section"><div class="panel-heading"><h2>{account.name}</h2><span>{len(events)} movimiento{'s' if len(events) != 1 else ''}</span></div><div class="table-scroll"><table><thead><tr><th>Fecha</th><th>Tipo</th><th>Descripción</th><th>Importe</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>'''
        )

    return "".join(sections) or '<section class="panel accounts-section"><p class="muted">No hay cuentas.</p></section>'
