from pfp.domain.asset import Asset


class AssetCatalog:

    _assets = {
        "BTC": Asset(
            symbol="BTC",
            name="Bitcoin",
            portfolio_class="CRYPTO",
            ticker="BTC",
        ),
        "IE00BKM4GZ66": Asset(
            symbol="IE00BKM4GZ66",
            name="iShares Core MSCI Emerging Markets IMI UCITS ETF",
            portfolio_class="EQUITY",
            isin="IE00BKM4GZ66",
            ticker="EIMI",
        ),
        "IE00B03HD191": Asset(
            symbol="IE00B03HD191",
            name="Vanguard Global Stock Index Fund EUR Acc",
            portfolio_class="EQUITY",
            isin="IE00B03HD191",
        ),
        "IE00B4L5Y983": Asset(
            symbol="IE00B4L5Y983",
            name="iShares Core MSCI World UCITS ETF USD (Acc)",
            portfolio_class="EQUITY",
            isin="IE00B4L5Y983",
            ticker="EUNL",
        ),
        "IE00B5BMR087": Asset(
            symbol="IE00B5BMR087",
            name="iShares Core S&P 500 UCITS ETF USD (Acc)",
            portfolio_class="EQUITY",
            isin="IE00B5BMR087",
            ticker="SXR8",
        ),
        "IE000I1Q42S9": Asset(
            symbol="IE000I1Q42S9",
            name="Fixed Income 2027",
            portfolio_class="FIXED_INCOME",
            isin="IE000I1Q42S9",
        ),
        "IE00BK5BQT80": Asset(
            symbol="IE00BK5BQT80",
            name="Vanguard FTSE All-World UCITS ETF USD (Acc)",
            portfolio_class="EQUITY",
            isin="IE00BK5BQT80",
            ticker="VWCE",
        ),
        "IE00BG47KH54": Asset(
            symbol="IE00BG47KH54",
            name="Vanguard Global Aggregate Bond UCITS ETF EUR Hedged Acc",
            portfolio_class="FIXED_INCOME",
            isin="IE00BG47KH54",
            ticker="VAGF",
        ),
        "IE00B4ND3602": Asset(
            symbol="IE00B4ND3602",
            name="Gold",
            portfolio_class="GOLD",
            isin="IE00B4ND3602",
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
            isin=symbol if symbol.upper().startswith("IE") else None,
        )
