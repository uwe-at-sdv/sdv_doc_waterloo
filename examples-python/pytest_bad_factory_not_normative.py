from __future__ import annotations

class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| provide an example for a factory.
		constructor:
			default
	Factory:
		X.from_int:
			|Must| create an instance and set member variable |var|`_q`.
		make_X:
			|Must| create an instance.
	Public_methods:
		from_int
	"""
	def __init__(self) -> None:
		self._q: int = 0

	@classmethod
	def from_int(cls, q: int) -> X:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| create an instance of |type|`X` and set |var|`_q` from |var|`q`.
		Parameters:
			q:
				The important number.
		Returns:
			The instance of |type|`X`.
		Raises:
		"""
		x = X()
		x._q = q
		return x


def make_X() -> X:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| create an instance of |type|`X`.
	Parameters:
	Returns:
		The instance of |type|`X`.
	Raises:
	"""
	return X()
