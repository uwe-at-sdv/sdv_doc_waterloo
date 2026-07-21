#!/usr/bin/env python3
"""Interpreter fuer die Snippet-Sprache (siehe snippets_syntax.txt).

# Version: 1.2.0
# - 1.2.0 [2026-07-21]	Function write returns content.
# - 1.1.0 [2026-07-21]	Function lit for literals.
# - 1.0.0 [2026-07-21]	initial

Ein Snippet-Dokument ist gueltiges JSON. Jeder Knoten ist entweder
ein String-Literal oder ein Dict mit genau einem $-Schluessel (= Funktion).
Auswertung ist ein Tree-Walk; jeder Knoten evaluiert zu einem String.

Aufruf:
    python sdv_snippets.py <snippet.json> [--option wert ...]
"""
from __future__ import annotations

import json
import pathlib
import sys


class Interp:
    def __init__(self, opts: dict[str, str], basedir: str | pathlib.Path = "."):
        self.opts = opts
        self.basedir = pathlib.Path(basedir)

    def eval(self, node):
        if isinstance(node, str):
            return node
        if not isinstance(node, dict) or not node:
            raise SyntaxError(f"kein gueltiger Knoten: {node!r}")
        fn = self._fn_key(node)
        handler = getattr(self, "fn_" + fn[1:], None)
        if handler is None:
            raise SyntaxError(f"unbekannte Funktion: {fn}")
        return handler(node[fn])

    @staticmethod
    def _fn_key(node: dict) -> str:
        keys = [k for k in node if k.startswith("$")]
        if len(keys) != 1:
            raise SyntaxError(f"Knoten braucht genau einen $-Schluessel: {list(node)}")
        return keys[0]

    @staticmethod
    def _subject(payload: dict) -> dict:
        key = Interp._fn_key(payload)
        return {key: payload[key]}

    def _resolve(self, path: str) -> pathlib.Path:
        p = pathlib.Path(path)
        return p if p.is_absolute() else self.basedir / p

    def fn_read(self, a):
        return self._resolve(self.eval(a["path"])).read_text().rstrip("\n")

    def fn_write(self, a):
        content = self.eval(a["content"])
        self._resolve(self.eval(a["path"])).write_text(content + "\n")
        return content

    def fn_opt(self, a):
        name = self.eval(a["arg"])
        try:
            return self.opts[name]
        except KeyError:
            raise KeyError(f"Option nicht gesetzt: {name}") from None

    def fn_switch(self, a):
        subj = self.eval(self._subject(a))
        for k, v in a.items():
            if not k.startswith("$") and k == subj:
                return self.eval(v)
        raise KeyError(f"$switch: kein Zweig fuer {subj!r}")

    def fn_replace(self, a):
        s = self.eval(self._subject(a))
        for k, v in a.items():
            if not k.startswith("$"):
                s = s.replace(k, self.eval(v))
        return s

    def fn_lit(self, a):
        if not isinstance(a, str):
            raise SyntaxError(f"$lit erwartet ein String-Literal: {a!r}")
        return a


def run(doc: dict, opts: dict[str, str], doc_dir: pathlib.Path):
    interp = Interp(opts, basedir=doc_dir)
    if isinstance(doc, dict) and "$basedir" in doc:
        base = interp.eval(doc["$basedir"])
        interp.basedir = (doc_dir / base).resolve()
    results = []
    for k, v in doc.items():
        if k == "$basedir":
            continue
        results.append(interp.eval({k: v}))
    return results


def parse_opts(argv: list[str]) -> dict[str, str]:
    opts: dict[str, str] = {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                opts[a] = argv[i + 1]
                i += 2
            else:
                opts[a] = ""
                i += 1
        else:
            i += 1
    return opts


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    positionals = [a for a in argv if not a.startswith("--")]
    if not positionals:
        print(__doc__, file=sys.stderr)
        return 2
    snippet = pathlib.Path(positionals[0])
    doc = json.loads(snippet.read_text())
    run(doc, parse_opts(argv), snippet.resolve().parent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
