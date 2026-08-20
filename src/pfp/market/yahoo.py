from decimal import Decimal

import yfinance as yf

from pfp.market.currency import normalize_price
from pfp.market.yahoo_currency_rates import (
    YahooCurrencyRateProvider,
)


YAHOO_SYMBOLS = {
    "BTC": "BTC-EUR",
    "IE00BK5BQT80": "VWCE.DE",
    "IE00B4L5Y983": "EUNL.DE",
    "IE00BG47KH54": "VAGF.DE",
    "IE00BKM4GZ66": "IS3N.DE",
    "IE00B5BMR087": "SXR8.DE",
    "IE00B4ND3602": "SGLN.L",
    "IE000I1Q42S9": "BD27.AS",
    "US55024U1097": "LITE",
    "US1717793095": "CIEN",
    "US12510Q1004": "CCC",
}


YAHOO_CURRENCY_NORMALIZATION = {
    "GBp": "GBP",
}


class YahooFinancePriceProvider:

    def __init__(
        self,
        currency_rate_provider=None,
    ):
        self.currency_rate_provider = (
            currency_rate_provider
            or YahooCurrencyRateProvider()
        )

    def get_prices(
        self,
        symbols: list[str],
    ) -> dict[str, Decimal]:

        prices: dict[str, Decimal] = {}

        for symbol in symbols:
            try:
                yahoo_symbol = YAHOO_SYMBOLS.get(symbol)

                if yahoo_symbol is None:
                    continue

                ticker = yf.Ticker(yahoo_symbol)

                history = ticker.history(
                    period="1d",
                    auto_adjust=False,
                )

                if history.empty:
                    continue

                close = history["Close"].iloc[-1]

                if close is None:
                    continue

                currency = ticker.fast_info.get("currency")

                if currency is None:
                    continue

                normalized_currency = YAHOO_CURRENCY_NORMALIZATION.get(
                    currency,
                    currency,
                )

                price = normalize_price(
                    Decimal(str(close)),
                    currency,
                )

                if normalized_currency != "EUR":
                    exchange_rate = self.currency_rate_provider.get_rate(
                        normalized_currency,
                        "EUR",
                    )
                    price *= exchange_rate

                prices[symbol] = price.quantize(Decimal("0.01"))
            except Exception:
                continue

        return prices
