#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import tempfile
from pathlib import Path
from typing import Any


def _minimal_docstring_for_module() -> str:
    lines = [
        '"""',
        "Preamble:",
        "\tprofile:",
        "\t\tmodule",
        "\tnormative_sections:",
        "\t\tContract",
        "Contract:",
        "\tgeneral:",
        '"""',
        "",
    ]
    return "\n".join(lines)


def _minimal_docstring_for_class() -> str:
    lines = [
        '"""',
        "Preamble:",
        "\tprofile:",
        "\t\tclass",
        "\tnormative_sections:",
        "\t\tContract",
        "Contract:",
        "\tgeneral:",
        '"""',
        "",
    ]
    return "\n".join(lines)


def _minimal_docstring_for_function() -> str:
    lines = [
        '"""',
        "Preamble:",
        "\tprofile:",
        "\t\tfunction",
        "\tnormative_sections:",
        "\t\tContract, Parameters, Returns, Raises",
        "Contract:",
        "\tgeneral:",
        "Parameters:",
        "Returns:",
        "Raises:",
        '"""',
        "",
    ]
    return "\n".join(lines)


def _validate_source_fragment(kind: str, source_fragment: str) -> None:
    if kind == "module":
        return

    tree = ast.parse(source_fragment)
    if not tree.body:
        raise ValueError("source_fragment is empty after parsing.")

    node = tree.body[0]
    if kind == "class" and not isinstance(node, ast.ClassDef):
        raise ValueError("source_fragment does not parse to a class header.")
    if kind == "function" and not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ValueError("source_fragment does not parse to a function header.")


def _write_docstring_to_tmp(content: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".txt",
        prefix="waterloo-docstring-",
        delete=False,
    ) as handle:
        handle.write(content)
        return str(Path(handle.name))


def main() -> int:
    try:
        payload = json.loads(input())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"Invalid JSON input: {exc}"}))
        return 1

    try:
        version = payload.get("version")
        command = payload.get("command")
        kind = payload.get("kind")
        source_fragment = payload.get("source_fragment", "")

        if version != 1:
            raise ValueError(f"Unsupported protocol version: {version!r}.")
        if command != "generate_minimal_docstring_to_tmp":
            raise ValueError(f"Unsupported command: {command!r}.")
        if kind not in {"module", "class", "function"}:
            raise ValueError(f"Unsupported kind: {kind!r}.")
        if not isinstance(source_fragment, str):
            raise ValueError("source_fragment must be a string.")

        _validate_source_fragment(kind, source_fragment)

        if kind == "module":
            doc = _minimal_docstring_for_module()
        elif kind == "class":
            doc = _minimal_docstring_for_class()
        else:
            doc = _minimal_docstring_for_function()

        tmp_path = _write_docstring_to_tmp(doc)
        print(json.dumps({"ok": True, "kind": kind, "tmp_file": tmp_path}))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
