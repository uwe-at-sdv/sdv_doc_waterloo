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
		|Must| provide a demo for the CON-045 validation-error case.
"""

import sys

sys.modules.setdefault("demo_3_CON_045_m", sys.modules[__name__])


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
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Missing_section
			scope:
				public
		Contract:
			general:
				|Must| be minimal.
		"""
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
				demo_3_CON_045_m.Y_extension.m
		"""
		pass
