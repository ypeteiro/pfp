from pathlib import Path

from pfp.engine.portfolio_engine import PortfolioEngine
from pfp.importers.trade_republic import TradeRepublicImporter
from datetime import date, datetime, timezone
from decimal import Decimal

from pfp.domain.movement import Movement
from pfp.domain.investment import Investment
from pfp.domain.portfolio import Portfolio
from pfp.domain.position import Position
from pfp.domain.sale import Sale

CSV_FILE = Path("data/imports/trade_republic.csv")


def _movement(**overrides):
    values = dict(
        datetime=datetime(2026, 8, 19, tzinfo=timezone.utc),
        date=date(2026, 8, 19),
        account_type="DEFAULT",
        account_id=None,
        broker="Test Bank",
        category="CASH",
        type="TRANSFER_INSTANT_INBOUND",
        asset_class=None,
        name=None,
        symbol=None,
        shares=None,
        price=None,
        amount=Decimal("0"),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description=None,
        transaction_id="test",
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )
    values.update(overrides)
    return Movement(**values)


def test_import_trade_republic():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    assert len(movements) == 17


def test_build_portfolio():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    portfolio = PortfolioEngine().build(movements)
    assert len(portfolio.positions) == 9
    assert round(float(portfolio.cash), 2) == 3593.39
    assert round(float(portfolio.invested), 2) == 21406.61


def test_build_consolidates_cash_across_multiple_accounts():
    movements = [
        _movement(account_id="ABANCA_NOMINA", amount=Decimal("1000")),
        _movement(account_id="TRADE_REPUBLIC", broker="Trade Republic", amount=Decimal("2000")),
    ]
    portfolio = PortfolioEngine().build(movements)
    balances = {account.name: account.balance for account in portfolio.accounts}
    assert balances == {
        "ABANCA_NOMINA": Decimal("1000"),
        "TRADE_REPUBLIC": Decimal("2000"),
    }
    assert portfolio.cash == Decimal("3000")


def test_build_supports_account_without_investments():
    movements = [
        _movement(account_id="ABANCA_NOMINA", amount=Decimal("31000")),
        _movement(account_id="TRADE_REPUBLIC", broker="Trade Republic", amount=Decimal("1000")),
    ]
    portfolio = PortfolioEngine().build(movements)
    abanca = next(account for account in portfolio.accounts if account.name == "ABANCA_NOMINA")
    assert abanca.balance == Decimal("31000")
    assert portfolio.positions == {}
    assert portfolio.cash == Decimal("32000")


def test_build_transfer_between_accounts_is_cash_neutral():
    movements = [
        _movement(account_id="ABANCA", amount=Decimal("1000")),
        _movement(account_id="TR", broker="Trade Republic", amount=Decimal("500")),
        _movement(account_id="ABANCA", type="TRANSFER_OUTBOUND", amount=Decimal("800")),
        _movement(account_id="TR", broker="Trade Republic", type="TRANSFER_INBOUND", amount=Decimal("800")),
    ]
    portfolio = PortfolioEngine().build(movements)
    balances = {account.name: account.balance for account in portfolio.accounts}
    assert balances == {"ABANCA": Decimal("200"), "TR": Decimal("1300")}
    assert portfolio.cash == Decimal("1500")


def test_build_external_inflow_increases_consolidated_cash():
    portfolio = PortfolioEngine().build([_movement(account_id="ABANCA", amount=Decimal("1000"))])
    assert portfolio.cash == Decimal("1000")


def test_build_external_outflow_reduces_consolidated_cash():
    portfolio = PortfolioEngine().build([
        _movement(account_id="ABANCA", amount=Decimal("1000")),
        _movement(account_id="ABANCA", type="TRANSFER_OUTBOUND", amount=Decimal("300")),
    ])
    assert portfolio.cash == Decimal("700")


