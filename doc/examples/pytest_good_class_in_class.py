#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

"""
Preamble:	
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must_not| demonstrate nested classes.
Public_classes:
	X
Class_overview:
	X:
		The outer class
"""

class X:
	"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| represent the outer class.
	constructor:
		|Must| be default-constructible
Public_classes:
	Y
Class_overview:
	Y:
		The inner class
	"""
	class Y:
		"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| represent an inner class.
	constructor:
		|Must| be default-constructible
Public_classes:
	Z
Class_overview:
	Z:
		The innermost class
		"""
		class Z:
			"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract, Public_methods
Contract:
	general:
		|Must| represent an inner class.
	constructor:
		|Must| be default-constructible
Public_methods:
	spam
Method_overview:
	spam:
		Does nothing
			"""
			def spam() -> None:
				"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must_not| do anything
Parameters:
Returns:
	|None|
Raises:
				"""
	pass

