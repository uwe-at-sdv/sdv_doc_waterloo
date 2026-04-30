"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
	scope:
		core
Contract:
	general:
		|Must| demonstrate a scope monotonicity violation between module and class.
Public_classes:
	C_ext
"""

class C_ext:
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

