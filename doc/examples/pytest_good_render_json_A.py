from __future__ import annotations
from typing import TypeAlias,Final

from pytest_good_render_json_B import *
import pytest_good_render_json_C


class A:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types, Public_variables, Public_constants
		scope:
			public
	Contract:
		general:
			|Must| represent a class in an API module.
		constructor:
			|Must| be default-constructible
	Public_types:
		ClassTypeA_t:
			A type alias.
			Line two of docstring.
	Public_variables:
		class_var_a:
			A variable.
	Public_constants:
		class_const_a:
			A variable.
	"""
	ClassTypeA_t: TypeAlias = int
	class_var_a: ClassTypeA_t = 5
	class_const_a: Final[ClassTypeA_t] = 5

def spam_a() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| represent a function in a public module.
	Parameters:
	Returns:
		None
	Raises:
	"""
