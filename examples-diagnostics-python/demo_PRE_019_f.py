#!/usr/bin/env python3

"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| demonstrate PRE-019 for a function.
"""

import sys

sys.modules.setdefault("demo_PRE_019_f", sys.modules[__name__])


def f() -> None:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate PRE-019.
	"""
	pass
