"""Entry point for `python -m recallstorm`."""
from __future__ import annotations

import sys
from recallstorm.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
