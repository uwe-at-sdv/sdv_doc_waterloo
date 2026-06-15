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
			Contract, Public_classes
	Contract:
		general:
			|Must| contain a misclassified class entry in Public_classes.
		constructor:
	Public_classes:
		m
	"""
	def m(self) -> int:
		return 1
