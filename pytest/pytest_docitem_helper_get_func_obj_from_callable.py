#!/usr/bin/env python3
"""Pytests for get_func_obj_from_callable."""

from __future__ import annotations

from typing import Generator
import math

import sdv.doc.waterloo.docitem_helper as h


def f() -> None:
	pass


def g() -> Generator[int, None, None]:
	yield 42


class X:
	def __call__(self) -> None:
		print("Hello Kitty")

	def m() -> None:
		pass

	@classmethod
	def m_cls(cls) -> None:
		pass

	@staticmethod
	def m_stat(cls) -> None:
		pass

	def g() -> Generator[int, None, None]:
		yield 42


CASES: list[tuple[str, object, str | None]] = [
	("callable_class", X, "X.__call__"),
	("callable_instance", X(), "X.__call__"),
	("module_function", f, "f"),
	("generator_function", g, "g"),
	("instance_method", X.m, "X.m"),
	("bound_classmethod", X.m_cls, "X.m_cls"),
	("staticmethod", X.m_stat, "X.m_stat"),
	("generator_method", X.g, "X.g"),
	("builtin_math", math.sin, "math.sin"),
	("builtin_print", print, "builtins.print"),
]


def test_get_func_obj_from_callable_matrix() -> None:
	for label, obj, expected_qname in CASES:
		func_obj = h.get_func_obj_from_callable(obj)
		if expected_qname is None:
			assert func_obj is None, label
		else:
			assert func_obj is not None, label
			assert h.get_obj_fully_qualified_name(func_obj).endswith(expected_qname), label
