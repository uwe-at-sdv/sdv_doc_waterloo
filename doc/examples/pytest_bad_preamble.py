#!/usr/bin/env python3
# This file is part of the pytest-suite. Do not modify without updating test_docitem_pytest.py
# Cases covered here are not always primarily preamble problems, but the preamble is always involved.
class A_00:
	"""
Preamble:
	"""
class A_00_0:
	"""
Not+an+identifier:
	"""
class A_01:
	"""
Preamble:
	profile:
	"""
class A_01_0:
	"""
Preamble:
	not+an+identifier:
	"""
class A_02:
	"""
Preamble:
	profile:
		nonsense
	"""
class A_03:
	"""
Preamble:
	profile:
		class#@$%
	"""
class A_04:
	"""
Preamble:
	profile:
		class
	"""
class A_05:
	"""
Preamble:
	profile:
		class
	normative_sections:
Contract:
	"""
class A_06:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Nonsense
	"""
class A_07:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Contract
Contract:
	"""
class A_08:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Terminology
Contract:
Terminology:
	"""
class A_09:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
Contract:
Description:
	|Must| be normative.
	"""
class A_10:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
Contract:
Definitions:
	"""
