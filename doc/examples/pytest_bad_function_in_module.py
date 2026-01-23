#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

# ./waterlint.py validate --obj pytest_bad_function_in_module -> Ok	(coverage not validated)
# ./waterlint.py coverage --obj pytest_bad_function_in_module -> Error	(validate_module_function_coverage, 2 errors)
"""
Preamble:	
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must_not| demonstrate nested classes.
Public_functions:
	f_not_listed_bad_doc:
		A function with invalid docstring
"""

def f_not_listed_bad_doc() -> None:
	"""
Some random docstring format
	"""	
