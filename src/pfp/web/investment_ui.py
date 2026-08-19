"""Presentation helpers for the web investment form."""

from html import escape


PORTFOLIO_CLASSES = ("RV", "RF", "GOLD", "CRYPTO")


def investment_form_html(error: str | None = None, values: dict[str, str] | None = None, assets=()) -> str:
    values = values or {}
    error_html = f'<div class="form-error" role="alert">{escape(error)}</div>' if error else ""
    asset_options = "".join(f'<option value="{escape(asset.symbol, quote=True)}">{escape(asset.name)}</option>' for asset in assets)
    return f'''<h1>Registrar inversión</h1>
<p class="muted">Registra una compra en el portfolio actual. El campo Activo usa el catálogo configurado en PFP.</p>
<section class="panel investment-form-panel">{error_html}
<form class="investment-form" method="post" action="/investments">
<label>Fecha y hora<input required type="datetime-local" name="datetime" value="{value(values, "datetime")}"></label>
<label>Activo<input required type="text" name="symbol" value="{value(values, "symbol")}" placeholder="VWCE" autocomplete="off" list="asset-options"><datalist id="asset-options">{asset_options}</datalist></label>
<label>Participaciones<input required type="number" name="shares" value="{value(values, "shares")}" min="0" step="any"></label>
<label>Precio<input required type="number" name="price" value="{value(values, "price")}" min="0" step="any"></label>
<label>Importe<input required type="number" name="amount" value="{value(values, "amount")}" min="0" step="any"></label>
<label>Clase de cartera<select required name="portfolio_class">{portfolio_class_options(values.get("portfolio_class", "RV"))}</select></label>
<label>Broker<input required type="text" name="broker" value="{value(values, "broker", "Trade Republic")}"></label>
<label>ID de operación <span class="muted">(opcional)</span><input type="text" name="operation_id" value="{value(values, "operation_id")}" autocomplete="off"></label>
<div class="form-actions"><button type="submit">Registrar inversión</button><a class="filter-reset" href="/positions">Cancelar</a></div>
</form></section>'''


def value(values: dict[str, str], key: str, default: str = "") -> str:
    return escape(str(values.get(key, default)), quote=True)


def portfolio_class_options(selected: str) -> str:
    return "".join(
        f'<option value="{escape(item, quote=True)}"{" selected" if item == selected else ""}>{escape(item)}</option>'
        for item in PORTFOLIO_CLASSES
    )
