#!/usr/bin/env python3
"""Select active Waterloo injection grammar in package.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Final

VALID_MODES: Final[set[str]] = {"stable", "experimental"}
GRAMMAR_PATH_BY_MODE: Final[dict[str, str]] = {
    "stable": "./syntaxes/waterloo.injection.tmLanguage.json",
    "experimental": "./syntaxes/waterloo.injection.tmLanguage.experimental.json",
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in VALID_MODES:
        print("Usage: select_grammar.py <stable|experimental>", file=sys.stderr)
        return 2

    mode = sys.argv[1]
    package_json_path = Path(__file__).resolve().parent.parent / "package.json"
    data = json.loads(package_json_path.read_text(encoding="utf-8"))

    grammar_entry = {
        "scopeName": "waterloo.injection",
        "path": GRAMMAR_PATH_BY_MODE[mode],
        "injectTo": ["source.python"],
    }
    data.setdefault("contributes", {})["grammars"] = [grammar_entry]

    package_json_path.write_text(
        json.dumps(data, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Active grammar set to '{mode}': {grammar_entry['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
