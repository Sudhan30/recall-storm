"""OURS. CLI: python -m recallstorm run --scenario ID --data DIR --out DIR"""
from __future__ import annotations

import argparse
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="recallstorm")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--scenario", required=True)
    r.add_argument("--data", required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from .plan import run
    stats = run(a.scenario, a.data, a.out, classifier=None, generator="baseline_d")
    print(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
