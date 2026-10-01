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


def test_lookup_yahoo_asset_returns_none_when_search_fails(monkeypatch):
    class FailingSearch:
        def __init__(self, query, max_results):
            raise RuntimeError("Yahoo unavailable")

    monkeypatch.setattr(yahoo.yf, "Search", FailingSearch)

    assert yahoo.lookup_yahoo_asset("US0605051046") is None
