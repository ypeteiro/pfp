from pathlib import Path

from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.trade_republic import TradeRepublicImporter
from datetime import date, datetime, timezone
from decimal import Decimal

from pfp.domain.movement import Movement

from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position

CSV_FILE = Path("data/imports/trade_republic.csv")


def test_import_trade_republic():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    assert len(movements) == 17


def test_build_portfolio():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    portfolio = PortfolioEngine().build(movements)

    assert len(portfolio.positions) == 9
    assert round(float(portfolio.cash), 2) == 3603.39
    assert round(float(portfolio.invested), 2) == 21396.61


def test_portfolio_creates_account_from_movements():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    portfolio = PortfolioEngine().build(movements)

    assert len(portfolio.accounts) == 1

    account = portfolio.accounts[0]

    assert account.broker == "Trade Republic"
    assert account.currency == "EUR"


def test_trade_republic_account_balance():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    portfolio = PortfolioEngine().build(movements)

    assert len(portfolio.accounts) == 1

    account = portfolio.accounts[0]

    assert account.name == "Trade Republic"
    assert account.broker == "Trade Republic"
    assert account.currency == "EUR"
    assert round(float(account.balance), 2) == 3603.39
    
def test_trade_republic_account_name():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    portfolio = PortfolioEngine().build(movements)

    account = portfolio.accounts[0]

    assert account.name == "Trade Republic"
    
def test_portfolio_cash_matches_account_balance():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    portfolio = PortfolioEngine().build(movements)

    assert len(portfolio.accounts) == 1

    account = portfolio.accounts[0]

    assert portfolio.cash == account.balance

def test_sell_reduces_position_and_increases_cash():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    sell = Movement(
        datetime=datetime(2026, 8, 1, tzinfo=timezone.utc),
        date=date(2026, 8, 1),
        account_type="DEFAULT",
        broker="Trade Republic",
        category="CASH",
        type="SELL",
        asset_class="EQUITY",
        name="iShares Core MSCI World UCITS ETF",
        symbol="IE00B4L5Y983",
        shares=Decimal("0.1"),
        price=Decimal("150"),
        amount=Decimal("150"),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description="Test sell",
        transaction_id="test-sell-001",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )

    movements.append(sell)

    portfolio = PortfolioEngine().build(movements)

    position = portfolio.positions["IE00B4L5Y983"]

    assert position.shares == Decimal("0.692682")
    assert portfolio.cash == Decimal("3753.39")

def test_sell_reduces_invested_at_average_cost():
    importer = TradeRepublicImporter()

    movements = importer.load(CSV_FILE)

    sell = Movement(
        datetime=datetime(2026, 8, 1, tzinfo=timezone.utc),
        date=date(2026, 8, 1),
        account_type="DEFAULT",
        broker="Trade Republic",
        category="CASH",
        type="SELL",
        asset_class="EQUITY",
        name="iShares Core MSCI World UCITS ETF",
        symbol="IE00B4L5Y983",
        shares=Decimal("0.1"),
        price=Decimal("150"),
        amount=Decimal("150"),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description="Test sell",
        transaction_id="test-sell-002",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )

    movements.append(sell)

    portfolio = PortfolioEngine().build(movements)

    position = portfolio.positions["IE00B4L5Y983"]

    expected_average_price = Decimal("100") / Decimal("0.792682")
    expected_invested = expected_average_price * Decimal("0.692682")

    assert position.shares == Decimal("0.692682")
    assert position.invested.quantize(Decimal("0.0000000001")) == (
        expected_invested.quantize(Decimal("0.0000000001"))
    )

    assert position.average_price.quantize(Decimal("0.0000000001")) == (
        expected_average_price.quantize(Decimal("0.0000000001"))
    )
    
def test_apply_investment_reduces_cash_and_increases_position():
    portfolio = Portfolio()

    portfolio.cash = Decimal("1000")

    investment = Investment(
        datetime=datetime.now(timezone.utc),
        symbol="TEST",
        shares=Decimal("4"),
        amount=Decimal("400"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
    )

    PortfolioEngine().apply_investment(
        portfolio,
        investment,
    )

    position = portfolio.positions["TEST"]

    assert portfolio.cash == Decimal("600")
    assert position.shares == Decimal("4")
    assert position.invested == Decimal("400")
    assert position.average_price == Decimal("100")
    assert position.portfolio_class == "EQUITY"


def test_apply_investment_adds_to_existing_position():
    portfolio = Portfolio()

    portfolio.cash = Decimal("1000")

    portfolio.positions["TEST"] = Position(
        symbol="TEST",
        name="Test",
        shares=Decimal("2"),
        invested=Decimal("200"),
        average_price=Decimal("100"),
        portfolio_class="EQUITY",
    )

    investment = Investment(
        datetime=datetime.now(timezone.utc),
        symbol="TEST",
        shares=Decimal("4"),
        amount=Decimal("600"),
        price=Decimal("150"),
        portfolio_class="EQUITY",
    )

    PortfolioEngine().apply_investment(
        portfolio,
        investment,
    )

    position = portfolio.positions["TEST"]

    assert portfolio.cash == Decimal("400")
    assert position.shares == Decimal("6")
    assert position.invested == Decimal("800")
    assert position.average_price == (
        Decimal("800") / Decimal("6")
    )


def test_apply_investment_rejects_insufficient_cash():
    portfolio = Portfolio()

    portfolio.cash = Decimal("100")

    investment = Investment(
        datetime=datetime.now(timezone.utc),
        symbol="TEST",
        shares=Decimal("2"),
        amount=Decimal("200"),
        price=Decimal("100"),
        portfolio_class="EQUITY",
    )

    try:
        PortfolioEngine().apply_investment(
            portfolio,
            investment,
        )
    except ValueError as exc:
        assert str(exc) == "Insufficient cash"
    else:
        raise AssertionError(
            "Expected ValueError"
        )    
