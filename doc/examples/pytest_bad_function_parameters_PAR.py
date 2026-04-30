from __future__ import annotations
from enum import Enum,IntEnum
from types import FunctionType, MappingProxyType, ModuleType
from typing_extensions import Self, TypeIs
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, Literal, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

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

def f_PAR_001() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns, Raises
	Contract:
		general:
			|Must| trigger PAR-001.
	Returns:
		|None|
	Raises:
	"""
	pass

def f_PAR_002() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns, Raises
	Contract:
		general:
			|Must| trigger PAR-002.
	Parameters:
	Returns:
		|None|
	Raises:
	"""
	pass

def f_PAR_003(a: int, /, b: str, c: float = 1.23, *, d: bool, **kwargs: Any) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger nothing; positive test with different kinds of parameters.
	Parameters:
		a:
			A positional parameter
		b:
			A positional or keyword parameter
		c:
			A positional or keyword parameter with default value
		d:
			A keyword parameter
		kwargs:
			a map vor variadic arguments
	Returns:
		|None|
	Raises:
	"""
	pass

def f_PAR_004(a: int, /, b: str, c: float = 1.23, *, d: bool, **kwargs: Any) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger PAR-004.
	Parameters:
		a:
			A positional parameter
		b:
			A positional or keyword parameter
		d:
			A keyword parameter
		kwargs:
			a map vor variadic arguments
	Returns:
		|None|
	Raises:
	"""
	pass

def f_PAR_005(a: int, /, c: float = 1.23, *, d: bool, **kwargs: Any) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger PAR-005.
	Parameters:
		a:
			A positional parameter
		b:
			A positional or keyword parameter
		c:
			A positional or keyword parameter with default value
		d:
			A keyword parameter
		kwargs:
			a map vor variadic arguments
	Returns:
		|None|
	Raises:
	"""
	pass

def f_PAR_006(a: int, /, b: str, c: float = 1.23, *, d: bool, **kwargs: Any) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger PAR-006.
	Parameters:
		a:
			A positional parameter
		b:
			A positional or keyword parameter
		c:
			A positional or keyword parameter with default value
		not_@_parname:
			A keyword parameter
		kwargs:
			a map vor variadic arguments
	Returns:
		|None|
	Raises:
	"""
	pass

def f_PAR_007(a: int, /, b: str, c: float = 1.23, *, d: bool, **kwargs: Any) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| trigger PAR-007.
	Parameters:
		a:
			A positional parameter
		b:
			A positional or keyword parameter
		c:
			A positional or keyword parameter with default value
		d:
			A keyword parameter
		kwargs:
			Unallowed_subsection:
				Not allowed.
	Returns:
		|None|
	Raises:
	"""
	pass

