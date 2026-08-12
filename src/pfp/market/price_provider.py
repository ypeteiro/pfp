from decimal import Decimal

from pfp.market.vanguard import VanguardApiPriceProvider
from pfp.market.yahoo import YahooFinancePriceProvider


class CompositePriceProvider:

    def __init__(self, yahoo_provider=None, vanguard_provider=None):
        self.yahoo_provider = yahoo_provider or YahooFinancePriceProvider()
        self.vanguard_provider = vanguard_provider or VanguardApiPriceProvider()

    def get_prices(self, symbols: list[str]) -> dict[str, Decimal]:
        prices: dict[str, Decimal] = {}

        try:
            prices.update(self.yahoo_provider.get_prices(symbols))
        except Exception:
            pass

        missing_symbols = [symbol for symbol in symbols if symbol not in prices]
        if not missing_symbols:
            return prices

        try:
            prices.update(self.vanguard_provider.get_prices(missing_symbols))
        except Exception:
            pass

        return prices