def test_buy_includes_fee_and_tax_in_cash_and_cost_basis():
    movement = _movement(
        account_id="TR",
        broker="Trade Republic",
        category="TRADING",
        type="BUY",
        asset_class="ETF",
        name="Test ETF",
        symbol="TEST",
        shares=Decimal("2"),
        price=Decimal("50"),
        amount=Decimal("-100"),
        fee=Decimal("-1"),
        tax=Decimal("-0.50"),
        transaction_id="test-buy-fee",
    )
    portfolio = PortfolioEngine().build([_movement(account_id="TR", broker="Trade Republic", amount=Decimal("200")), movement])
    position = portfolio.positions["TEST"]
    assert portfolio.cash == Decimal("98.50")
    assert position.invested == Decimal("101.50")
    assert position.average_price == Decimal("50.75")


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
    assert round(float(account.balance), 2) == 3593.39


def test_trade_republic_account_name():
    importer = TradeRepublicImporter()
    movements = TradeRepublicImporter().load(CSV_FILE)
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


def _sell_movement(shares="0.1", amount="150", transaction_id="test-sell"):
    return Movement(
        datetime=datetime(2026, 8, 1, tzinfo=timezone.utc),
        date=date(2026, 8, 1),
        account_type="DEFAULT",
        account_id=None,
        broker="Trade Republic",
        category="CASH",
        type="SELL",
        asset_class="EQUITY",
        name="iShares Core MSCI World UCITS ETF",
        symbol="IE00B4L5Y983",
        shares=Decimal(shares),
        price=Decimal(amount) / Decimal(shares),
        amount=Decimal(amount),
        fee=Decimal("0"),
        tax=Decimal("0"),
        currency="EUR",
        original_amount=None,
        original_currency=None,
        fx_rate=None,
        description="Test sell",
        transaction_id=transaction_id,
        counterparty_name=None,
        counterparty_iban=None,
        payment_reference=None,
        mcc_code=None,
    )


def test_sell_reduces_position_and_increases_cash():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    movements.append(_sell_movement())
    portfolio = PortfolioEngine().build(movements)
    position = portfolio.positions["IE00B4L5Y983"]
    assert position.shares == Decimal("0.692682")
    assert portfolio.cash == Decimal("3743.39")


def test_sell_reduces_invested_at_average_cost():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    before = PortfolioEngine().build(movements)
    movements.append(_sell_movement(transaction_id="test-sell-002"))
    portfolio = PortfolioEngine().build(movements)
    position = portfolio.positions["IE00B4L5Y983"]
    expected_average_price = before.positions["IE00B4L5Y983"].average_price
    expected_invested = expected_average_price * Decimal("0.692682")
    assert position.shares == Decimal("0.692682")
    assert position.invested.quantize(Decimal("0.0000000001")) == expected_invested.quantize(Decimal("0.0000000001"))
    assert position.average_price.quantize(Decimal("0.0000000001")) == expected_average_price.quantize(Decimal("0.0000000001"))


def test_sell_records_realized_gain_loss():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    before = PortfolioEngine().build(movements)
    movements.append(_sell_movement())
    portfolio = PortfolioEngine().build(movements)
    average_price = before.positions["IE00B4L5Y983"].average_price
    expected_realized = Decimal("150") - (average_price * Decimal("0.1"))
    assert portfolio.realized_gain_loss.quantize(Decimal("0.0000000001")) == expected_realized.quantize(Decimal("0.0000000001"))


def test_sell_records_realized_loss():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    before = PortfolioEngine().build(movements)
    movements.append(_sell_movement(amount="10", transaction_id="test-sell-loss"))
    after = PortfolioEngine().build(movements)
    realized_change = after.realized_gain_loss - before.realized_gain_loss
    average_price = before.positions["IE00B4L5Y983"].average_price
    expected_realized = Decimal("10") - (average_price * Decimal("0.1"))
    assert realized_change < Decimal("0")
    assert realized_change.quantize(Decimal("0.0000000001")) == expected_realized.quantize(Decimal("0.0000000001"))


def test_sell_rejects_more_shares_than_position():
    importer = TradeRepublicImporter()
    movements = importer.load(CSV_FILE)
    movements.append(_sell_movement(shares="1", amount="150", transaction_id="test-sell-too-many"))
    try:
        PortfolioEngine().build(movements)
    except ValueError as exc:
        assert str(exc) == "Insufficient shares"
    else:
        raise AssertionError("Expected ValueError")


