#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

# ./waterlint.py validate --obj pytest_bad_class_in_module -> Ok	(coverage not validated)
# ./waterlint.py coverage --obj pytest_bad_class_in_module -> Error	(validate_module_class_coverage, 2 errors)
"""
Preamble:	
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must_not| demonstrate nested classes.
Class_overview:
	X_not_listed_bad_doc:
		A clas with invalid docstring
	X_not_listed_no_doc:
		A clas without docstring
Public_classes:
	X_not_listed_bad_doc
	X_not_listed_no_doc
"""

class X_not_listed_bad_doc:
	"""
Some random docstring format
	"""	
class X_not_listed_no_doc:
	pass
