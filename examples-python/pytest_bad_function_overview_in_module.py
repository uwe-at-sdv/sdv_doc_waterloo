#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must_not| demonstrate nested classes.
Function_overview:
	f_missing_public:
		Informative note about the function, but Public_functions is missing.
"""


def f_missing_public() -> None:
	"""A valid Waterloo docstring for the function."""
	pass

