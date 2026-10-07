from pfp.web.navigation import NAVIGATION, OPERATIONS, PORTFOLIO, navigation_html


def test_navigation_contains_main_sections():
    assert [item.label for item in NAVIGATION] == [
        "Dashboard",
        "Cuentas",
        "Posiciones",
        "Movimientos",
        "Conciliación",
    ]
    assert any(item.path == "/reconciliation-history" for item in NAVIGATION)


def test_portfolio_sections_are_grouped_in_dropdown():
    assert [item.label for item in PORTFOLIO] == [
        "Asignación",
        "Objetivos",
        "Rebalanceo",
    ]
    html = navigation_html("/targets")
    assert "Cartera" in html
    assert 'href="/allocation"' in html
    assert 'href="/targets"' in html
    assert 'href="/rebalance"' in html
    assert 'href="/targets" aria-current="page" class="active"' in html
    assert " open" in html

    portfolio_start = html.index('<details class="operations-menu"')
    portfolio_end = html.index("</details>", portfolio_start)
    portfolio_html = html[portfolio_start:portfolio_end]
    assert 'href="/refresh"' not in portfolio_html


def test_operations_are_grouped_in_dropdown_without_refresh():
    assert [item.label for item in OPERATIONS] == [
        "Activos",
        "Nueva inversión",
        "Nueva venta",
    ]
    html = navigation_html("/investments/new")
    assert "Operaciones" in html
    assert 'href="/assets"' in html
    assert 'href="/investments/new"' in html
    assert 'href="/sales/new"' in html
    assert 'href="/refresh"' in html
    assert 'class="refresh-icon"' in html
    assert 'aria-label="Actualizar datos"' in html
    assert " open" in html


def test_navigation_marks_active_page_and_help_icon():
    html = navigation_html("/positions")
    assert 'href="/positions"' in html
    assert 'aria-current="page" class="active"' in html
    assert 'href="/"' in html
    assert 'class="help-icon"' in html
    assert 'aria-label="Ayuda / README"' in html
    assert 'title="Ayuda / README"' in html
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html