def test_build_applies_persisted_sale_once():
    base = PortfolioEngine().build(TradeRepublicImporter().load(CSV_FILE))
    sale = Sale(
        datetime=datetime(2026, 8, 10, tzinfo=timezone.utc),
        symbol="IE00B4L5Y983",
        shares=Decimal("0.1"),
        amount=Decimal("150"),
        price=Decimal("1500"),
    )
    portfolio = PortfolioEngine().build(TradeRepublicImporter().load(CSV_FILE), sales=[sale])
    position = portfolio.positions["IE00B4L5Y983"]
    assert position.shares == base.positions["IE00B4L5Y983"].shares - Decimal("0.1")
    assert portfolio.cash == base.cash + Decimal("150")


def test_apply_investment_reduces_cash_and_increases_position():
    portfolio = Portfolio()
    portfolio.cash = Decimal("1000")
    investment = Investment(datetime=datetime.now(timezone.utc), symbol="TEST", shares=Decimal("4"), amount=Decimal("400"), price=Decimal("100"), portfolio_class="EQUITY")
    PortfolioEngine().apply_investment(portfolio, investment)
    position = portfolio.positions["TEST"]
    assert portfolio.cash == Decimal("600")
    assert position.shares == Decimal("4")
    assert position.invested == Decimal("400")
    assert position.average_price == Decimal("100")
    assert position.portfolio_class == "EQUITY"


def test_apply_investment_adds_to_existing_position():
    portfolio = Portfolio()
    portfolio.cash = Decimal("1000")
    portfolio.positions["TEST"] = Position(symbol="TEST", name="Test", shares=Decimal("2"), invested=Decimal("200"), average_price=Decimal("100"), portfolio_class="EQUITY")
    investment = Investment(datetime=datetime.now(timezone.utc), symbol="TEST", shares=Decimal("4"), amount=Decimal("600"), price=Decimal("150"), portfolio_class="EQUITY")
    PortfolioEngine().apply_investment(portfolio, investment)
    position = portfolio.positions["TEST"]
    assert portfolio.cash == Decimal("400")
    assert position.shares == Decimal("6")
    assert position.invested == Decimal("800")
    assert position.average_price == Decimal("800") / Decimal("6")


def test_apply_investment_rejects_insufficient_cash():
    portfolio = Portfolio()
    portfolio.cash = Decimal("100")
    investment = Investment(datetime=datetime.now(timezone.utc), symbol="TEST", shares=Decimal("2"), amount=Decimal("200"), price=Decimal("100"), portfolio_class="EQUITY")
    try:
        PortfolioEngine().apply_investment(portfolio, investment)
    except ValueError as exc:
        assert str(exc) == "Insufficient cash"
    else:
        raise AssertionError("Expected ValueError")


def test_build_applies_persisted_investment_once():
    investment = Investment(datetime=datetime(2026, 8, 10, tzinfo=timezone.utc), symbol="TEST", shares=Decimal("4"), amount=Decimal("400"), price=Decimal("100"), portfolio_class="EQUITY")
    portfolio = PortfolioEngine().build(movements=[], investments=[investment])
    position = portfolio.positions["TEST"]
    assert portfolio.cash == Decimal("-400")
    assert position.shares == Decimal("4")
    assert position.invested == Decimal("400")
    assert position.portfolio_class == "EQUITY"


def test_build_applies_multiple_persisted_investments_once_each():
    first = Investment(datetime=datetime(2026, 8, 10, tzinfo=timezone.utc), symbol="TEST", shares=Decimal("2"), amount=Decimal("200"), price=Decimal("100"), portfolio_class="EQUITY")
    second = Investment(datetime=datetime(2026, 8, 11, tzinfo=timezone.utc), symbol="TEST", shares=Decimal("3"), amount=Decimal("360"), price=Decimal("120"), portfolio_class="EQUITY")
    portfolio = PortfolioEngine().build(movements=[], investments=[first, second])
    position = portfolio.positions["TEST"]
    assert portfolio.cash == Decimal("-560")
    assert position.shares == Decimal("5")
    assert position.invested == Decimal("560")
    assert position.average_price == Decimal("112")
