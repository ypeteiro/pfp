from decimal import Decimal

from pfp.market.vanguard import (
    VanguardApiPriceProvider,
)
from pfp.market.yahoo import (
    YahooFinancePriceProvider,
)


class CompositePriceProvider:

    def __init__(
        self,
        yahoo_provider=None,
        vanguard_provider=None,
    ):
        self.yahoo_provider = (
            yahoo_provider
            or YahooFinancePriceProvider()
        )

        self.vanguard_provider = (
            vanguard_provider
            or VanguardApiPriceProvider()
        )

    def get_prices(
        self,
        symbols: list[str],
    ) -> dict[str, Decimal]:

        prices = self.yahoo_provider.get_prices(
            symbols
        )

        missing_symbols = [
            symbol
            for symbol in symbols
            if symbol not in prices
        ]

        if not missing_symbols:
            return prices

        vanguard_prices = (
            self.vanguard_provider.get_prices(
                missing_symbols
            )
        )

        prices.update(
            vanguard_prices
        )

        return prices