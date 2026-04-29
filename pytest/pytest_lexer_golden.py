#!/usr/bin/env python3
"""Golden-file tests for PythonWaterlooLexer token streams."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from pytest_common import ROOT, PATH_EXAMPLES

GOLDEN_IN = PATH_EXAMPLES / "golden_files" / "in"
GOLDEN_OUT = PATH_EXAMPLES / "golden_files" / "out"
LEXER_PATH = ROOT / "ide-plugins" / "pygments" / "python_waterloo_lexer.py"


def _load_python_waterloo_lexer_class():
	spec = importlib.util.spec_from_file_location("python_waterloo_lexer_local", LEXER_PATH)
	if spec is None or spec.loader is None:
		raise RuntimeError(f"Could not load lexer module from {LEXER_PATH}")
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module.PythonWaterlooLexer


PythonWaterlooLexer = _load_python_waterloo_lexer_class()


def _serialize_tokens(src: str) -> str:
	lexer = PythonWaterlooLexer()
	lines: list[str] = []
	for pos, token_type, text in lexer.get_tokens_unprocessed(src):
		lines.append(f"{pos}|{token_type}|{text!r}")
	return "\n".join(lines) + "\n"


def _collect_inputs() -> list[Path]:
	return sorted(GOLDEN_IN.glob("*.py"))


@pytest.mark.parametrize("in_file", _collect_inputs(), ids=lambda p: p.stem)
def test_lexer_golden_file(in_file: Path) -> None:
	"""Compare token stream with fixed golden snapshot."""
	out_file = GOLDEN_OUT / f"{in_file.stem}.tokens.txt"

	src = in_file.read_text(encoding="utf-8")
	actual = _serialize_tokens(src)
	if not out_file.exists():
		out_file.write_text(actual, encoding="utf-8")
		pytest.skip(f"Created golden snapshot: {out_file}")

	expected = out_file.read_text(encoding="utf-8")
	assert actual == expected
