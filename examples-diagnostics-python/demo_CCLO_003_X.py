"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| contain a class demo.
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
			|Must| define a class overview.
		constructor:
	Class_overview:
		Y:
			|Must| be a public class in the class docstring.
	"""
	pass
