# PFP — Personal Finance Portfolio

PFP is a Python CLI for tracking and managing an investment portfolio from Trade Republic transaction exports.

## Current capabilities

- Import Trade Republic CSV movements.
- Build and value the portfolio.
- Fetch market prices through Yahoo Finance with Vanguard fallback.
- Convert non-EUR prices to EUR, including USD and GBP/GBp.
- Recommend investments for new contributions.
- Calculate portfolio rebalancing against target allocations.
- Execute rebalance orders and persist them.
- Register investments and sales.
- Persist investment and sale operations with idempotency keys.
- Rebuild the portfolio from the original movements plus persisted operations.
- Calculate realized gains and losses.

## Requirements

- Python 3.13+

Install development dependencies with:

```bash
python -m pip install -e ".[dev]"
```

## Tests

Run the complete test suite with:

```bash
python -m pytest
```

## CLI

### Portfolio valuation

```bash
python -m pfp portfolio data/imports/trade_republic.csv
```

### Investment recommendation

```bash
python -m pfp recommend 800 data/imports/trade_republic.csv
```

### Rebalancing

Calculate the required orders:

```bash
python -m pfp rebalance data/imports/trade_republic.csv
```

Execute and persist the orders:

```bash
python -m pfp rebalance data/imports/trade_republic.csv --execute
```

### Investment order

```bash
python -m pfp invest-order IE00BK5BQT80 500 data/imports/trade_republic.csv
```

### Sale

```bash
python -m pfp sell IE00BK5BQT80 2 250 data/imports/trade_republic.csv
```

Persisted operations are stored under `data/imports/` by default. That directory is intentionally ignored by Git because it contains local financial data.

## Project structure

- `src/pfp/domain/` — portfolio domain model.
- `src/pfp/engine/` — portfolio, investment, sale and rebalance logic.
- `src/pfp/importers/` — Trade Republic and persistence adapters.
- `src/pfp/market/` — market prices, currencies and providers.
- `src/pfp/excel/` — Excel workbook support.
- `tests/` — automated test suite.

## Status

PFP is at the first functional release stage. The core portfolio workflow is covered by automated tests and the project is being hardened for release.

## License

MIT.
