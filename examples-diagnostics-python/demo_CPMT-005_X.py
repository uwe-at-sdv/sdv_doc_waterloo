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
class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| contain a misclassified method entry in Public_methods.
		constructor:
	Public_methods:
		Y
	"""
	class Y:
		pass
