from decimal import Decimal
from types import SimpleNamespace

from pfp.web import rebalance_ui


def test_rebalance_ui_explains_rebalanceable_value_semantics(monkeypatch):
    result = SimpleNamespace(
        rebalanceable_value=Decimal("19000"),
        total_value=Decimal("19500"),
        orders=(),
    )
    monkeypatch.setattr(
        rebalance_ui,
        "RebalanceEngine",
        lambda: SimpleNamespace(rebalance=lambda portfolio, account_id: result),
    )

    account = SimpleNamespace(id="broker-1", name="Broker", broker="Test Broker")
    portfolio = SimpleNamespace(accounts=[account])

    html = rebalance_ui.rebalance_html(portfolio)

    assert "Valor rebalanceable" in html
    assert "Valor total cartera" in html
    assert "19.000,00 €" in html
    assert "19.500,00 €" in html
    assert "Las ponderaciones objetivo y las órdenes propuestas se calculan sobre el <strong>valor rebalanceable</strong>" in html
    assert "activos fuera de las clases objetivo quedan fuera del rebalanceo" in html
    assert "Efectivo y posiciones de la cuenta seleccionada" in html
    assert "incluidos los activos que no forman parte de las clases objetivo" in html


def test_rebalance_ui_keeps_selected_account_context(monkeypatch):
    result = SimpleNamespace(
        rebalanceable_value=Decimal("1000"),
        total_value=Decimal("1000"),
        orders=(),
    )
    calls = []

    def rebalance(portfolio, account_id):
        calls.append(account_id)
        return result

    monkeypatch.setattr(
        rebalance_ui,
        "RebalanceEngine",
        lambda: SimpleNamespace(rebalance=rebalance),
    )

    accounts = [
        SimpleNamespace(id="one", name="One", broker="Broker A"),
        SimpleNamespace(id="two", name="Two", broker="Broker B"),
    ]
    portfolio = SimpleNamespace(accounts=accounts)

    html = rebalance_ui.rebalance_html(portfolio, account_id="two")

    assert calls == ["two"]
    assert 'value="two" selected' in html
    assert "two" in html
