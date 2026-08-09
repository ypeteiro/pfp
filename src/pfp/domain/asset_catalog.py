from pfp.domain.asset import Asset


class AssetCatalog:

    _assets = {
        "BTC": Asset(
            symbol="BTC",
            name="Bitcoin",
            portfolio_class="CRYPTO",
        ),
        "IE00BKM4GZ66": Asset(
            symbol="IE00BKM4GZ66",
            name="Asset IE00BKM4GZ66",
            portfolio_class="EQUITY",
        ),
        "IE00B03HD191": Asset(
            symbol="IE00B03HD191",
            name="Asset IE00B03HD191",
            portfolio_class="EQUITY",
        ),
        "IE00B4L5Y983": Asset(
            symbol="IE00B4L5Y983",
            name="iShares Core MSCI World UCITS ETF",
            portfolio_class="EQUITY",
        ),
        "IE00B5BMR087": Asset(
            symbol="IE00B5BMR087",
            name="Asset IE00B5BMR087",
            portfolio_class="EQUITY",
        ),
        "IE000I1Q42S9": Asset(
            symbol="IE000I1Q42S9",
            name="Asset IE000I1Q42S9",
            portfolio_class="FIXED_INCOME",
        ),
        "IE00BK5BQT80": Asset(
            symbol="IE00BK5BQT80",
            name="Asset IE00BK5BQT80",
            portfolio_class="EQUITY",
        ),
        "IE00BG47KH54": Asset(
            symbol="IE00BG47KH54",
            name="Vanguard Global Aggregate Bond UCITS ETF",
            portfolio_class="FIXED_INCOME",
        ),
        "IE00B4ND3602": Asset(
            symbol="IE00B4ND3602",
            name="Gold",
            portfolio_class="GOLD",
        ),
    }

    @classmethod
    def get(cls, symbol: str) -> Asset | None:
        return cls._assets.get(symbol)

    @classmethod
    def get_or_create(
        cls,
        symbol: str,
        name: str | None = None,
    ) -> Asset:

        asset = cls.get(symbol)

        if asset is not None:
            return asset

        return Asset(
            symbol=symbol,
            name=name or symbol,
            portfolio_class="UNKNOWN",
        )