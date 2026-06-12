"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| contain a function overview entry that is not a function.
Public_functions:
	f
Function_overview:
	X:
		|Must| be a public function in the module.
"""

class X:
	pass

def f() -> int:
	return 1
