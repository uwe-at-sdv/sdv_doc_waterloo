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
		|Must| provide a demo for the CON-045 parse-error case.
"""

import sys

sys.modules.setdefault("demo_2_CON_045_m", sys.modules[__name__])


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
		"""Not a waterloo docstring"""
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
				demo_2_CON_045_m.Y_extension.m
		"""
		pass
