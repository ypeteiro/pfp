from datetime import date, timedelta
from decimal import Decimal

import yfinance as yf

from pfp.market.currency_rates import CurrencyRateProvider


YAHOO_CURRENCY_SYMBOLS = {
    ("GBP", "EUR"): "GBPEUR=X",
    ("USD", "EUR"): "USDEUR=X",
}


class YahooCurrencyRateProvider(CurrencyRateProvider):

    def _yahoo_symbol(self, from_currency: str, to_currency: str) -> str:
        if from_currency == to_currency:
            return ""

        yahoo_symbol = YAHOO_CURRENCY_SYMBOLS.get(
            (from_currency, to_currency)
        )

        if yahoo_symbol is None:
            raise ValueError(
                f"Unsupported currency pair: "
                f"{from_currency}/{to_currency}"
            )

        return yahoo_symbol

    @staticmethod
    def _last_close_on_or_before(history, target: date):
        if history.empty:
            return None

        for index, row in reversed(list(history.iterrows())):
            index_date = index.date() if hasattr(index, "date") else index
            if index_date <= target:
                return row["Close"]
        return None

    @staticmethod
    def _as_decimal(close) -> Decimal:
        if close is None:
            raise ValueError("No currency rate available")
        return Decimal(str(close)).quantize(Decimal("0.000001"))

    def get_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:

        if from_currency == to_currency:
            return Decimal("1")

        yahoo_symbol = self._yahoo_symbol(from_currency, to_currency)
        ticker = yf.Ticker(yahoo_symbol)
        history = ticker.history(
            period="1d",
            auto_adjust=False,
        )

        close = history["Close"].iloc[-1] if not history.empty else None
        if close is None:
            raise ValueError(
                f"No currency rate available for "
                f"{from_currency}/{to_currency}"
            )

        return self._as_decimal(close)

    def get_rate_at(
        self,
        from_currency: str,
        to_currency: str,
        at: date,
    ) -> Decimal:
        """Return the latest available FX close on or before ``at``."""

        if from_currency == to_currency:
            return Decimal("1")

        yahoo_symbol = self._yahoo_symbol(from_currency, to_currency)
        ticker = yf.Ticker(yahoo_symbol)
        history = ticker.history(
            start=at - timedelta(days=4),
            end=at + timedelta(days=1),
            auto_adjust=False,
        )
        close = self._last_close_on_or_before(history, at)
        if close is None:
            raise ValueError(
                f"No currency rate available for "
                f"{from_currency}/{to_currency} on or before {at}"
            )

        return self._as_decimal(close)
