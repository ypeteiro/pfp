from pfp.web.investment_ui import investment_form_html, portfolio_class_options


def test_investment_form_contains_required_fields_and_post_target():
    html = investment_form_html()
    assert '<form class="investment-form" method="post" action="/investments">' in html
    for field in ("datetime", "symbol", "shares", "price", "amount", "portfolio_class", "broker", "operation_id"):
        assert f'name="{field}"' in html
    assert "Registrar inversión" in html


def test_investment_form_escapes_values():
    html = investment_form_html(values={"symbol": '<VWCE&"', "broker": 'TR "broker"'})
    assert "&lt;VWCE&amp;&quot;" in html
    assert "TR &quot;broker&quot;" in html
    assert "<VWCE" not in html


def test_portfolio_class_options_selects_requested_class():
    html = portfolio_class_options("GOLD")
    assert '<option value="GOLD" selected>GOLD</option>' in html
    assert '<option value="RV">RV</option>' in html
