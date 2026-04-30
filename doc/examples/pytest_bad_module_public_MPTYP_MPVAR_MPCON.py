from __future__ import annotations

from types import ModuleType


def _mk_module(name: str, doc: str) -> ModuleType:
	m = ModuleType(name)
	m.__doc__ = doc
	return m


M_MPTYP_002 = _mk_module(
	"M_MPTYP_002",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| trigger MPTYP-002 (validate).
Public_types:
""",
)


M_MPTYP_004 = _mk_module(
	"M_MPTYP_004",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_types
Contract:
	general:
		|Must| trigger MPTYP-004 (validate).
Public_types:
	MyF@ncyType:
		Bad identifier
""",
)


M_MPTYP_005 = _mk_module(
	"M_MPTYP_005",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_types
Contract:
	general:
		|Must| trigger MPTYP-005 (validate).
Public_types:
	MyFancyType:
		Not resolvable
""",
)


M_MPTYP_006 = _mk_module(
	"M_MPTYP_006",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_types
Contract:
	general:
		|Must| trigger MPTYP-006 (validate).
Public_types:
	MyFancyType:
		Unallowed_subsection:
			Not allowed
""",
)
setattr(M_MPTYP_006, "MyFancyType", int)


M_MPTYP_008 = _mk_module(
	"M_MPTYP_008",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_types
Contract:
	general:
		|Must| trigger MPTYP-008 (validate).
Public_types:
	MyFancyType:
		Not a type alias
""",
)


class _NotAlias:
	pass


setattr(M_MPTYP_008, "MyFancyType", _NotAlias)


M_MPVAR_002 = _mk_module(
	"M_MPVAR_002",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| trigger MPVAR-002 (validate).
Public_variables:
""",
)


M_MPVAR_004 = _mk_module(
	"M_MPVAR_004",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_variables
Contract:
	general:
		|Must| trigger MPVAR-004 (validate).
Public_variables:
	my_f@ncy_var:
		Bad identifier
""",
)


M_MPVAR_005 = _mk_module(
	"M_MPVAR_005",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_variables
Contract:
	general:
		|Must| trigger MPVAR-005 (validate).
Public_variables:
	my_fancy_var:
		Not resolvable
""",
)


M_MPVAR_006 = _mk_module(
	"M_MPVAR_006",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_variables
Contract:
	general:
		|Must| trigger MPVAR-006 (validate).
Public_variables:
	my_fancy_var:
		Unallowed_subsection:
			Not allowed
""",
)
setattr(M_MPVAR_006, "my_fancy_var", "abc")


M_MPVAR_008 = _mk_module(
	"M_MPVAR_008",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_variables
Contract:
	general:
		|Must| trigger MPVAR-008 (validate).
Public_variables:
	my_fancy_var:
		Not a named value
""",
)


def _my_fancy_var() -> None:
	pass


setattr(M_MPVAR_008, "my_fancy_var", _my_fancy_var)


M_MPCON_002 = _mk_module(
	"M_MPCON_002",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| trigger MPCON-002 (validate).
Public_constants:
""",
)


M_MPCON_004 = _mk_module(
	"M_MPCON_004",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_constants
Contract:
	general:
		|Must| trigger MPCON-004 (validate).
Public_constants:
	my_f@ncy_con:
		Bad identifier
""",
)


M_MPCON_005 = _mk_module(
	"M_MPCON_005",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_constants
Contract:
	general:
		|Must| trigger MPCON-005 (validate).
Public_constants:
	my_fancy_con:
		Not resolvable
""",
)


M_MPCON_006 = _mk_module(
	"M_MPCON_006",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_constants
Contract:
	general:
		|Must| trigger MPCON-006 (validate).
Public_constants:
	my_fancy_con:
		Annotated but not Final
""",
)
setattr(M_MPCON_006, "my_fancy_con", "abc")
M_MPCON_006.__annotations__ = {"my_fancy_con": str}


M_MPCON_007 = _mk_module(
	"M_MPCON_007",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_constants
Contract:
	general:
		|Must| trigger MPCON-007 (validate).
Public_constants:
	my_fancy_con:
		Unallowed_subsection:
			Not allowed
""",
)
setattr(M_MPCON_007, "my_fancy_con", "abc")


M_MPCON_009 = _mk_module(
	"M_MPCON_009",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_constants
Contract:
	general:
		|Must| trigger MPCON-009 (validate).
Public_constants:
	my_fancy_con:
		Not a named value
""",
)


def _my_fancy_con() -> None:
	pass


setattr(M_MPCON_009, "my_fancy_con", _my_fancy_con)
