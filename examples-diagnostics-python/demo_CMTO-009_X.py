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
			|Must| contain a method overview entry that is not a method.
		constructor:
	Public_methods:
		m
	Method_overview:
		Y:
			|Must| be a public method in the class.
	"""
	class Y:
		pass

	def m(self) -> int:
		return 1
