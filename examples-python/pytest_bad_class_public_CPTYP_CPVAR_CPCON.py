from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger nothing.
		constructor:
			default
	"""
class X_CPTYP_002:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger CPTYP-002 (validate).
		constructor:
			default
	Public_types:
	"""
class X_CPTYP_004:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types
	Contract:
		general:
			|Must| trigger CPTYP-004 (validate).
		constructor:
			default
	Public_types:
		MyF@ncyType:
			Has bad name
	"""
class X_CPTYP_005:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types
	Contract:
		general:
			|Must| trigger CPTYP-005 (validate).
		constructor:
			default
	Public_types:
		MyFancyType:
			A type alias
	"""
class X_CPTYP_006:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types
	Contract:
		general:
			|Must| trigger CPTYP-006 (validate).
		constructor:
			default
	Public_types:
		MyFancyType:
			Unallowed_subsection:
				Not allowed
	"""
	class MyFancyType:
		pass
class X_CPTYP_008:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types
	Contract:
		general:
			|Must| trigger CPTYP-008 (validate).
		constructor:
			default
	Public_types:
		MyFancyType:
			A type alias
	"""
	class MyFancyType:
		pass

class X_CPVAR_002:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger CPVAR-002 (validate).
		constructor:
			default
	Public_variables:
	"""
class X_CPVAR_004:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| trigger CPVAR-004 (validate).
		constructor:
			default
	Public_variables:
		my_f@ncy_var:
			Has bad name
	"""
class X_CPVAR_005:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| trigger CPVAR-005 (validate).
		constructor:
			default
	Public_variables:
		my_fancy_var:
			Not resolvable
	"""
class X_CPVAR_006:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| trigger CPVAR-006 (validate).
		constructor:
			default
	Public_variables:
		my_fancy_var:
			Unallowed_subsection:
				Not allowed
	"""
class X_CPVAR_008:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| trigger CPVAR-008 (validate).
		constructor:
			default
	Public_variables:
		my_fancy_var:
			Not a variable
	"""
	def my_fancy_var() -> None:
		pass
class X_CPCON_002:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger CPCON-002 (validate).
		constructor:
			default
	Public_constants:
	"""
class X_CPCON_004:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
	Contract:
		general:
			|Must| trigger CPCON-004 (validate).
		constructor:
			default
	Public_constants:
		my_f@ncy_con:
			Has bad name
	"""
class X_CPCON_005:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
	Contract:
		general:
			|Must| trigger CPCON-005 (validate).
		constructor:
			default
	Public_constants:
		my_fancy_con:
			Not resolvable
	"""
class X_CPCON_007:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
	Contract:
		general:
			|Must| trigger CPCON-007 (validate).
		constructor:
			default
	Public_constants:
		my_fancy_con:
			Unallowed_subsection:
				Not allowed
	"""
class X_CPCON_009:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
	Contract:
		general:
			|Must| trigger CPCON-009 (validate).
		constructor:
			default
	Public_constants:
		my_fancy_con:
			Not a constant
	"""
	def my_fancy_con() -> None:
		pass

class X_CPCON_006:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
	Contract:
		general:
			|Must| trigger CPCON-006 (validate).
		constructor:
			default
	Public_constants:
		my_fancy_con:
			Not a constant
	"""
	my_fancy_con: str = "abc"
