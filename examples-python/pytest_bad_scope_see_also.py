# |must_not| validate
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
		|Must| provide See_also entries that violate scope monotonicity.
See_also:
	spam, eggs
"""

# must validate
def spam() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises, See_also
		scope:
			core
	Contract:
		general:
			|Must| be minimal.
	Parameters:
	Returns:
		|None|
	Raises:
	See_also:
		eggs
	"""
	pass

# |must_not| validate
def eggs() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises, See_also
		scope:
			extension
	Contract:
		general:
			|Must| be minimal.
	Parameters:
	Returns:
		|None|
	Raises:
	See_also:
		spam
	"""
	pass
