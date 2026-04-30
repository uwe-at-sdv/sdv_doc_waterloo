"""
Not a valid docstring
"""

from __future__ import annotations
from typing import TypeAlias,Final

class C:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types, Public_variables, Public_constants
		scope:
			core
	Contract:
		general:
			|Must| represent a class in an internal module.
		constructor:
			|Must| be default-constructible
	Public_types:
		ClassTypeC_t:
			A type alias
	Public_variables:
		class_var_c:
			A class variable
	Public_constants:
		class_const_c:
			A class constant
	"""
	ClassTypeC_t: TypeAlias = float
	class_var_c: ClassTypeC_t = 6.6
	class_const_c: Final[ClassTypeC_t] = 6.6

def spam_c_core() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			core
	Contract:
		general:
			|Must| represent a function in an internal module.
	Parameters:
	Returns:
		None
	
	"""

def spam_c_no_doc() -> None:
	pass

def spam_c_invalid() -> None:
	"""
	invalid
	"""

