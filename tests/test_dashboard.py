from decimal import Decimal

from pfp.dashboard import _bar, _money, print_dashboard
from pfp.reporting.portfolio_report import PortfolioReport


def test_money_format():
    assert _money(Decimal('24849.94')) == '24.849,94 EUR'


def test_bar_scales_to_percentage():
    assert _bar(Decimal('50'), 10) == '#####-----'


def test_print_dashboard_contains_key_sections(capsys):
    report = PortfolioReport(
        cash=Decimal('670'),
        invested=Decimal('24179.94'),
        market_value=Decimal('24179.94'),
        total_value=Decimal('24849.94'),
        realized_gain_loss=Decimal('0'),
        unrealized_gain_loss=Decimal('-150.06'),
        equity_value=Decimal('18134.955'),
        fixed_income_value=Decimal('4835.988'),
        gold_value=Decimal('1208.997'),
        crypto_value=Decimal('0'),
        positions=(),
    )
    print_dashboard(report)
    output = capsys.readouterr().out
    assert 'PFP DASHBOARD' in output
    assert '24.849,94' in output
    assert 'DISTRIBUCION' in output
    assert 'Renta variable' in output
