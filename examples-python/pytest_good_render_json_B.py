"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions, Public_types, Public_variables, Public_constants
	scope:
		extension
Contract:
	general:
		|Must| represent a well-documented internal module.
Public_classes:
	B
Public_functions:
	spam_b
Public_types:
	ModuleTypeB_t:
		A type alias
Public_variables:
	module_var_b:
		A variable
Public_constants:
	module_const_b:
		A constant
"""
# When rendered in JSON for scope "public", the module will appear
# in the TOC and it will be counted, but the entry in __WTRL_OBJECTS__
# is a stub. We cannot completely omit it, because it has public
# functions, but we can neither render it because it is marked non-public.

from __future__ import annotations
from typing import TypeAlias,Final

class B:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types, Public_variables, Public_constants
		scope:
			extension
	Contract:
		general:
			|Must| represent a class in an internal module.
		constructor:
			|Must| be default-constructible
	Public_types:
		ClassTypeB_t:
			A type alias
	Public_variables:
		class_var_b:
			A class variable
	Public_constants:
		class_const_b:
			A class constant
	"""
	ClassTypeB_t: TypeAlias = float
	class_var_b: ClassTypeB_t = 6.6
	class_const_b: Final[ClassTypeB_t] = 6.6

class B_no_doc:
	pass

class B_invalid:
	"""
	invalid
	"""

ModuleTypeB_t: TypeAlias = float
module_var_b: ModuleTypeB_t = 5.5
module_const_b: Final[ModuleTypeB_t] = 5.5


def spam_b() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| represent a function in an internal module.
	Parameters:
	Returns:
		|None|
	Raises:	
	"""
