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
			|Must| contain a class overview entry that is not a class.
		constructor:
	Public_classes:
		Y
	Class_overview:
		m:
			|Must| be a public class in the class docstring.
	"""
	class Y:
		pass

	def m(self) -> int:
		return 1
