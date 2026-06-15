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
def f() -> int:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns
	Contract:
		general:
			|Must| work.
	Parameters:
		x:
			|Must| be documented.
	Returns:
		1
	"""
	return 1
