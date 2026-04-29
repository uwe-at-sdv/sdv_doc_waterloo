"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| provide an example class.
Public_classes:
	MyClass
Class_overview:
	MyClass:
		An empty class
"""
class MyClass:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| provide nothing.
		constructor:
			|Must| be default-constructible.
	"""
	pass


