"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| provide a module-level wrapper for the demo.
"""
from amb_base_a import Base as BaseA
from amb_base_b import Base as BaseB

class X(BaseA, BaseB):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from
	Contract:
		general:
			|Must| derive from both Base classes.
		constructor:
	Derived_from:
		Base
	"""
	pass
