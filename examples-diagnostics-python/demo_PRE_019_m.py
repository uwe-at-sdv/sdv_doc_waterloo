#!/usr/bin/env python3

"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| demonstrate PRE-019 for a method.
"""

import sys

sys.modules.setdefault("demo_PRE_019_m", sys.modules[__name__])


class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| be minimal.
	Public_methods:
		m
	"""

	def m(self) -> None:
		"""
		Preamble:
			profile:
				module
			normative_sections:
				Contract
		Contract:
			general:
				|Must| demonstrate PRE-019.
		"""
		pass
