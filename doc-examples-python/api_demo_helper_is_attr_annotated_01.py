#!/usr/bin/env python3

from __future__ import annotations
from typing import Final
import sdv.doc.waterloo.docitem_helper as h

def f(a: int, b: float) -> None:
	pass

class X:
	v: int = 42
	c: Final[float] = 1.23

	@staticmethod
	def sm(a: int, b: float) -> None:
		pass
	@classmethod
	def cm(cls, a: int, b: float) -> None:
		pass
	def m1(self):
		pass
	def m2(self, a: int, b: Final[float]) -> None:
		pass

# Functions and methods expose parameter and return annotations.
assert not h.is_attr_annotated(X.m1, "return")
assert h.is_attr_annotated(f, "a")
assert h.is_attr_annotated(f, "b")
assert h.is_attr_annotated(f, "return")

# Static and class methods behave like plain functions for annotations.
assert h.is_attr_annotated(X.sm, "a")
assert h.is_attr_annotated(X.sm, "b")
assert h.is_attr_annotated(X.sm, "return")

assert h.is_attr_annotated(X.cm, "a")
assert h.is_attr_annotated(X.cm, "b")
assert h.is_attr_annotated(X.cm, "return")

# A method with annotations on both parameters and return value.
assert h.is_attr_annotated(X.m2, "a")
assert h.is_attr_annotated(X.m2, "b")
assert h.is_attr_annotated(X.m2, "return")

# Class attributes are also supported.
assert h.is_attr_annotated(X, "v")

# Final annotations are a separate helper, but the same object shapes apply.
assert h.is_attr_final(h, "CANONICAL_ORDER_OF_PROFILES")
assert h.is_attr_final(X, "c")
assert h.is_attr_final(X.m2, "b")
assert not h.is_attr_final(X.m2, "a")
