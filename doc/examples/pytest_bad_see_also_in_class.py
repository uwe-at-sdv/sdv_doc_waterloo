import math

class A_no_docstring:
	pass
class A_invalid_docstring:
	"""
	Not a waterloo docstring
	"""

class X_00:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate an unresolvable "See_also".
			|Must_not| list "See_also" as normative.
		constructor:
			|Must| be default-constructible.
	See_also:
		math.not_a_function
	"""
	pass

class X_01:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate a "See_also" reference without docstring.
			|Must_not| list "See_also" as normative.
		constructor:
			|Must| be default-constructible.
	See_also:
		A_no_docstring
	"""
	pass

class X_02:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate a "See_also" reference with invalid docstring.
			|Must_not| list "See_also" as normative.
		constructor:
			|Must| be default-constructible.
	See_also:
		A_invalid_docstring
	"""
	pass

class X_03:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, See_also
	Contract:
		general:
			|Must| demonstrate an unresolvable "See_also" while :wtrl_label:`See_also` is normative.
		constructor:
			|Must| be default-constructible.
	See_also:
		math.not_a_function
	"""
	pass

class X_04:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, See_also
	Contract:
		general:
			|Must| demonstrate a "See_also" reference without docstring while :wtrl_label:`See_also` is normative.
		constructor:
			|Must| be default-constructible.
	See_also:
		A_no_docstring
	"""
	pass

class X_05:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, See_also
	Contract:
		general:
			|Must| demonstrate a "See_also" reference with invalid docstring while :wtrl_label:`See_also` is normative.
		constructor:
			|Must| be default-constructible.
	See_also:
		A_invalid_docstring
	"""
	pass
