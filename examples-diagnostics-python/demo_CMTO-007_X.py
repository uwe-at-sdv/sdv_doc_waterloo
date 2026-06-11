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
			|Must| define a method overview.
		constructor:
	Public_methods:
		m
	Method_overview:
		m:
			|Must| be a public method.
	"""
	def m(self) -> int:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Returns
		Contract:
			general:
				|Must| return a value.
		Returns:
			1
		"""
		return 1
