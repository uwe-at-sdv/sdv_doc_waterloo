#!/usr/bin/env python3

from __future__ import annotations
from typing import Any, TYPE_CHECKING
import sdv.doc.waterloo.docitem_helper as h

def join_strings(values: list[Any]) -> str:
	if h.is_list_of_str(values):
		# mypy narrows `values` to `list[str]` in this branch.
		if TYPE_CHECKING:
			# h.is_list_of_str returns TypeGuard by annotation.
			# So, here we know at type checking that values is
			# a list of strings. mypy output is:
			# `note: Revealed type is "list[str]"`
			reveal_type(values)
		return ", ".join(values)
	return "<not a list[str]>"

assert join_strings(["a", "b"]) == "a, b"
assert join_strings([1, 2]) == "<not a list[str]>"
