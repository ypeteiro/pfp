from pfp.web.asset_ui import asset_form_html


def test_asset_form_autocompletes_identity_from_isin():
    html = asset_form_html()

    assert '/assets/lookup?isin=' in html
    assert 'Datos encontrados en Yahoo Finance.' in html
    assert 'name="isin"' in html
    assert 'name="ticker"' in html
    assert 'name="name"' in html
