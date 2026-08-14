from pfp.web.navigation import NAVIGATION, navigation_html


def test_navigation_contains_main_sections():
    assert [item.label for item in NAVIGATION] == [
        "Dashboard",
        "Posiciones",
        "Movimientos",
        "Asignación",
    ]


def test_navigation_marks_active_page():
    html = navigation_html("/positions")
    assert 'href="/positions"' in html
    assert 'aria-current="page" class="active"' in html
    assert 'href="/"' in html
