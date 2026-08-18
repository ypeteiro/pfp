from html import escape


def sale_form_html(error: str | None = None, values: dict[str, str] | None = None) -> str:
    values = values or {}
    error_html = f'<div class="form-error" role="alert">{escape(error)}</div>' if error else ""
    return f'''<h1>Registrar venta</h1>
<p class="muted">Registra una venta en el portfolio actual. La posición y el efectivo se actualizan al registrar la operación.</p>
<section class="panel investment-form-panel">{error_html}
<form class="investment-form" method="post" action="/sales">
<label>Fecha y hora<input required type="datetime-local" name="datetime" value="{value(values, "datetime")}"></label>
<label>Activo<input required type="text" name="symbol" value="{value(values, "symbol")}" placeholder="VWCE" autocomplete="off"></label>
<label>Participaciones<input required type="number" name="shares" value="{value(values, "shares")}" min="0" step="any"></label>
<label>Precio<input required type="number" name="price" value="{value(values, "price")}" min="0" step="any"></label>
<label>Importe<input required type="number" name="amount" value="{value(values, "amount")}" min="0" step="any"></label>
<label>Broker<input required type="text" name="broker" value="{value(values, "broker", "Trade Republic")}"></label>
<label>ID de operación <span class="muted">(opcional)</span><input type="text" name="operation_id" value="{value(values, "operation_id")}" autocomplete="off"></label>
<div class="form-actions"><button type="submit">Registrar venta</button><a class="filter-reset" href="/positions">Cancelar</a></div>
</form></section>'''


def value(values: dict[str, str], key: str, default: str = "") -> str:
    return escape(str(values.get(key, default)), quote=True)
