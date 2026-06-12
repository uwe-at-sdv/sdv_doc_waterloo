#!/usr/bin/env python3

"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
scope:
	public
Contract:
	general:
		|Must| provide a demo for the CON-043 inherited-method case.
"""

import sys

sys.modules.setdefault("demo_CON_043_m", sys.modules[__name__])


class Y_extension:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
		scope:
			extension
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	Public_methods:
		m
	"""

	def m(self) -> None:
		pass


class Other:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
		scope:
			extension
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	Public_methods:
		m
	"""

	def m(self) -> None:
		pass


class X(Y_extension):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
		scope:
			public
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	Public_methods:
		m
	"""

	def m(self) -> None:
		"""
		Preamble:
			profile:
				inherited_method
			normative_sections:
				Contract
			scope:
				public
		Contract:
			general:
				|Must| be minimal.
			base:
				demo_CON_043_m.Other.m
		"""
		pass
