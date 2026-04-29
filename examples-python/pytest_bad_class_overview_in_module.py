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
Class_overview:
	X_missing_public:
		Informative note about the class, but Public_classes is missing.
"""


class X_missing_public:
	"""A docstring for the class."""
	pass

