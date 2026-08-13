from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from pfp.reporting.portfolio_report import PortfolioReport


def export_portfolio_report(report: PortfolioReport, output: Path) -> None:
    workbook = Workbook()
    summary = workbook.active
    summary.title = "Resumen"

    summary.append(["Métrica", "Valor"])
    for cell in summary[1]:
        cell.font = Font(bold=True)

    rows = [
        ("Patrimonio", report.total_value),
        ("Efectivo", report.cash),
        ("Invertido", report.invested),
        ("Valor de mercado", report.market_value),
        ("P/L realizado", report.realized_gain_loss),
        ("P/L no realizado", report.unrealized_gain_loss),
        ("Renta variable", report.equity_value),
        ("Renta fija", report.fixed_income_value),
        ("Oro", report.gold_value),
        ("Crypto", report.crypto_value),
    ]
    for row in rows:
        summary.append(row)

    positions = workbook.create_sheet("Posiciones")
    positions.append([
        "Símbolo", "Nombre", "Clase", "Participaciones", "Invertido",
        "Precio mercado", "Valor mercado", "P/L",
    ])
    for cell in positions[1]:
        cell.font = Font(bold=True)
    for position in report.positions:
        positions.append([
            position.symbol,
            position.name,
            position.portfolio_class,
            position.shares,
            position.invested,
            position.market_price,
            position.market_value,
            position.gain_loss,
        ])

    for sheet in workbook.worksheets:
        sheet.freeze_panes = "A2"
        for column in sheet.columns:
            width = max(len(str(cell.value or "")) for cell in column) + 2
            sheet.column_dimensions[column[0].column_letter].width = min(width, 32)

    output.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output)
