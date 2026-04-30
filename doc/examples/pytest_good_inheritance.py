#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

class X:
	pass
	def spam(self) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must_not| do anyhing
Parameters:
Returns:
	|Must| return None
Raises:
		"""
		pass
class Y(X):
	pass
	def spam(self) -> None:
		"""
Preamble:
	profile:
		inherited_method
	normative_sections:
		Contract
Contract:
	general:
		|Must_not| do anyhing
	base:
		pytest_good_inheritance.X.spam
		"""
		pass
class Z(Y):
	pass
	def spam(self) -> None:
		"""
Preamble:
	profile:
		inherited_method
	normative_sections:
		Contract
Contract:
	general:
		|Must_not| do anyhing
	base:
		pytest_good_inheritance.Y.spam
		"""
		pass
