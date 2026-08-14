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
    NavigationItem("Posiciones", "/positions"),
    NavigationItem("Movimientos", "/movements"),
    NavigationItem("Asignación", "/allocation"),
)

README_URL = "https://github.com/ypeteiro/pfp/blob/develop/README.md"


def navigation_html(active_path: str = "/") -> str:
    links = []
    for item in NAVIGATION:
        active = ' aria-current="page" class="active"' if not item.external and item.path == active_path else ""
        target = ' target="_blank" rel="noopener noreferrer"' if item.external else ""
        links.append(f'<a href="{item.path}"{active}{target}>{item.label}</a>')
    links.append(
        f'<a href="{escape(README_URL, quote=True)}" target="_blank" '
        'rel="noopener noreferrer" class="help-link">Ayuda / README</a>'
    )
    return "<nav>" + "".join(links) + "</nav>"
