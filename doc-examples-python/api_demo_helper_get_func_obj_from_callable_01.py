#!/usr/bin/env python3

from __future__ import annotations
from typing import Generator
import math
import sdv.doc.waterloo.docitem_helper as h

# Excerpts from the contract:
# Must handle functions at module level.
def f() -> None:
	pass

# Must handle generators
def g() -> Generator[int,None,None]:
	yield 42

class X:
	def __call__(self) -> None:
		print("Hello Kitty")
	# Must handle functions in classes without decorators.
	def m() -> None:
		pass
	# Must handle functions in classes with decorator `@classmethod`.
	@classmethod
	def m_cls(cls) -> None:
		pass
	# Must handle functions in classes with decorator `@staticmethod`.
	@staticmethod
	def m_stat(cls) -> None:
		pass
	# Must handle generators
	def g() -> Generator[int,None,None]:
		yield 42

def show(label: str, obj: object) -> None:
	print(f"{label}: {h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(obj))}")

def test_get_func_obj_from_callable() -> None:
	x = X()
	show("class", X)
	show("module function", f)
	show("generator function", g)
	show("callable instance", x)
	show("instance method", X.m)
	show("classmethod", X.m_cls)
	show("staticmethod", X.m_stat)
	show("generator method", X.g)
	show("function helper", h.get_func_obj_from_callable)
	show("builtin math.sin", math.sin)
	show("builtin print", print)

if __name__ == "__main__":
	test_get_func_obj_from_callable()
