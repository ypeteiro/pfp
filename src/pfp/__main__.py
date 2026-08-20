import sys

from pfp.cli import main
from pfp.history_cli import main as history_main
from pfp.portfolio_cli import run_portfolio


if len(sys.argv) > 1 and sys.argv[1] == "history":
    history_main(sys.argv[2:])
elif len(sys.argv) > 1 and sys.argv[1] == "portfolio":
    parser_args = sys.argv[2:]
    if not parser_args:
        raise SystemExit("portfolio requires a movements file")
    movements_file = parser_args[0]
    investments_file = "data/imports/investments.csv"
    sales_file = "data/imports/sales.csv"
    index = 1
    while index < len(parser_args):
        if parser_args[index] == "--investments-file" and index + 1 < len(parser_args):
            investments_file = parser_args[index + 1]
            index += 2
        elif parser_args[index] == "--sales-file" and index + 1 < len(parser_args):
            sales_file = parser_args[index + 1]
            index += 2
        else:
            raise SystemExit(f"unknown portfolio argument: {parser_args[index]}")
    run_portfolio(movements_file, investments_file, sales_file)
else:
    main()
