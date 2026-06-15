#!/usr/bin/env python3

r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_types
Contract:
	general:
		|Must| demonstrate that Public_types entries must be TypeAlias or NewType.
Public_types:
	MyFancyType:
		Not a type alias
"""

class _NotAlias:
	pass


MyFancyType = _NotAlias
