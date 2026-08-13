from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from pfp.reporting.portfolio_report import PortfolioReport


class WorkbookWriter:
    def write(self, report: PortfolioReport, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        workbook = Workbook()
        summary = workbook.active
        summary.title = "Resumen"
        self._write_summary(summary, report)
        self._write_positions(workbook, report)

        workbook.save(output)
        return output

    @staticmethod
    def _write_summary(sheet, report: PortfolioReport) -> None:
        sheet.append(["PFP — Resumen de cartera"])
        sheet["A1"].font = Font(bold=True, size=16)
        sheet.append([])
        rows = [
            ("Patrimonio total", report.total_value),
            ("Efectivo", report.cash),
            ("Capital invertido", report.invested),
            ("Valor de mercado", report.market_value),
            ("P/L realizado", report.realized_gain_loss),
            ("P/L no realizado", report.unrealized_gain_loss),
            ("Renta variable", report.equity_value),
            ("Renta fija", report.fixed_income_value),
            ("Oro", report.gold_value),
            ("Cripto", report.crypto_value),
        ]
        for label, value in rows:
            sheet.append([label, value])
        sheet["A3"].font = Font(bold=True)
        for row in sheet.iter_rows(min_row=4, max_row=sheet.max_row, min_col=2, max_col=2):
            row[0].number_format = '#,##0.00 [$€-es-ES]'
        WorkbookWriter._autosize(sheet)

    @staticmethod
    def _write_positions(workbook: Workbook, report: PortfolioReport) -> None:
        sheet = workbook.create_sheet("Posiciones")
        headers = [
            "Símbolo",
            "Nombre",
            "Clase",
            "Participaciones",
            "Invertido",
            "Precio mercado",
            "Valor mercado",
            "P/L",
        ]
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True)

        for position in report.positions:
            sheet.append([
                position.symbol,
                position.name,
                position.portfolio_class,
                position.shares,
                position.invested,
                position.market_price,
                position.market_value,
                position.gain_loss,
            ])

        for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=5, max_col=8):
            for cell in row:
                cell.number_format = '#,##0.00 [$€-es-ES]'
        for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=4, max_col=4):
            row[0].number_format = '0.########'
        WorkbookWriter._autosize(sheet)

    @staticmethod
    def _autosize(sheet) -> None:
        for column in sheet.columns:
            width = max(len(str(cell.value or "")) for cell in column) + 2
            sheet.column_dimensions[get_column_letter(column[0].column)].width = min(width, 45)
