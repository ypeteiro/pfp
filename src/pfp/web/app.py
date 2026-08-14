"""HTTP application routing for the PFP web UI."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.allocation_ui import allocation_html
from pfp.web.dashboard_ui import dashboard_v2_html
from pfp.web.movements_ui import movements_html
from pfp.web.navigation import navigation_html
from pfp.web.positions_ui import positions_html


@dataclass(frozen=True, slots=True)
class WebApp:
    report: PortfolioReport

    def render(self, path: str) -> str:
        parsed = urlsplit(path)
        route = parsed.path
        query = parse_qs(parsed.query)
        sort = query.get("sort", ["weight"])[0]
        direction = query.get("direction", ["desc"])[0]
        pages = {
            "/": self._dashboard,
            "/index.html": self._dashboard,
            "/positions": self._positions,
            "/movements": self._movements,
            "/allocation": self._allocation,
        }
        renderer = pages.get(route)
        if renderer is None:
            raise KeyError(route)
        if route in {"/", "/index.html"}:
            content = self._dashboard(sort, direction)
        elif route == "/positions":
            content = self._positions(sort, direction)
        else:
            content = renderer()
        return self._layout(content, route)

    def _layout(self, content: str, path: str) -> str:
        return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PFP</title><style>{CSS}</style></head><body><header><div><strong>PFP</strong><span>Personal Finance Portfolio</span></div>{navigation_html(path)}</header><main>{content}</main></body></html>'''

    def _dashboard(self, sort: str = "weight", direction: str = "desc") -> str:
        return dashboard_v2_html(self.report, sort, direction)

    def _positions(self, sort: str = "weight", direction: str = "desc") -> str:
        return positions_html(self.report, sort, direction)

    def _movements(self) -> str:
        return movements_html(self.report)

    def _allocation(self) -> str:
        return allocation_html(self.report)


CSS = """
:root{font-family:Inter,Segoe UI,sans-serif;color:#172033;background:#f5f7fb}body{margin:0}header{background:#172033;color:white;padding:18px 32px;display:flex;justify-content:space-between;align-items:center;gap:24px}header strong{font-size:22px}header span{margin-left:12px;color:#aeb8c8;font-size:13px}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{color:#cbd5e1;text-decoration:none;padding:8px 12px;border-radius:8px}nav a.active,nav a:hover{background:#334155;color:white}main{max-width:1180px;margin:0 auto;padding:32px}h1{margin-top:0}.panel{background:white;border:1px solid #e3e8f0;border-radius:14px;padding:20px;box-shadow:0 2px 8px #17203310}.metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:18px 0}.metric{background:white;border:1px solid #e3e8f0;border-radius:12px;padding:16px}.metric-label{display:flex;align-items:center;gap:6px;color:#687386;font-size:12px}.metric strong{display:block;font-size:22px;margin-top:6px}.positive{color:#15803d}.negative{color:#b91c1c}.muted{color:#687386}.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px}.panel-heading h2{margin:0}.panel-heading span{color:#687386;font-size:12px}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse}th,td{padding:11px 12px;border-bottom:1px solid #edf0f5;text-align:left;white-space:nowrap}th{background:#eaf1f8;font-size:13px}.sortable-heading{display:inline-flex;align-items:center;gap:4px;color:inherit;text-decoration:none}.sortable-heading:hover{text-decoration:underline}.sort-arrow{font-size:10px;color:#687386}td small{display:block;color:#687386;font-size:11px;margin-top:3px}.allocation-recommendation{margin:18px 0}.allocation-recommendation h2{margin-top:0}.allocation-label{display:flex;justify-content:space-between;align-items:center;gap:12px}.allocation-name{display:inline-flex;align-items:center;gap:5px}.allocation-label strong{font-size:16px}.allocation-meta{color:#687386;font-size:12px;margin-top:5px}.tooltip{position:relative;display:inline-flex;align-items:center;justify-content:center;color:#8290a5;font-size:13px;cursor:help;line-height:1;outline:none}.tooltip-content{position:absolute;z-index:20;left:50%;bottom:calc(100% + 10px);transform:translateX(-50%);width:260px;padding:12px 14px;border-radius:9px;background:#172033;color:#fff;font-size:12px;line-height:1.5;font-weight:400;box-shadow:0 8px 24px #17203333;opacity:0;visibility:hidden;pointer-events:none;transition:opacity .15s ease}.tooltip-content:after{content:"";position:absolute;left:50%;bottom:-6px;transform:translateX(-50%) rotate(45deg);width:12px;height:12px;background:#172033}.tooltip:hover .tooltip-content,.tooltip:focus .tooltip-content{opacity:1;visibility:visible}.allocation-row{padding:10px 0}.allocation-row+.allocation-row{border-top:1px solid #edf0f5}.bar{height:8px;background:#e9edf3;border-radius:999px;overflow:hidden;margin-top:7px}.bar span{display:block;height:100%;background:#2563eb;border-radius:999px}.evolution-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.evolution-summary>div{background:#f8fafc;border-radius:10px;padding:12px}.evolution-summary span{display:block;color:#687386;font-size:11px}.evolution-summary strong{display:block;margin-top:5px;font-size:17px}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}@media(max-width:800px){header{padding:16px;align-items:flex-start;flex-direction:column}main{padding:18px}.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.two-col{grid-template-columns:1fr}.evolution-summary{grid-template-columns:repeat(2,minmax(0,1fr))}.tooltip-content{left:0;transform:none}.tooltip-content:after{left:12px;transform:rotate(45deg)}}
"""