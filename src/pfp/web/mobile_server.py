"""Convenience launcher for running PFP on a local network."""

from __future__ import annotations

import argparse
from pathlib import Path

from pfp.web.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PFP web app for access from a mobile device")
    parser.add_argument("movements_file")
    parser.add_argument("--investments-file", default="data/imports/investments.csv")
    parser.add_argument("--sales-file", default="data/imports/sales.csv")
    parser.add_argument("--assets-file", default="data/assets.csv")
    parser.add_argument("--reconciliations-file", default="data/accounts/reconciliation_history.csv")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(
        Path(args.movements_file),
        host="0.0.0.0",
        port=args.port,
        investments_file=Path(args.investments_file),
        sales_file=Path(args.sales_file),
        assets_file=Path(args.assets_file),
        reconciliations_file=Path(args.reconciliations_file),
    )


if __name__ == "__main__":
    main()
