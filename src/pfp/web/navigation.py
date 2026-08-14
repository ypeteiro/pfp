"""Navigation model for the PFP web application."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NavigationItem:
    label: str
    path: str


NAVIGATION = (
    NavigationItem("Dashboard", "/"),
    NavigationItem("Posiciones", "/positions"),
    NavigationItem("Movimientos", "/movements"),
    NavigationItem("Asignación", "/allocation"),
)


def navigation_html(active_path: str = "/") -> str:
    links = []
    for item in NAVIGATION:
        active = ' aria-current="page" class="active"' if item.path == active_path else ""
        links.append(f'<a href="{item.path}"{active}>{item.label}</a>')
    return "<nav>" + "".join(links) + "</nav>"
