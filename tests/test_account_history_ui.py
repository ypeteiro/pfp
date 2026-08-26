from datetime import datetime
from decimal import Decimal

from pfp.domain.account import Account
from pfp.domain.account_transfer import AccountTransfer
from pfp.domain.external_cash_movement import ExternalCashMovement
from pfp.web.account_history_ui import account_history_html


def test_account_history_shows_external_movements_and_transfers_from_account_perspective():
    accounts = [
        Account("ABANCA", "ABANCA", account_id="abanca", balance=Decimal("700")),
        Account("Trade Republic", "Trade Republic", account_id="trade_republic", balance=Decimal("500")),
    ]
    external_movements = [
        ExternalCashMovement(datetime(2026, 8, 20, 10, 0), "abanca", Decimal("1000"), description="Aportación inicial"),
    ]
    transfers = [
        AccountTransfer(datetime(2026, 8, 21, 10, 0), "abanca", "trade_republic", Decimal("300"), "EUR"),
    ]

    html = account_history_html(accounts, external_movements, transfers)

    assert "Aportación inicial" in html
    assert "Movimiento externo" in html
    assert "Traspaso enviado" in html
    assert "Traspaso recibido" in html
    assert "-300,00 €" in html
    assert "+300,00 €" in html


def test_account_history_shows_empty_state_for_account_without_movements():
    accounts = [Account("ABANCA", "ABANCA", account_id="abanca", balance=Decimal("1000"))]
    unrelated_movement = ExternalCashMovement(datetime(2026, 8, 20, 10, 0), "other", Decimal("100"))
    unrelated_transfer = AccountTransfer(datetime(2026, 8, 21, 10, 0), "other", "another", Decimal("50"), "EUR")

    html = account_history_html(accounts, [unrelated_movement], [unrelated_transfer])

    assert "No hay movimientos registrados." in html
