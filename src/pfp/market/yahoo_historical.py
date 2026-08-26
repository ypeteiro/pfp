from datetime import date, datetime, timedelta
from decimal import Decimal

import yfinance as yf

from pfp.market.currency import normalize_price
from pfp.market.yahoo import YAHOO_CURRENCY_NORMALIZATION, YAHOO_SYMBOLS
from pfp.market.yahoo_currency_rates import YahooCurrencyRateProvider
from pfp.reporting.historical_prices import HistoricalPriceProvider


class YahooFinanceHistoricalPriceProvider(HistoricalPriceProvider):
    """Fetch historical closing prices from Yahoo Finance."""

    def __init__(self, currency_rate_provider=None):
        self.currency_rate_provider = currency_rate_provider or YahooCurrencyRateProvider()

    @staticmethod
    def _last_close_on_or_before(history, target: date):
        if history.empty:
            return None

        for index, row in reversed(list(history.iterrows())):
            index_date = index.date() if hasattr(index, "date") else index
            if index_date <= target:
                return row["Close"]
        return None

    def price(self, symbol: str, at: datetime) -> Decimal | None:
        yahoo_symbol = YAHOO_SYMBOLS.get(symbol)
        if yahoo_symbol is None:
            return None

        ticker = yf.Ticker(yahoo_symbol)
        history = ticker.history(
            start=at.date() - timedelta(days=4),
            end=at.date() + timedelta(days=1),
            auto_adjust=False,
        )
        close = self._last_close_on_or_before(history, at.date())
        if close is None:
            return None

        currency = ticker.fast_info.get("currency")
        if currency is None:
            return None

        normalized_currency = YAHOO_CURRENCY_NORMALIZATION.get(currency, currency)
        price = normalize_price(Decimal(str(close)), currency)
        if normalized_currency != "EUR":
            price *= self.currency_rate_provider.get_rate_at(
                normalized_currency, "EUR", at.date()
            )
        return price.quantize(Decimal("0.01"))
