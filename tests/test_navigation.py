from pfp.web.navigation import NAVIGATION, OPERATIONS, navigation_html


def test_navigation_contains_main_sections():
    assert [item.label for item in NAVIGATION] == [
        "Dashboard",
        "Cuentas",
        "Posiciones",
        "Movimientos",
        "Asignación",
    ]


def test_operations_are_grouped_in_dropdown():
    assert [item.label for item in OPERATIONS] == [
        "Activos",
        "Nueva inversión",
        "Nueva venta",
        "Actualizar datos",
    ]
    html = navigation_html("/investments/new")
    assert "Operaciones" in html
    assert 'href="/assets"' in html
    assert 'href="/investments/new"' in html
    assert 'href="/sales/new"' in html
    assert 'href="/refresh"' in html
    assert " open" in html


def test_navigation_marks_active_page_and_help_icon():
    html = navigation_html("/positions")
    assert 'href="/positions"' in html
    assert 'aria-current="page" class="active"' in html
    assert 'href="/"' in html
    assert 'href="/help"' in html
    assert 'aria-label="Ayuda"' in html
