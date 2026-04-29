# Works normally in validate; should trigger CPMT-007 in coverage.
class X_00:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger nothing in validation.
			|Must| trigger CPMT-007 in coverage.
		constructor:
			default
	Public_methods:
		m
	"""
	def m(self) -> None:
		"""
		"""


class X_01:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger CPMT-002 in validation.
		constructor:
			default
	Public_methods:
		m
	"""
	def m(self) -> None:
		pass


class X_02:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CPMT-004 in validation.
		constructor:
			default
	Public_methods:
		m
	"""


class X_03:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CPMT-005 in validation.
		constructor:
			default
	Public_methods:
		m
	"""
	class m:
		pass


class X_04:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CPMT-006 in coverage.
		constructor:
			default
	Public_methods:
	"""
	def m(self) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| do nothing.
		Parameters:
		Returns:
			|None|
		Raises:
		"""
		return None

