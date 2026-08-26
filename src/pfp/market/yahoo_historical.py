from datetime import datetime, timedelta
from decimal import Decimal

import yfinance as yf

from pfp.market.currency import normalize_price
from pfp.market.yahoo import YAHOO_CURRENCY_NORMALIZATION, YAHOO_SYMBOLS
from pfp.reporting.historical_prices import HistoricalPriceProvider


class YahooFinanceHistoricalPriceProvider(HistoricalPriceProvider):
    """Fetch historical closing prices from Yahoo Finance."""

    def __init__(self, currency_rate_provider=None):
        self.currency_rate_provider = currency_rate_provider

    def price(self, symbol: str, at: datetime) -> Decimal | None:
        yahoo_symbol = YAHOO_SYMBOLS.get(symbol)
        if yahoo_symbol is None:
            return None

        try:
            history = yf.Ticker(yahoo_symbol).history(
                start=at.date(),
                end=at.date() + timedelta(days=1),
                auto_adjust=False,
            )
            if history.empty:
                return None

            close = history["Close"].iloc[0]
            currency = yf.Ticker(yahoo_symbol).fast_info.get("currency")
            if close is None or currency is None:
                return None

            normalized_currency = YAHOO_CURRENCY_NORMALIZATION.get(currency, currency)
            price = normalize_price(Decimal(str(close)), currency)
            if normalized_currency != "EUR":
                if self.currency_rate_provider is None:
                    return None
                price *= self.currency_rate_provider.get_rate_at(
                    normalized_currency, "EUR", at
                )
            return price.quantize(Decimal("0.01"))
        except Exception:
            return None
