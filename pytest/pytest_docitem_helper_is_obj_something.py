#!/usr/bin/env python3
"""Pytests for the is_obj_* helper matrix."""

from __future__ import annotations

from typing import Callable, TypeAlias

import pytest

import sdv.doc.waterloo.docitem_helper as h


class X:
	@classmethod
	def m_cls(cls) -> None:
		pass

	@staticmethod
	def m_stat(cls) -> None:
		pass

	def m(self) -> None:
		pass

	v: int = 42
	t: TypeAlias = int | float


def f() -> None:
	pass


FUNCTIONS_TO_TEST: list[Callable[[object], bool]] = [
	h.is_obj_module,
	h.is_obj_class,
	h.is_obj_function,
	h.is_obj_method_like,
	h.is_obj_named_value,
	h.is_obj_documentable,
	h.is_obj_annotatable,
]

OBJECTS_TO_TEST: list[tuple[str, object]] = [
	("h", h),
	("X", X),
	("f", f),
	("X.m", X.m),
	("X.m_cls", X.m_cls),
	("X.m_stat", X.m_stat),
	("X.v", X.v),
	("X.t", X.t),
]

EXPECTED_MATRIX: dict[str, dict[str, bool]] = {
	"is_obj_module": {
		"h": True,
		"X": False,
		"f": False,
		"X.m": False,
		"X.m_cls": False,
		"X.m_stat": False,
		"X.v": False,
		"X.t": False,
	},
	"is_obj_class": {
		"h": False,
		"X": True,
		"f": False,
		"X.m": False,
		"X.m_cls": False,
		"X.m_stat": False,
		"X.v": False,
		"X.t": False,
	},
	"is_obj_function": {
		"h": False,
		"X": False,
		"f": True,
		"X.m": True,
		"X.m_cls": True,
		"X.m_stat": True,
		"X.v": False,
		"X.t": False,
	},
	"is_obj_method_like": {
		"h": False,
		"X": False,
		"f": False,
		"X.m": True,
		"X.m_cls": True,
		"X.m_stat": True,
		"X.v": False,
		"X.t": False,
	},
	"is_obj_named_value": {
		"h": False,
		"X": False,
		"f": False,
		"X.m": False,
		"X.m_cls": False,
		"X.m_stat": False,
		"X.v": True,
		"X.t": True,
	},
	"is_obj_documentable": {
		"h": True,
		"X": True,
		"f": True,
		"X.m": True,
		"X.m_cls": True,
		"X.m_stat": True,
		"X.v": False,
		"X.t": False,
	},
	"is_obj_annotatable": {
		"h": True,
		"X": True,
		"f": True,
		"X.m": True,
		"X.m_cls": True,
		"X.m_stat": True,
		"X.v": False,
		"X.t": False,
	},
}


@pytest.mark.parametrize("func", FUNCTIONS_TO_TEST, ids=lambda f: f.__name__)
@pytest.mark.parametrize("label,obj", OBJECTS_TO_TEST, ids=lambda p: p[0] if isinstance(p, tuple) else str(p))
def test_is_obj_matrix(func: Callable[[object], bool], label: str, obj: object) -> None:
	expected = EXPECTED_MATRIX[func.__name__][label]
	assert func(obj) is expected
