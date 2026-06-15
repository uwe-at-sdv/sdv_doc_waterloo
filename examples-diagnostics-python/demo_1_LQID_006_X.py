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
			...
		constructor:
			...
	Public_methods:
		f1,f2
		f3,f4
	"""
	def f1() -> None:
		pass
	def f2() -> None:
		pass
	def fq1() -> None:
		pass
	def f4() -> None:
		pass
