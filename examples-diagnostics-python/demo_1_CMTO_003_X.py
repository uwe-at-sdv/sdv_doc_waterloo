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
			Contract
	Contract:
		general:
			|Must| define a method overview.
		constructor:
	Method_overview:
		m:
			|Must| be a public method in the class.
	"""
	def m(self) -> int:
		return 1
