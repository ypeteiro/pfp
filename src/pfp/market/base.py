from abc import ABC, abstractmethod
from decimal import Decimal


class MarketPriceProvider(ABC):

    @abstractmethod
    def get_prices(
        self,
        symbols: list[str],
    ) -> dict[str, Decimal]:
        raise NotImplementedError