#!/usr/bin/env python3
"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Public_methods
	scope:
		public
Contract:
	general:
		|Must| provide a demo for CPMT-004.
Public_methods:
	MissingMethod
"""
class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
		scope:
			public
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	Public_methods:
		MissingMethod
	"""
	def m(self) -> None:
		pass
