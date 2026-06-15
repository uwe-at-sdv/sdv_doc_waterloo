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
			|Must| define a nested class overview.
		constructor:
	Public_classes:
		Y
	Class_overview:
		Y:
			|Must| be a nested public class.
	"""
	class Y:
		"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract
		Contract:
			general:
				|Must| be the nested class.
			constructor:
		"""
		pass
