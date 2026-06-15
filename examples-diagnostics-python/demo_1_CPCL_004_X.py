#!/usr/bin/env python3
"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Public_classes
	scope:
		public
Contract:
	general:
		|Must| provide a demo for CPCL-004.
Public_classes:
	MissingClass
"""
class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes, Public_methods
		scope:
			public
	Contract:
		general:
			|Must| be minimal.
		constructor:
			|Must| be default-constructible.
	Public_classes:
		MissingClass
	Public_methods:
		m
	"""
	def m(self) -> None:
		pass
