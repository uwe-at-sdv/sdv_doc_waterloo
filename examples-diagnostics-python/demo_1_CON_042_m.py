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
		|Must| provide a demo for the CON-042 inherited-method case.
"""

import sys

sys.modules.setdefault("demo_1_CON_042_m", sys.modules[__name__])


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

# With these it would run error-free.
#class MissingClass(Y_extension):
#	def m():
#		"""
#		Preamble:
#			profile:
#				method
#			normative_sections:
#				Contract, Parameters, Returns, Raises
#		Contract:
#			general:
#		Parameters:
#		Returns:
#		Raises:
#		"""
#		pass
#
#class X(MissingClass):
#	...

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
				demo_1_CON_042_m.MissingClass.m
		"""
		pass
