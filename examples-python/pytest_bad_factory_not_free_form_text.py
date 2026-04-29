from __future__ import annotations

class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods, Factory
	Contract:
		general:
			|Must| provide an example for a factory.
		constructor:
			default
	Factory:
		X.from_int:
			|Must| create an instance and set member variable |var|`_q`.
		make_X:
			Illegal_subsection:
				|Must| create an instance.
	Public_methods:
		from_int
	"""
	def __init__(self) -> None:
		self._q: int = 0

	@classmethod
	def from_int(cls, q: int) -> X:
		x = X()
		x._q = q
		return x


def make_X() -> X:
	return X()
