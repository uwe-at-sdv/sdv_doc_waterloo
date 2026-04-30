"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| demonstrate bad value for profile.
Parameters:
Returns:
	|None|
Raises:
"""

class B:
	def spam(self) -> None:
		"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate bad value for profile.
		constructor:
			Bad profile
		"""
		pass
class X(B):
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| demonstrate bad value for profile.
	"""
	def spam(self) -> None:
		"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate bad value for profile.
		"""
		pass

def eggs() -> None:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate bad value for profile.
		constructor:
			Bad profile
	"""
	pass
