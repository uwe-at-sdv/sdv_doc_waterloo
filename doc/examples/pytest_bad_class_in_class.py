#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

# ./waterlint.py coverage --obj pytest_bad_class_in_class -> Error (validate_module_class_coverage)
"""
Preamble:	
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| demonstrate nested classes.
Class_overview:
	X_00:
		An outer class
	X_01:
		Another outer class
	X_02:
		Another outer class
Public_classes:
	X_00
	X_01
	X_02
	X_03
	X_04
"""

# ./waterlint.py coverage --obj pytest_bad_class_in_class.X_00 -> Error (validate_class_class_coverage)
class X_00:
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
Class_overview:
	Y:
		The inner class
Public_classes:
	Y
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
Class_overview:
	Z_nodoc:
		Has no docstring
Public_classes:
	Z_nodoc
		"""
		class Z_nodoc:
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


# ./waterlint.py validate --obj pytest_bad_class_in_class.X_01			-> Ok
# ./waterlint.py validate --obj pytest_bad_class_in_class.X_01.Y_not_listed	-> Ok
# ./waterlint.py coverage --obj pytest_bad_class_in_class.X_01			-> Warning (validate_class_class_coverage)
class X_01:
	"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
		|Must| represent the outer class.
	constructor:
		|Must| be default-constructible
	"""
	class Y_not_listed:
		"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
		|Must| represent an inner class.
	constructor:
		|Must| be default-constructible
		"""

# ./waterlint.py validate --obj pytest_bad_class_in_class.X_02				-> Ok
# ./waterlint.py validate --obj pytest_bad_class_in_class.X_02.Y_not_listed_bad_doc	-> Error
# ./waterlint.py validate --obj pytest_bad_class_in_class.X_02.Y_not_listed_no_doc	-> Error
# ./waterlint.py coverage --obj pytest_bad_class_in_class.X_02				-> Ok (validate_class_class_coverage)
class X_02:
	"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
		|Must| represent the outer class.
	constructor:
		|Must| be default-constructible
	"""
# The class has no waterloo docstring but it is not listed
# so this should be none of our business in coverage of X_02.
	class Y_not_listed_bad_doc:
		"""
Some random docstring format
		"""
# Similar, no docstring but not listed -> not a problem.
	class Y_not_listed_no_doc:
		pass

# ./waterlint.py coverage --obj pytest_bad_class_in_class.X_03 -> Error (validate_class_method_coverage)
class X_03:
	"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract, Public_methods
Contract:
	general:
		|Must| represent the outer class.
	constructor:
		|Must| be default-constructible
Method_overview:
	f_listed_bad_doc:
		Method with invalid docstring
Public_methods:
	f_listed_bad_doc
	"""
	def f_listed_bad_doc(self) -> None:
		"""
Some random docstring format
		"""

# ./waterlint.py coverage --obj pytest_bad_class_in_class.X_04 -> Warning (validate_class_method_coverage)
class X_04:
	"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
		|Must| represent the outer class.
	constructor:
		|Must| be default-constructible
	"""
	def f_not_listed_valid(self) -> None:
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

# ./waterlint.py coverage --obj pytest_bad_class_in_class.X_05 -> Error (validate_class_method_coverage)
class X_05:
	"""
Preamble:	
	profile:
		class
	normative_sections:
		Contract, Public_methods
Contract:
	general:
		|Must| represent the outer class.
	constructor:
		|Must| be default-constructible
Method_overview:
	f_listed_no_doc:
		Method with missing docstring
Public_methods:
	f_listed_no_doc
	"""
	def f_listed_no_doc(self) -> None:
		pass
