from decimal import Decimal

import yfinance as yf

from pfp.market.currency_rates import CurrencyRateProvider


YAHOO_CURRENCY_SYMBOLS = {
    ("GBP", "EUR"): "GBPEUR=X",
    ("USD", "EUR"): "USDEUR=X",
}


class YahooCurrencyRateProvider(CurrencyRateProvider):

    def get_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:

        if from_currency == to_currency:
            return Decimal("1")

        yahoo_symbol = YAHOO_CURRENCY_SYMBOLS.get(
            (from_currency, to_currency)
        )

        if yahoo_symbol is None:
            raise ValueError(
                f"Unsupported currency pair: "
                f"{from_currency}/{to_currency}"
            )

        ticker = yf.Ticker(yahoo_symbol)

        history = ticker.history(
            period="1d",
            auto_adjust=False,
        )

        if history.empty:
            raise ValueError(
                f"No currency rate available for "
                f"{from_currency}/{to_currency}"
            )

        close = history["Close"].iloc[-1]

        if close is None:
            raise ValueError(
                f"No currency rate available for "
                f"{from_currency}/{to_currency}"
            )

        return Decimal(
            str(close)
        ).quantize(
            Decimal("0.000001")
        )
