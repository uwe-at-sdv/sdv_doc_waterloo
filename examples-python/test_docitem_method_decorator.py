#!/usr/bin/env python3

from __future__ import annotations
from types import ModuleType
from typing import Any,Callable,NoReturn,cast

import functools
from abc import ABC, abstractmethod

class B:
	@abstractmethod
	def f_abstractmethod(self) -> NoReturn:
		r"""
		Preamble:
			profile:
				function
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| always raise an exception because\
				it is an abstract method.
		Parameters:
		Returns:
			Does not return.
		Raises:
			NotImplementedError:
				|Must| always raise. Method |must| be\
				implemented by derived class.
		"""
		raise NotImplementedError

class X:
	def f_method(self,q: int) -> None:
		print(f"{self.__class__.__name__}.f_method")
	@classmethod
	def f_classmethod(cls,q: float) -> None:
		print(f"{cls.__name__}.f_classmethod")
	@staticmethod
	def f_staticmethod(q: bool) -> None:
		"""
		Preamble:
			profile:
				function
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| print its name
		Parameters:
			q:
				A dummy parameter.
		Returns:
			|None|
		Raises:
		"""
		print("f_staticmethod")


def trace(fn: Callable[...,Any]) -> Any:
	@functools.wraps(fn)
	def wrapper(*args, **kwargs): #type: ignore[no-untyped-def]
			print("call", fn.__name__)
			return fn(*args, **kwargs)
	return wrapper

@trace
@functools.lru_cache(maxsize=128)
def fib(n: int) -> int:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| compute the |var|`n`-th Fibonacci number.
			|Must| cache intermediate results.
	Parameters:
		n:
			The |var|`n` in "compute the |var|`n`-th Fibonacci number".
	Returns:
		The Fibonacci number
	Raises:
		BaseException:
			|May| propagate from |mod| functools.
	"""
	if n < 2:
		return n
	return cast(int,fib(n - 1) + fib(n - 2))


if __name__ == "__main__":
	X().f_method(123)
	X.f_classmethod(4.56)
	X.f_staticmethod(True)
