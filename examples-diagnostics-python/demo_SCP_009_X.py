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
		|Must| provide classes for the base-class scope demo.
"""

class A:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
		scope:
			extension
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	"""
	pass

class X(A):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from
		scope:
			public
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	Derived_from:
		A
	"""
	pass
