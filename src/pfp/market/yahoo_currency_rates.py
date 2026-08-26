from datetime import date, timedelta
from decimal import Decimal

import yfinance as yf

from pfp.market.currency_rates import CurrencyRateProvider


YAHOO_CURRENCY_SYMBOLS = {
    ("GBP", "EUR"): "GBPEUR=X",
    ("USD", "EUR"): "USDEUR=X",
}


class YahooCurrencyRateProvider(CurrencyRateProvider):

    def _symbol(self, from_currency: str, to_currency: str) -> str:
        if from_currency == to_currency:
            return ""
        yahoo_symbol = YAHOO_CURRENCY_SYMBOLS.get((from_currency, to_currency))
        if yahoo_symbol is None:
            raise ValueError(
                f"Unsupported currency pair: {from_currency}/{to_currency}"
            )
        return yahoo_symbol

    def get_rate(self, from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return Decimal("1")

        ticker = yf.Ticker(self._symbol(from_currency, to_currency))
        history = ticker.history(period="1d", auto_adjust=False)
        if history.empty:
            raise ValueError(
                f"No currency rate available for {from_currency}/{to_currency}"
            )
        close = history["Close"].iloc[-1]
        if close is None:
            raise ValueError(
                f"No currency rate available for {from_currency}/{to_currency}"
            )
        return Decimal(str(close)).quantize(Decimal("0.000001"))

    def get_rate_at(
        self,
        from_currency: str,
        to_currency: str,
        at: date,
    ) -> Decimal:
        if from_currency == to_currency:
            return Decimal("1")

        ticker = yf.Ticker(self._symbol(from_currency, to_currency))
        history = ticker.history(
            start=at,
            end=at + timedelta(days=1),
            auto_adjust=False,
        )
        if history.empty:
            raise ValueError(
                f"No currency rate available for {from_currency}/{to_currency} at {at}"
            )
        close = history["Close"].iloc[-1]
        if close is None:
            raise ValueError(
                f"No currency rate available for {from_currency}/{to_currency} at {at}"
            )
        return Decimal(str(close)).quantize(Decimal("0.000001"))
