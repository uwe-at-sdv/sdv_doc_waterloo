from __future__ import annotations

from types import ModuleType
from typing import Final


def _mk_module(name: str, doc: str) -> ModuleType:
	m = ModuleType(name)
	m.__doc__ = doc
	return m


M_MPVAR_010 = _mk_module(
	"M_MPVAR_010",
	"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_variables
Contract:
	general:
		|Must| demonstrate that annotated variables can satisfy MPVAR-005.
Public_variables:
	my_fancy_var:
		Annotated variable
""",
)
M_MPVAR_010.__annotations__ = {"my_fancy_var": int}
