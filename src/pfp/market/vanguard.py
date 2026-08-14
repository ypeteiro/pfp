from abc import ABC, abstractmethod
from decimal import Decimal
from urllib.request import Request, urlopen
import re


VANGUARD_PRODUCTS = {
    "IE00B03HD191": (
        "https://www.ch.vanguard/"
        "en/private-investor/product/mf/equity/"
        "9837/global-stock-index-fund-eur-acc"
    ),
}


class VanguardPriceProvider(ABC):

    @abstractmethod
    def get_prices(
        self,
        symbols: list[str],
    ) -> dict[str, Decimal]:
        raise NotImplementedError


class VanguardApiPriceProvider(
    VanguardPriceProvider
):

    def get_prices(
        self,
        symbols: list[str],
    ) -> dict[str, Decimal]:

        prices: dict[str, Decimal] = {}

        for symbol in symbols:

            url = VANGUARD_PRODUCTS.get(
                symbol
            )

            if url is None:
                continue

            price = self._get_price(
                url
            )

            if price is not None:
                prices[symbol] = price

        return prices

    def _get_price(
        self,
        url: str,
    ) -> Decimal | None:

        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36"
                ),
                "Accept": "text/html",
            },
        )

        try:

            with urlopen(
                request,
                timeout=10,
            ) as response:

                html = (
                    response
                    .read()
                    .decode(
                        "utf-8",
                        errors="ignore",
                    )
                )

        except Exception:
            return None

        value = self._extract_nav(
            html
        )

        if value is None:
            return None

        try:

            return Decimal(
                value
            ).quantize(
                Decimal("0.01")
            )

        except Exception:
            return None

    @staticmethod
    def _extract_nav(
        html: str,
    ) -> str | None:

        patterns = (
            r"NAV\s+Price\s*\(EUR\)"
            r".{0,500}?"
            r"(?:€|EUR\s*)"
            r"([0-9]+\.[0-9]+)",

            r'"navPrice"\s*:\s*'
            r'"?([0-9]+\.[0-9]+)"?',

            r'"nav"\s*:\s*'
            r'"?([0-9]+\.[0-9]+)"?',
        )

        for pattern in patterns:

            match = re.search(
                pattern,
                html,
                re.IGNORECASE | re.DOTALL,
            )

            if match is not None:
                return match.group(1)

        return None