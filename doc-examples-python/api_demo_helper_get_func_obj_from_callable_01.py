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
	# Must handle functions in classes with decorator `@staticmethod`.
	@classmethod
	def m_cls(cls) -> None:
		pass
	# Must andle functions in classes with decorator `@classmethod`.
	@staticmethod
	def m_stat(cls) -> None:
		pass
	# Must handle generators
	def g() -> Generator[int,None,None]:
		yield 42

def test_get_func_obj_from_callable() -> None:
	x = X()
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(X)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(f)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(g)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(x)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(X.m)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(X.m_cls)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(X.m_stat)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(X.g)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(h.get_func_obj_from_callable)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(math.sin)))
	print(h.get_obj_fully_qualified_name(h.get_func_obj_from_callable(print)))

if __name__ == "__main__":
	test_get_func_obj_from_callable()
