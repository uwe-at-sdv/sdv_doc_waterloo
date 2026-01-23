#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

class X_00:
	pass
	def spam(self) -> None:
		pass
class Y_00(X_00):
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
		"""
		pass

class X_01:
	pass
	def spam(self) -> None:
		pass
class Y_01(X_01):
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
		"""
		pass

class X_02:
	pass
	def spam(self) -> None:
		pass
class Y_02(X_02):
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
		not+a+qualified+identifier
		"""
		pass

class X_03:
	pass
	def spam(self) -> None:
		pass
class Y_03(X_03):
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
		cookies
		"""
		pass

class X_04:
	pass
	def spam(self) -> None:
		pass
class Y_04(X_04):
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
		pytest_bad_inheritance.X_03.spam
		"""
		pass

class X_05:
	pass
	def spam(self) -> None:
		"""
		"""
		pass
class Y_05(X_05):
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
		pytest_bad_inheritance.X_05.spam
		"""
		pass


class X_06:
	pass
	def spam(self) -> None:
		"""
Not a waterloo docstring
		"""
		pass
class Y_06(X_06):
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
		pytest_bad_inheritance.X_06.spam
		"""
		pass

