"""Minimal stdin/stdout echo server for transport debugging."""

from __future__ import annotations

import sys


def main() -> int:
    print("stdio_echo: ready", file=sys.stderr, flush=True)
    for line in sys.stdin:
        text = line.rstrip("\n")
        print(f"ECHO {text}", flush=True)
    print("stdio_echo: eof", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
