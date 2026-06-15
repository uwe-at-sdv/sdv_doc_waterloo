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
		|Must| provide a demo for the CON-040 inherited-method case.
"""

import sys

sys.modules.setdefault("demo_1_CON_040_m", sys.modules[__name__])


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


class Z_extension:
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
				demo_1_CON_040_m.Y_extension.m
				demo_1_CON_040_m.Z_extension.m
		"""
		pass
