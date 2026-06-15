#!/usr/bin/env python3

r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| demonstrate inherited definition items with a direct module that lacks Definitions.
"""

class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Definitions
	Contract:
		general:
			|Must| demonstrate inherited definition items.
		constructor:
			default
	Definitions:
		_inherit:
			Term_A
	"""
