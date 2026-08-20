"""Navigation model for the PFP web application."""

from dataclasses import dataclass


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
)

OPERATIONS = (
    NavigationItem("Activos", "/assets"),
    NavigationItem("Nueva inversión", "/investments/new"),
    NavigationItem("Nueva venta", "/sales/new"),
    NavigationItem("Actualizar datos", "/refresh"),
)

HELP_PATH = "/help"


def navigation_html(active_path: str = "/") -> str:
    links = []
    for item in NAVIGATION:
        active = ' aria-current="page" class="active"' if item.path == active_path else ""
        links.append(f'<a href="{item.path}"{active}>{item.label}</a>')

    operation_active = active_path in {item.path for item in OPERATIONS if item.path != "/refresh"}
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
        f'<a class="help-icon" href="{HELP_PATH}" aria-label="Ayuda" title="Ayuda">?</a>'
    )
    return "<nav>" + "".join(links) + "</nav>"
