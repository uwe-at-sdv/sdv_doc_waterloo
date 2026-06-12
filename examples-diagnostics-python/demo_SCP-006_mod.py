"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, See_also
	scope:
		public
Contract:
	general:
		|Must| demonstrate a scope monotonicity violation for See_also.
See_also:
	spam
"""

def spam() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			core
	Contract:
		general:
			|Must| be minimal.
	Parameters:
	Returns:
		|None|
	Raises:
	"""
	pass
