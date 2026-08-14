from datetime import datetime
from decimal import Decimal

from pfp.domain.capital_flow import CapitalFlow, FlowType
from pfp.reporting.patrimony_evolution import PatrimonyEvolution
from pfp.web.patrimony_ui import patrimony_evolution_html


def test_patrimony_evolution_view_shows_history_and_summary():
    evolution = PatrimonyEvolution.from_capital_flows((
        CapitalFlow(datetime(2026, 1, 1), Decimal("1000"), FlowType.CONTRIBUTION, "a"),
        CapitalFlow(datetime(2026, 2, 1), Decimal("200"), FlowType.CONTRIBUTION, "b"),
        CapitalFlow(datetime(2026, 3, 1), Decimal("100"), FlowType.WITHDRAWAL, "c"),
    ))
    html = patrimony_evolution_html(evolution)
    for text in ("Evolución patrimonial", "Capital neto aportado", "Aportaciones", "Retiradas", "1.200,00 €", "100,00 €", "01/03/2026"):
        assert text in html


def test_patrimony_evolution_view_handles_empty_history():
    evolution = PatrimonyEvolution((), Decimal("0"), Decimal("0"), Decimal("0"))
    html = patrimony_evolution_html(evolution)
    assert "Sin datos históricos suficientes" in html
