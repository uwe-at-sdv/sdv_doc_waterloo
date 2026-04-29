from __future__ import annotations

from types import ModuleType


def _mk_module(name: str, doc: str) -> ModuleType:
	m = ModuleType(name)
	m.__doc__ = doc
	return m


# ---------------------------------------------------------------------------
# MCLO: Class_overview (module profile)
# ---------------------------------------------------------------------------

M_MCLO_002 = _mk_module(
	"M_MCLO_002",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Class_overview
Contract:
	general:
		|Must| trigger MCLO-002.
Public_classes:
	X
Class_overview:
	X:
		A class
""",
)
setattr(M_MCLO_002, "X", type("X", (), {}))


M_MCLO_003 = _mk_module(
	"M_MCLO_003",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| trigger MCLO-003.
Class_overview:
	X:
		A class
""",
)
setattr(M_MCLO_003, "X", type("X", (), {}))


M_MCLO_005 = _mk_module(
	"M_MCLO_005",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| trigger MCLO-005.
Public_classes:
	X
Class_overview:
	not_@_good_name:
		Bad identifier
""",
)
setattr(M_MCLO_005, "X", type("X", (), {}))


M_MCLO_006 = _mk_module(
	"M_MCLO_006",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| trigger MCLO-006.
Public_classes:
	X
Class_overview:
	X:
		Unallowed_subsection:
			Not allowed
""",
)
setattr(M_MCLO_006, "X", type("X", (), {}))


M_MCLO_007 = _mk_module(
	"M_MCLO_007",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| trigger MCLO-007.
Public_classes:
	X
Class_overview:
	X:
		|Must| be listed.
""",
)
setattr(M_MCLO_007, "X", type("X", (), {}))


M_MCLO_008 = _mk_module(
	"M_MCLO_008",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| trigger MCLO-008.
Public_classes:
Class_overview:
	X:
		Not resolvable
""",
)


M_MCLO_009 = _mk_module(
	"M_MCLO_009",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| trigger MCLO-009.
Public_classes:
	Y
Class_overview:
	X:
		Not a class object
""",
)


def _x_not_class() -> None:
	pass


setattr(M_MCLO_009, "X", _x_not_class)
setattr(M_MCLO_009, "Y", type("Y", (), {}))


M_MCLO_011 = _mk_module(
	"M_MCLO_011",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| trigger MCLO-011.
Public_classes:
	Y
Class_overview:
	X:
		Not listed in Public_classes
""",
)
setattr(M_MCLO_011, "X", type("X", (), {}))
setattr(M_MCLO_011, "Y", type("Y", (), {}))


# ---------------------------------------------------------------------------
# MFNO: Function_overview (module profile)
# ---------------------------------------------------------------------------

M_MFNO_002 = _mk_module(
	"M_MFNO_002",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions, Function_overview
Contract:
	general:
		|Must| trigger MFNO-002.
Public_functions:
	f
Function_overview:
	f:
		A function
""",
)


def _f_ok() -> None:
	pass


setattr(M_MFNO_002, "f", _f_ok)


M_MFNO_003 = _mk_module(
	"M_MFNO_003",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| trigger MFNO-003.
Function_overview:
	f:
		A function
""",
)
setattr(M_MFNO_003, "f", _f_ok)


M_MFNO_005 = _mk_module(
	"M_MFNO_005",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| trigger MFNO-005.
Public_functions:
	f
Function_overview:
	not good:
		Bad identifier
""",
)
setattr(M_MFNO_005, "f", _f_ok)


M_MFNO_006 = _mk_module(
	"M_MFNO_006",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| trigger MFNO-006.
Public_functions:
	f
Function_overview:
	f:
		Unallowed_subsection:
			Not allowed
""",
)
setattr(M_MFNO_006, "f", _f_ok)


M_MFNO_007 = _mk_module(
	"M_MFNO_007",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| trigger MFNO-007.
Public_functions:
	f
Function_overview:
	f:
		|Must| be listed.
""",
)
setattr(M_MFNO_007, "f", _f_ok)


M_MFNO_008 = _mk_module(
	"M_MFNO_008",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| trigger MFNO-008.
Public_functions:
Function_overview:
	f:
		Not resolvable
""",
)


M_MFNO_009 = _mk_module(
	"M_MFNO_009",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| trigger MFNO-009.
Public_functions:
	g
Function_overview:
	f:
		Not a function
""",
)
setattr(M_MFNO_009, "f", type("X", (), {}))
setattr(M_MFNO_009, "g", _f_ok)


M_MFNO_011 = _mk_module(
	"M_MFNO_011",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| trigger MFNO-011.
Public_functions:
	g
Function_overview:
	f:
		Not listed in Public_functions
""",
)


def _g_ok() -> None:
	pass


setattr(M_MFNO_011, "f", _f_ok)
setattr(M_MFNO_011, "g", _g_ok)
