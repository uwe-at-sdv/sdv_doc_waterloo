from typing import Any, Dict, Final, TypeAlias

# A base class which becomes part of the API.
class MyBaseClass:
	pass

# A private base class which prefer not o propagate as API.
class MyOtherBaseClass:
	pass

class MyClass(MyBaseClass,MyOtherBaseClass):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Definitions, Derived_from, Public_classes,
			Public_methods, Public_types, Public_variables, Public_constants
	Definitions:
		MyExampleItem:
			Define a term normatively. Same as for modules.
	Terminology:
		Fancy-Unicorn:
			Define a term informatively. Same as for modules.
	Contract:
		general:
			|Must| demonstrate the minimal class docstring.
		constructor:
			|Must| demand an int-valued positional parameter 'a'.
			|Must| demand a str-valued positional or keyword parameter 'b'.
			|Must| accept a float-valued positional or keyword parameter 'c'.
			|Must| demand a bool-valued keyword parameter 'd'.
			|Must| accept (variadic) keyword parameters and dispatch them as follows:
			|Must| accept a keyword parameter 'e' and assert it is str-valued (if present).
			The constructor |must| print all parameter values to 'stdout'.
		traits:
			final
	Derived_from:
		MyBaseClass
	Description:
		As for modules
	Notes:
		Purpose and Syntax:
			Same as for modules
	Public_classes:
		MyNestedClass
	Class_overview:
		MyNestedClass:
			Use this section for informative reminders what the class\
			is good for.
			Multiple lines are possible. Do not use Normativity Keywords.
	Public_methods:
		my_method
	Method_overview:
		my_method:
			Important for demonstration but does nothing
	Public_types:
		MyTypeAlias_t:
			Important type for annotations
	Public_variables:
		my_variable:
			A variable
	Public_constants:
		MY_CONSTANT:
			Another constant
	See_also:
		test_docitem_module_minimal
	"""

	class MyNestedClass:
		pass

	MyTypeAlias_t: TypeAlias = float | int

	my_variable: MyTypeAlias_t = 123

	MY_CONSTANT: Final[str] = "hello"

	def __init__(self, a: int, /, b: str, c: float = 1.23, *, d: bool, **kwargs: Any) -> None:
		# 'a' is positional-only
		# 'b' and 'c' are positional or keyword
		# 'd' is keyword-only
		
		print(a, b, c, d, kwargs)
		
		# Validation of 'e' from variadic parameters
		if "e" in kwargs:
			assert isinstance(kwargs["e"], str), "Parameter 'e' must be a string"
	def my_method(self, q : MyTypeAlias_t) -> None:
		pass

if __name__ == "__main__":
	m = MyClass(1,"hi",2.34,e="xyz",d=False)
	m = MyClass(2,"hi",3.45,e="yzx",d=False)
	m = MyClass(3,c=4.56,b="hi",d=True,e="zxy")
