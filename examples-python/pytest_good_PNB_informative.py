#!/usr/bin/env python3
r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions
Contract:
	general:
		|Must| use tokenized normativity keyword form.
Public_classes:
	X
Public_functions:
	f
Class_overview:
	X:
		This class must be described informatively.
Function_overview:
	f:
		This function should be described informatively.
"""

class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| use tokenized normativity keyword form.
		constructor:
	"""

def f() -> None:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Raises, Returns
	Contract:
		general:
			|Must| use tokenized normativity keyword form.
	Parameters:
	Raises:
	Returns:
		|None|
	"""
	pass
