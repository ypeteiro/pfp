"""HTTP application routing for the PFP web UI."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from html import escape
from pathlib import Path

from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.dashboard import build_dashboard
from pfp.web.navigation import navigation_html


@dataclass(frozen=True, slots=True)
class WebApp:
    report: PortfolioReport

    def render(self, path: str) -> str:
        pages = {
            "/": self._dashboard,
            "/index.html": self._dashboard,
            "/positions": self._positions,
            "/movements": self._movements,
            "/allocation": self._allocation,
        }
        renderer = pages.get(path)
        if renderer is None:
            raise KeyError(path)
        return self._layout(renderer(), path)

    def _layout(self, content: str, path: str) -> str:
        return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PFP</title><style>{CSS}</style></head>
<body><header><div><strong>PFP</strong><span>Personal Finance Portfolio</span></div>{navigation_html(path)}</header>
<main>{content}</main></body></html>"""

    def _dashboard(self) -> str:
        model = build_dashboard(self.report)
        cards = "".join(f'<article class="card"><small>{escape(c.label)}</small><strong>{euro(c.value)}</strong></article>' for c in model.cards)
        allocation = "".join(f'<tr><td>{escape(a.asset_class)}</td><td>{euro(a.value)}</td><td>{pct(a.weight)}</td></tr>' for a in model.allocation)
        return f'<h1>Dashboard</h1><section class="grid">{cards}</section><section class="panel"><h2>Asignación actual</h2><table><tr><th>Clase</th><th>Valor</th><th>Peso</th></tr>{allocation}</table></section>'

    def _positions(self) -> str:
        rows = "".join(
            f'<tr><td>{escape(p.isin or "—")}</td><td>{escape(p.ticker or "—")}</td><td>{escape(p.name)}</td><td>{escape(p.portfolio_class or "—")}</td><td>{p.shares}</td><td>{euro(p.market_value)}</td><td>{euro(p.gain_loss)}</td></tr>'
            for p in self.report.positions
        )
        return f'<h1>Posiciones</h1><section class="panel"><table><tr><th>ISIN</th><th>Ticker</th><th>Nombre</th><th>Clase</th><th>Participaciones</th><th>Valor</th><th>P/L</th></tr>{rows}</table></section>'

    def _movements(self) -> str:
        rows = "".join(
            f'<tr><td>{escape(str(m.datetime))}</td><td>{escape(m.type or "—")}</td><td>{escape(m.symbol or "—")}</td><td>{euro(m.amount)}</td></tr>'
            for m in self.report.movements
        )
        return f'<h1>Movimientos</h1><section class="panel"><table><tr><th>Fecha</th><th>Tipo</th><th>Símbolo</th><th>Importe</th></tr>{rows}</table></section>'

    def _allocation(self) -> str:
        values = {"RV": self.report.equity_value, "RF": self.report.fixed_income_value, "Oro": self.report.gold_value, "Cripto": self.report.crypto_value}
        targets = {"RV": Decimal("0.75"), "RF": Decimal("0.20"), "Oro": Decimal("0.05"), "Cripto": Decimal("0")}
        total = self.report.market_value
        rows = []
        for asset_class, target in targets.items():
            value = values[asset_class]
            weight = value / total if total else Decimal("0")
            deviation = weight - target
            action = "Aumentar" if deviation < Decimal("-0.02") else "Reducir" if deviation > Decimal("0.02") else "Mantener"
            rows.append(f'<tr><td>{asset_class}</td><td>{pct(target)}</td><td>{pct(weight)}</td><td>{pct(deviation)}</td><td>{action}</td></tr>')
        return '<h1>Asignación</h1><section class="panel"><table><tr><th>Clase</th><th>Objetivo</th><th>Actual</th><th>Desviación</th><th>Acción</th></tr>' + ''.join(rows) + '</table></section>'


CSS = """
:root{font-family:Inter,Segoe UI,sans-serif;color:#172033;background:#f5f7fb}body{margin:0}header{background:#172033;color:white;padding:18px 32px;display:flex;justify-content:space-between;align-items:center;gap:24px}header strong{font-size:22px}header span{margin-left:12px;color:#aeb8c8;font-size:13px}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{color:#cbd5e1;text-decoration:none;padding:8px 12px;border-radius:8px}nav a.active,nav a:hover{background:#334155;color:white}main{max-width:1180px;margin:0 auto;padding:32px}h1{margin-top:0}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.card,.panel{background:white;border:1px solid #e3e8f0;border-radius:14px;padding:20px;box-shadow:0 2px 8px #17203310}.card small{display:block;color:#687386}.card strong{display:block;font-size:26px;margin-top:8px}table{width:100%;border-collapse:collapse}th,td{padding:11px 12px;border-bottom:1px solid #edf0f5;text-align:left}th{background:#eaf1f8;font-size:13px}@media(max-width:800px){header{padding:16px;align-items:flex-start;flex-direction:column}main{padding:18px}.grid{grid-template-columns:1fr 1fr}}@media(max-width:520px){.grid{grid-template-columns:1fr}table{font-size:13px}}
"""


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%".replace(".", ",")
