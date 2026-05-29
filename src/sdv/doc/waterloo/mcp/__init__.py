"""Waterloo MCP package."""

from __future__ import annotations

from pathlib import Path


def _read_version() -> str:
    path = Path(__file__).resolve().with_name("VERSION")
    try:
        return path.read_text(encoding="utf-8").strip() or "0.0.0"
    except Exception:
        return "0.0.0"


__version__ = _read_version()

