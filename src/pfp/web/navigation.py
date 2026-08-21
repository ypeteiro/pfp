"""Navigation model for the PFP web application."""

from dataclasses import dataclass
from html import escape


@dataclass(frozen=True, slots=True)
class NavigationItem:
    label: str
    path: str
    external: bool = False


NAVIGATION = (
    NavigationItem("Dashboard", "/"),
    NavigationItem("Cuentas", "/accounts"),
    NavigationItem("Posiciones", "/positions"),
    NavigationItem("Movimientos", "/movements"),
    NavigationItem("Asignación", "/allocation"),
    NavigationItem("Rebalanceo", "/rebalance"),
)

OPERATIONS = (
    NavigationItem("Activos", "/assets"),
    NavigationItem("Nueva inversión", "/investments/new"),
    NavigationItem("Nueva venta", "/sales/new"),
)

README_URL = "https://github.com/ypeteiro/pfp/blob/develop/README.md"
REFRESH_PATH = "/refresh"


def navigation_html(active_path: str = "/") -> str:
    links = []
    for item in NAVIGATION:
        active = ' aria-current="page" class="active"' if item.path == active_path else ""
        links.append(f'<a href="{item.path}"{active}>{item.label}</a>')

    operation_active = active_path in {item.path for item in OPERATIONS}
    open_attr = " open" if operation_active else ""
    operation_links = "".join(
        f'<a href="{item.path}">{item.label}</a>' for item in OPERATIONS
    )
    links.append(
        f'<details class="operations-menu"{open_attr}>'
        f'<summary>Operaciones</summary>'
        f'<div class="operations-dropdown">{operation_links}</div>'
        f'</details>'
    )
    links.append(
        f'<a class="refresh-icon" href="{REFRESH_PATH}" aria-label="Actualizar datos" '
        'title="Actualizar datos">↻</a>'
    )
    links.append(
        f'<a class="help-icon" href="{escape(README_URL, quote=True)}" target="_blank" '
        'rel="noopener noreferrer" aria-label="Ayuda / README" title="Ayuda / README">'
        '<span aria-hidden="true">?</span><span class="sr-only">Ayuda / README</span></a>'
    )
    return "<nav>" + "".join(links) + "</nav>"
