from datetime import date, datetime, timedelta
from decimal import Decimal

import yfinance as yf

from pfp.domain.asset_catalog import AssetCatalog
from pfp.market.currency import normalize_price
from pfp.market.yahoo import YAHOO_CURRENCY_NORMALIZATION, YAHOO_SYMBOLS, resolve_yahoo_symbol
from pfp.market.yahoo_currency_rates import YahooCurrencyRateProvider
from pfp.reporting.historical_prices import HistoricalPriceProvider


class YahooFinanceHistoricalPriceProvider(HistoricalPriceProvider):
    """Fetch historical closing prices from Yahoo Finance."""

    def __init__(self, currency_rate_provider=None):
        self.currency_rate_provider = currency_rate_provider or YahooCurrencyRateProvider()
        self._history_cache = {}
        self._ticker_cache = {}

    @staticmethod
    def _last_close_on_or_before(history, target: date):
        if history.empty:
            return None
        for index, row in reversed(list(history.iterrows())):
            index_date = index.date() if hasattr(index, "date") else index
            if index_date > target:
                continue
            try:
                close = Decimal(str(row["Close"]))
            except Exception:
                continue
            if close.is_finite():
                return close
        return None

    @staticmethod
    def _historical_symbol(symbol: str) -> str | None:
        if symbol in YAHOO_SYMBOLS:
            return YAHOO_SYMBOLS[symbol]
        asset = AssetCatalog.get(symbol)
        if asset is not None and asset.isin:
            return asset.isin
        return resolve_yahoo_symbol(symbol)

    @staticmethod
    def _currency(ticker):
        try:
            return ticker.fast_info.get("currency")
        except Exception:
            return None

    def prefetch(self, symbols, dates) -> None:
        requested_dates = [at.date() if isinstance(at, datetime) else at for at in dates]
        if not requested_dates:
            return
        start = min(requested_dates) - timedelta(days=30)
        end = max(requested_dates) + timedelta(days=1)
        currencies = set()
        for symbol in set(symbols):
            yahoo_symbol = self._historical_symbol(symbol)
            if yahoo_symbol is None or yahoo_symbol in self._history_cache:
                continue
            try:
                ticker = yf.Ticker(yahoo_symbol)
                history = ticker.history(start=start, end=end, auto_adjust=False)
                self._history_cache[yahoo_symbol] = history
                self._ticker_cache[yahoo_symbol] = ticker
                currency = self._currency(ticker)
                if currency:
                    currencies.add(YAHOO_CURRENCY_NORMALIZATION.get(currency, currency))
            except Exception:
                self._history_cache[yahoo_symbol] = None
        rate_prefetch = getattr(self.currency_rate_provider, "prefetch", None)
        if rate_prefetch is not None:
            for currency in currencies:
                if currency != "EUR":
                    rate_prefetch(currency, "EUR", requested_dates)

    def price(self, symbol: str, at: datetime) -> Decimal | None:
        yahoo_symbol = self._historical_symbol(symbol)
        if yahoo_symbol is None:
            return None
        ticker = self._ticker_cache.get(yahoo_symbol)
        history = self._history_cache.get(yahoo_symbol)
        if history is None:
            try:
                ticker = yf.Ticker(yahoo_symbol)
                history = ticker.history(
                    start=at.date() - timedelta(days=30),
                    end=at.date() + timedelta(days=1),
                    auto_adjust=False,
                )
                self._history_cache[yahoo_symbol] = history
                self._ticker_cache[yahoo_symbol] = ticker
            except Exception:
                return None
        close = self._last_close_on_or_before(history, at.date())
        if close is None or ticker is None:
            return None
        currency = self._currency(ticker)
        if currency is None:
            return None
        normalized_currency = YAHOO_CURRENCY_NORMALIZATION.get(currency, currency)
        price = normalize_price(close, currency)
        if normalized_currency != "EUR":
            try:
                price *= self.currency_rate_provider.get_rate_at(normalized_currency, "EUR", at.date())
            except Exception:
                return None
        return price.quantize(Decimal("0.01"))
