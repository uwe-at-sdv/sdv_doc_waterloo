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
		|Must| demonstrate a scope monotonicity violation for a module.
Public_classes:
	X_extension
"""

class X_extension:
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
