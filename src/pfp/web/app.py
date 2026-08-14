"""HTTP application routing for the PFP web UI."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

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
        pages = {"/": self._dashboard, "/index.html": self._dashboard, "/positions": self._positions, "/movements": self._movements, "/allocation": self._allocation}
        renderer = pages.get(path)
        if renderer is None:
            raise KeyError(path)
        return self._layout(renderer(), path)

    def _layout(self, content: str, path: str) -> str:
        return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PFP</title><style>{CSS}</style></head><body><header><div><strong>PFP</strong><span>Personal Finance Portfolio</span></div>{navigation_html(path)}</header><main>{content}</main></body></html>'''

    def _dashboard(self) -> str:
        return dashboard_v2_html(self.report)

    def _positions(self) -> str:
        return positions_html(self.report)

    def _movements(self) -> str:
        return movements_html(self.report)

    def _allocation(self) -> str:
        return allocation_html(self.report)


CSS = """
:root{font-family:Inter,Segoe UI,sans-serif;color:#172033;background:#f5f7fb}body{margin:0}header{background:#172033;color:white;padding:18px 32px;display:flex;justify-content:space-between;align-items:center;gap:24px}header strong{font-size:22px}header span{margin-left:12px;color:#aeb8c8;font-size:13px}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{color:#cbd5e1;text-decoration:none;padding:8px 12px;border-radius:8px}nav a.active,nav a:hover{background:#334155;color:white}main{max-width:1180px;margin:0 auto;padding:32px}h1{margin-top:0}.panel{background:white;border:1px solid #e3e8f0;border-radius:14px;padding:20px;box-shadow:0 2px 8px #17203310}.metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:18px 0}.metric{background:white;border:1px solid #e3e8f0;border-radius:12px;padding:16px}.metric span{display:block;color:#687386;font-size:12px}.metric strong{display:block;font-size:22px;margin-top:6px}.positive{color:#15803d}.negative{color:#b91c1c}.muted{color:#687386}.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px}.panel-heading h2{margin:0}.panel-heading span{color:#687386;font-size:12px}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse}th,td{padding:11px 12px;border-bottom:1px solid #edf0f5;text-align:left;white-space:nowrap}th{background:#eaf1f8;font-size:13px}td small{display:block;color:#687386;font-size:11px;margin-top:3px}.allocation-recommendation{margin:18px 0}.allocation-recommendation h2{margin-top:0}@media(max-width:800px){header{padding:16px;align-items:flex-start;flex-direction:column}main{padding:18px}.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""
