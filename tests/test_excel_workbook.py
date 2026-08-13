from decimal import Decimal

from openpyxl import load_workbook

from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.excel.workbook import WorkbookWriter
from pfp.reporting.portfolio_report import PortfolioReport


def _report():
    portfolio = Portfolio(cash=Decimal("1000"))
    portfolio.positions["EUNL"] = Position(
        symbol="EUNL",
        name="MSCI World",
        portfolio_class="RV",
        shares=Decimal("2"),
        invested=Decimal("200"),
        market_price=Decimal("120"),
    )
    return PortfolioReport.from_portfolio(portfolio)


def test_workbook_writer_creates_summary_and_positions(tmp_path):
    output = tmp_path / "portfolio.xlsx"
    WorkbookWriter().write(_report(), output)
    workbook = load_workbook(output, data_only=False)
    assert workbook.sheetnames == ["Resumen", "Posiciones"]
    assert workbook["Resumen"]["A4"].value == "Patrimonio total"
    assert workbook["Resumen"]["B4"].value == Decimal("1240")
    assert workbook["Posiciones"]["A2"].value == "EUNL"
    assert workbook["Posiciones"]["D2"].value == Decimal("2")


def test_workbook_writer_creates_parent_directory(tmp_path):
    output = tmp_path / "exports" / "portfolio.xlsx"
    result = WorkbookWriter().write(_report(), output)
    assert result == output
    assert output.exists()
