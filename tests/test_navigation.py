from pfp.web.navigation import NAVIGATION, OPERATIONS, navigation_html


def test_navigation_contains_main_sections():
    assert [item.label for item in NAVIGATION] == [
        "Dashboard",
        "Cuentas",
        "Posiciones",
        "Movimientos",
        "Asignación",
        "Rebalanceo",
        "Conciliación",
    ]
    assert any(item.path == "/rebalance" for item in NAVIGATION)
    assert any(item.path == "/reconciliation-history" for item in NAVIGATION)


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

    operations_start = html.index('<details class="operations-menu"')
    operations_end = html.index("</details>", operations_start)
    operations_html = html[operations_start:operations_end]
    assert 'href="/refresh"' not in operations_html


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
