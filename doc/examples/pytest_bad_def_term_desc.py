#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py

class B_00:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Definitions
Definitions:
	Malformed_missing_colon
	"""
	pass
class B_01:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Definitions
Definitions:
	Not+an+identifier:
	"""
	pass

class B_02:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Definitions
Contract:
	general:
	constructor:
Definitions:
	Def_item:
	"""
	pass

class B_03:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
	constructor:
Terminology:
	A Term:
	"""
	pass

class B_04:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
	constructor:
Description:
	No_subsection_allowed:
		Illegal subsection
	"""
	pass

