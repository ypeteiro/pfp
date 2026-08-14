from abc import ABC, abstractmethod
from decimal import Decimal


class CurrencyRateProvider(ABC):

    @abstractmethod
    def get_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:
        raise NotImplementedError