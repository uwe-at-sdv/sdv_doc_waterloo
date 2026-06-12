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
		|Must| provide classes for the inherited-method scope demo.
"""

import sys

sys.modules.setdefault("demo_SCP_008_m", sys.modules[__name__])

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
				Contract, Parameters, Returns, Raises
			scope:
				extension
		Contract:
			general:
				|Must| be minimal.
		Parameters:
		Returns:
			|None|
		Raises:
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
				demo_SCP_008_m.Y_extension.m
		"""
		pass
