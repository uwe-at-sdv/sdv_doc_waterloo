from __future__ import annotations
from enum import Enum,IntEnum
from types import FunctionType, MappingProxyType, ModuleType
from typing_extensions import Self, TypeIs
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, Literal, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

# Intentionally not derived from BaseException.
class MyException:
	pass

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

def f_RAI_001() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns
	Contract:
		general:
			|Must| trigger RAI-001.
	Parameters:
	Returns:
		|None|
	"""
	pass

def f_RAI_002() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns
	Contract:
		general:
			|Must| trigger RAI-002.
	Parameters:
	Returns:
		|None|
	Raises:
	"""
	pass

def f_RAI_004() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RAI-004.
	Parameters:
	Returns:
		|None|
	Raises:
		MyFancyException:
			Does not exist.
	"""
	pass

def f_RAI_005() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RAI-005.
	Parameters:
	Returns:
		|None|
	Raises:
		MyFancyException:
			Unallowed_subsection:
				Not allowed
	"""
	pass

def f_RAI_007() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RAI-007.
	Parameters:
	Returns:
		|None|
	Raises:
		MyException:
			Not derived from BaseException.
	"""
	pass

def f_RAI_008() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger RAI-008.
	Parameters:
	Returns:
		|None|
	Raises:
		MyF_@_ncyException:
			Bad name
	"""
	pass
