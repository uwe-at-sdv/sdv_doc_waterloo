#!/usr/bin/env python3

r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions
Contract:
	general:
		|Must| demonstrate inherited definition items.
Definitions:
	Term_A:
		Definition of |term|`Term_A`.
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
		Term_A:
			Definition of |term|`Term_A` in the class itself.
		_inherit:
			Term_A
	"""
