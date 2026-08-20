import pytest

from pfp.domain.account_catalog import AccountCatalog


def test_default_account_definitions_have_stable_identity():
    accounts = AccountCatalog.defaults()

    assert {account.account_id for account in accounts} == {
        AccountCatalog.TRADE_REPUBLIC,
        AccountCatalog.ABANCA_AHORRO,
    }
    assert len({account.account_id for account in accounts}) == len(accounts)


def test_account_catalog_resolves_known_accounts():
    for account in AccountCatalog.defaults():
        assert AccountCatalog.get(account.account_id) is account
        assert AccountCatalog.contains(account.account_id)


def test_account_catalog_rejects_unknown_account():
    assert not AccountCatalog.contains("UNKNOWN")
    with pytest.raises(ValueError, match="Unknown account"):
        AccountCatalog.get("UNKNOWN")
