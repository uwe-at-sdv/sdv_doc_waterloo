#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must_not| demonstrate nested classes.
"""


class BadMethodOverview:
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
	Method_overview:
		m_unlisted:
			Method listed without Public_methods section.
	"""

	def m_unlisted(self) -> None:
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


class BadClassOverview:
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
	Class_overview:
		Inner:
			Nested class listed without Public_classes section.
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
