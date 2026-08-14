"""Minimal dependency-free web dashboard for PFP.

Run with:
    python -m pfp.web.server data/imports/trade_republic.csv
"""

from __future__ import annotations

import argparse
from decimal import Decimal
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pfp.cli import load_portfolio
from pfp.reporting.portfolio_report import PortfolioReport
from pfp.web.dashboard import build_dashboard


CSS = """
:root { font-family: Inter, Segoe UI, sans-serif; color: #172033; background: #f5f7fb; }
body { margin: 0; }
main { max-width: 1180px; margin: 0 auto; padding: 32px; }
h1 { margin: 0 0 6px; } .muted { color: #687386; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 24px 0; }
.card { background: white; border: 1px solid #e3e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 2px 8px #17203310; }
.card .label { color: #687386; font-size: 13px; } .card .value { font-size: 28px; font-weight: 700; margin-top: 8px; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; }
th, td { padding: 12px 14px; border-bottom: 1px solid #edf0f5; text-align: left; }
th { background: #eaf1f8; font-size: 13px; } .positive { color: #16734a; } .negative { color: #b42318; }
@media (max-width: 800px) { main { padding: 18px; } .grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 520px) { .grid { grid-template-columns: 1fr; } }
"""


def euro(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%".replace(".", ",")


def dashboard_html(report: PortfolioReport) -> str:
    model = build_dashboard(report)
    cards = "".join(
        f'<article class="card"><div class="label">{escape(card.label)}</div><div class="value">{euro(card.value)}</div></article>'
        for card in model.cards
    )
    allocation_rows = "".join(
        f"<tr><td>{escape(row.asset_class)}</td><td>{euro(row.value)}</td><td>{pct(row.weight)}</td></tr>"
        for row in model.allocation
    )
    position_rows = "".join(
        f"<tr><td>{escape(p.ticker or '—')}</td><td>{escape(p.name)}</td><td>{escape(p.portfolio_class or '—')}</td>"
        f"<td>{p.shares}</td><td>{euro(p.market_value)}</td><td class=\"{'negative' if (p.gain_loss or 0) < 0 else 'positive'}\">{euro(p.gain_loss)}</td></tr>"
        for p in report.positions
    )
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PFP Dashboard</title><style>{CSS}</style></head>
<body><main><h1>PFP</h1><div class="muted">Personal Finance Portfolio · Dashboard</div>
<section class="grid">{cards}</section>
<section class="card"><h2>Asignación</h2><table><thead><tr><th>Clase</th><th>Valor</th><th>Peso</th></tr></thead><tbody>{allocation_rows}</tbody></table></section>
<section class="card" style="margin-top:16px"><h2>Posiciones</h2><table><thead><tr><th>Ticker</th><th>Nombre</th><th>Clase</th><th>Participaciones</th><th>Valor</th><th>P/L</th></tr></thead><tbody>{position_rows}</tbody></table></section>
</main></body></html>"""


def serve(movements_file: Path, host: str = "127.0.0.1", port: int = 8000) -> None:
    portfolio = load_portfolio(movements_file)
    report = PortfolioReport.from_portfolio(portfolio)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path not in ("/", "/index.html"):
                self.send_error(404)
                return
            body = dashboard_html(report).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"PFP Dashboard: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PFP web dashboard")
    parser.add_argument("movements_file")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(Path(args.movements_file), args.host, args.port)


if __name__ == "__main__":
    main()
