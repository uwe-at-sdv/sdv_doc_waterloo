"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
	scope:
		public
Contract:
	general:
		|Must| demonstrate a scope monotonicity violation between derived and base classes.
Public_classes:
	A, B, C
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

# |must_not| validate
class B(A):
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

# |must| validate
class C(A):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from
		scope:
			core
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	Derived_from:
		A
	"""
	pass

