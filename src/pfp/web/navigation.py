"""Navigation model for the PFP web application."""

from dataclasses import dataclass


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
    NavigationItem("Ayuda / README", "https://github.com/ypeteiro/pfp#readme", external=True),
)


def navigation_html(active_path: str = "/") -> str:
    links = []
    for item in NAVIGATION:
        active = ' aria-current="page" class="active"' if not item.external and item.path == active_path else ""
        target = ' target="_blank" rel="noopener noreferrer"' if item.external else ""
        links.append(f'<a href="{item.path}"{active}{target}>{item.label}</a>')
    return "<nav>" + "".join(links) + "</nav>"
