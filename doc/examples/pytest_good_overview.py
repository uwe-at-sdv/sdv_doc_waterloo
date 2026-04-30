#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions
Contract:
	general:
		|Must| serve as a positive Overview example.
Class_overview:
	GoodClass:
		Informative text for the class overview.
Function_overview:
	good_function:
		Informative text for the function overview.
Public_classes:
	GoodClass
Public_functions:
	good_function
"""


class GoodClass:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes, Public_methods
	Contract:
		general:
			|Must| exist for testing.
		constructor:
			|Must| be default-constructible.
	Class_overview:
		Inner:
			Informative text for the nested class.
	Method_overview:
		good_method:
			Informative text for the method.
	Public_classes:
		Inner
	Public_methods:
		good_method
	"""

	class Inner:
		"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract
		Contract:
			general:
				|Must| exist for testing.
			constructor:
				|Must| be default-constructible.
		"""
		pass

	def good_method(self) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| exist for testing.
		Parameters:
		Returns:
			|None|
		Raises:
		"""
		pass


def good_function() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| exist for testing.
	Parameters:
	Returns:
		|None|
	Raises:
	"""
	pass
