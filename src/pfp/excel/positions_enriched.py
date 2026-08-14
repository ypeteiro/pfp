"""Helpers for the enriched Excel positions view.

The main workbook writer remains unchanged while the remote file is being
iterated.  This module keeps the column contract explicit and testable.
"""

from dataclasses import dataclass
from decimal import Decimal

from pfp.reporting.portfolio_report import PositionReport


@dataclass(frozen=True, slots=True)
class ExcelPosition:
    isin: str | None
    ticker: str | None
    name: str
    portfolio_class: str | None
    shares: Decimal
    invested: Decimal
    average_price: Decimal
    market_price: Decimal | None
    market_value: Decimal | None
    weight: Decimal | None
    gain_loss: Decimal | None
    gain_loss_pct: Decimal | None


def to_excel_position(position: PositionReport) -> ExcelPosition:
    gain_loss_pct = (
        position.gain_loss / position.invested
        if position.gain_loss is not None and position.invested
        else None
    )
    return ExcelPosition(
        isin=position.isin,
        ticker=position.ticker,
        name=position.name,
        portfolio_class=position.portfolio_class,
        shares=position.shares,
        invested=position.invested,
        average_price=position.average_price,
        market_price=position.market_price,
        market_value=position.market_value,
        weight=position.weight,
        gain_loss=position.gain_loss,
        gain_loss_pct=gain_loss_pct,
    )


POSITION_HEADERS = (
    "ISIN",
    "Ticker",
    "Nombre",
    "Clase",
    "Participaciones",
    "Invertido",
    "Precio medio",
    "Precio mercado",
    "Valor mercado",
    "Peso",
    "P/L",
    "P/L %",
)
