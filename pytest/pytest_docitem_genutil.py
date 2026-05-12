#!/usr/bin/env python3
from __future__ import annotations

import ast

from sdv.doc.waterloo.docitem_genutil import parse_source_fragment


def test_parse_source_fragment_accepts_inherited_method() -> None:
	node = parse_source_fragment("inherited_method", "def inherited(self) -> None: pass\n")
	assert isinstance(node, ast.FunctionDef)
	assert node.name == "inherited"


def test_parse_source_fragment_rejects_non_method_for_inherited_method() -> None:
	try:
		parse_source_fragment("inherited_method", "class NotAMethod: pass\n")
	except RuntimeError as exc:
		assert str(exc) == "source_fragment does not parse to a function/method header"
	else:
		raise AssertionError("expected RuntimeError")
