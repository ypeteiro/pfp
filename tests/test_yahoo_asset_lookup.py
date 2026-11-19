from pfp.market import yahoo


def test_lookup_yahoo_asset_returns_ticker_and_name_from_search(monkeypatch):
    class FakeSearch:
        def __init__(self, query, max_results):
            assert query == "US0605051046"
            assert max_results == 10
            self.quotes = [
                {
                    "symbol": "BAC",
                    "shortname": "Bank of America",
                }
            ]

    monkeypatch.setattr(yahoo.yf, "Search", FakeSearch)

    assert yahoo.lookup_yahoo_asset("US0605051046") == {
        "ticker": "BAC",
        "name": "Bank of America",
    }


def test_lookup_yahoo_asset_removes_yahoo_dollar_prefix(monkeypatch):
    class FakeSearch:
        def __init__(self, query, max_results):
            self.quotes = [
                {
                    "symbol": "$1GOOGL.MI",
                    "isin": "US02079K3059",
                    "shortname": "Alphabet Inc.",
                }
            ]

    monkeypatch.setattr(yahoo.yf, "Search", FakeSearch)

    assert yahoo.lookup_yahoo_asset("US02079K3059") == {
        "ticker": "1GOOGL.MI",
        "name": "Alphabet Inc.",
    }


def test_lookup_yahoo_asset_rejects_prefixed_morningstar_identifier(monkeypatch):
    class FakeSearch:
        def __init__(self, query, max_results):
            self.quotes = [
                {
                    "symbol": "$0P00000WLG.F",
                    "shortname": "Example fund",
                }
            ]

    monkeypatch.setattr(yahoo.yf, "Search", FakeSearch)

    assert yahoo.lookup_yahoo_asset("IE0000000000") is None


def test_lookup_yahoo_asset_returns_none_when_search_fails(monkeypatch):
    class FailingSearch:
        def __init__(self, query, max_results):
            raise RuntimeError("Yahoo unavailable")

    monkeypatch.setattr(yahoo.yf, "Search", FailingSearch)

    assert yahoo.lookup_yahoo_asset("US0605051046") is None
