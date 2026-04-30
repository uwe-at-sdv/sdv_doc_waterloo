from __future__ import annotations

from typing_extensions import Self


def f() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger nothing.
	Parameters:
	Returns:
		|None|
	Raises:
	"""
	pass


def f_RET_001() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Raises
	Contract:
		general:
			|Must| trigger RET-001.
	Parameters:
	Raises:
	"""
	pass


def f_RET_002() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Raises
	Contract:
		general:
			|Must| trigger RET-002.
	Parameters:
	Returns:
		|None|
	Raises:
	"""
	pass


def f_RET_004(flag: bool) -> bool:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RET-004 as warning.
	Parameters:
		flag:
			Some condition.
	Returns:
		Boolean indicator of success.
	Raises:
	"""
	return flag


def f_RET_005() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RET-005.
	Parameters:
	Returns:
		result:
			Not allowed subsection.
	Raises:
	"""
	pass


def f_RET_006() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RET-006 as warning.
	Parameters:
	Returns:
		None
	Raises:
	"""
	pass


def f_RET_007() -> Self:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RET-007 as warning.
	Parameters:
	Returns:
		Returns self.
	Raises:
	"""
	raise RuntimeError("not executed in tests")
