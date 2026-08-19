from html import escape


PORTFOLIO_CLASSES = ("EQUITY", "STOCK", "FIXED_INCOME", "GOLD", "CRYPTO", "UNKNOWN")


def assets_html(assets) -> str:
    rows = "".join(
        f'<tr><td>{escape(asset.symbol)}</td><td>{escape(asset.name)}</td><td>{escape(asset.ticker or "")}</td><td>{escape(asset.isin or "")}</td><td>{escape(asset.portfolio_class)}</td></tr>'
        for asset in sorted(assets, key=lambda item: item.symbol)
    )
    if not rows:
        rows = '<tr><td colspan="5" class="muted">No hay activos configurados.</td></tr>'
    return f'''<div class="panel-heading"><div><h1>Activos</h1><span>Catálogo de instrumentos disponible para el portfolio.</span></div><a class="new-investment-link" href="/assets/new">+ Nuevo activo</a></div>
<section class="panel"><div class="table-scroll"><table><thead><tr><th>Símbolo</th><th>Nombre</th><th>Ticker</th><th>ISIN</th><th>Clase</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''


def asset_form_html(error: str | None = None, values: dict[str, str] | None = None) -> str:
    values = values or {}
    error_html = f'<div class="form-error" role="alert">{escape(error)}</div>' if error else ""
    return f'''<h1>Nuevo activo</h1><p class="muted">Añade un instrumento sin modificar el código de PFP.</p><section class="panel investment-form-panel">{error_html}<form class="investment-form" method="post" action="/assets">
<label>Símbolo<input required type="text" name="symbol" value="{value(values, "symbol")}" placeholder="US1234567890"></label>
<label>Nombre<input required type="text" name="name" value="{value(values, "name")}"></label>
<label>Ticker <span class="muted">(opcional)</span><input type="text" name="ticker" value="{value(values, "ticker")}"></label>
<label>ISIN <span class="muted">(opcional)</span><input type="text" name="isin" value="{value(values, "isin")}"></label>
<label>Clase de cartera<select required name="portfolio_class">{portfolio_class_options(values.get("portfolio_class", "STOCK"))}</select></label>
<div class="form-actions"><button type="submit">Guardar activo</button><a class="filter-reset" href="/assets">Cancelar</a></div>
</form></section>'''


def value(values: dict[str, str], key: str) -> str:
    return escape(str(values.get(key, "")), quote=True)


def portfolio_class_options(selected: str) -> str:
    return "".join(f'<option value="{item}"{" selected" if item == selected else ""}>{item}</option>' for item in PORTFOLIO_CLASSES)
