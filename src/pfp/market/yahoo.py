from decimal import Decimal
import re

import yfinance as yf

from pfp.domain.asset_catalog import AssetCatalog
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
    "US92840M1027": "VST",
    "US67066G1040": "NVDA",
    "US0605051046": "BAC",
}


def resolve_yahoo_symbol(symbol: str) -> str | None:
    """Resolve a PFP symbol to a Yahoo Finance symbol."""
    yahoo_symbol = YAHOO_SYMBOLS.get(symbol)
    if yahoo_symbol is not None:
        return yahoo_symbol

    asset = AssetCatalog.get(symbol)
    if asset is not None:
        if asset.ticker:
            return asset.ticker
        if asset.isin:
            return asset.isin

    return None


def lookup_yahoo_asset(query: str) -> dict[str, str] | None:
    """Look up an instrument in Yahoo Finance and return its basic identity."""
    query = query.strip()
    if not query:
        return None

    try:
        search = yf.Search(query, max_results=10)
        quotes = getattr(search, "quotes", ()) or ()
        if not quotes:
            return None

        exact = next(
            (
                quote
                for quote in quotes
                if str(quote.get("symbol", "")).upper() == query.upper()
                or str(quote.get("isin", "")).upper() == query.upper()
            ),
            None,
        )

        # Yahoo Search may return internal Morningstar fund identifiers such
        # as $0P00000WLG.F for an ISIN. Never treat an unrelated search
        # result as the instrument the user asked for.
        is_isin = bool(re.fullmatch(r"[A-Za-z]{2}[A-Za-z0-9]{9}[0-9]", query))
        if is_isin:
            if exact is None:
                return None
            quote = exact
        else:
            quote = exact or quotes[0]
        ticker = str(quote.get("symbol", "")).strip()
        if not ticker:
            return None

        name = str(
            quote.get("longname")
            or quote.get("shortname")
            or ""
        ).strip()

        return {"ticker": ticker, "name": name}
    except Exception:
        return None


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
                yahoo_symbol = resolve_yahoo_symbol(symbol)
                if not yahoo_symbol:
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
