#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

"""
Preamble:	
	profile:
		module
	normative_sections:
		Contract
	status:
		stable
Contract:
	general:
		|Must| collect bad status examples.
"""

class X_00:
	def f_status_multiple(self) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
	status:
		experimental
		stable
Contract:
	general:
		|Must_not| do anything.
Parameters:
Returns:
	|None|
Raises:
		"""
		pass

class X_01:
	def f_status_not_identifier(self) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
	status:
		not+an+identifier
Contract:
	general:
		|Must_not| do anything.
Parameters:
Returns:
	|None|
Raises:
		"""
		pass

class X_02:
	def f_status_unknown_tag(self) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
	status:
		unstable
Contract:
	general:
		|Must_not| do anything.
Parameters:
Returns:
	|None|
Raises:
		"""
		pass

class X_03:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Method_overview, Public_methods
	status:
		experimental
Contract:
	general:
		|Must_not| do anything.
	constructor:
		|Must| be default-constructible
Method_overview:
	f_status_multiple:
		Bad: multiple items
Public_methods:
	f_status_multiple
	"""
