from __future__ import annotations

from typing import Final


class X_CPVAR_010:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| demonstrate that annotated fields can satisfy CPVAR-005.
		constructor:
			default
	Public_variables:
		my_fancy_field:
			Annotated field
	"""
	my_fancy_field: int
