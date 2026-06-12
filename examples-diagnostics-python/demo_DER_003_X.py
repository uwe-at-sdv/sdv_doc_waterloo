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
class Base:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| be a base class.
	"""
	pass

class X(Base):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from
	Contract:
		general:
			|Must| derive from Base.
		constructor:
	Derived_from:
		object
	"""
	pass
