import sys

from pfp.cli import main
from pfp.history_cli import main as history_main


if len(sys.argv) > 1 and sys.argv[1] == "history":
    history_main(sys.argv[2:])
else:
    main()
