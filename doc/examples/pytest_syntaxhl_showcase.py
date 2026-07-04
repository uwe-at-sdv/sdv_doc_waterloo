r"""
Preamble:
	profile:
		module
	scope:
		core, nonexistent
	status:
		frozen
	normative_sections:
		Contract, Definitions, Parameters, BadSection, See_also
	bad_subsection:
		Content
Definitions:
	Identifier:
		A string matching the regex |lit|`[a-zA-Z_][a-zA-Z0-9_]*`.
	_inherit:
		Term_A, Term_B
	bad term
		bad because colon is missing and it doesn't follow the identifier format.
Terminology:
	Un!corn:
		Fancy animal. Test roles: |mod|`ABC`
Bad Section:
	All sections are predefined, and "Bad Section" is not one of them.
Contract:
	general:
		|Must| do this and that. Test roles: |term|`ABC`
		|Should_not| do other things. Test roles: |term|`ABC`
		|ref|`label <target_in_rst>`
		|ref|`label <wtrl://qi.of.documented.object>`
		|ref|`label <https://link.com>`
	constructor:
		default - this is freeform text describing the constructor contract.
		Test roles: |func|`__init__`
	requires:
		|var|`x` > 0. Test roles: |var|`x`
	ensures:
		The result is positive. Test roles: |value|`positive`
	invariants:
		Idempotent. Test roles: |term|`idempotent`
	traits:
		abstract
	base:
		MyBaseClassA, MyBaseClassB
	bad_subsection:
		Contract only contains predefined subsections,\
		and "bad_subsection" is not one of them.
Description:
	This is a logical line consisting of two\
	physical lines.
	|
	This is another logical line. Test roles: |label|`ABC`
Derived_from:
	MyBaseClassA, MyBaseClassB
Factory:
	my_factory:
		Each entry in this section describes a factory function.\
		The entry name is the name of the factory function,\
		and the content is freeform text describing the factory contract.
Public_classes:
	ClassOne, ClassTwo
Class_overview:
	class_one:
		Brief description of class one. Test roles: |type|`class_one`
	class_two:
		Brief description of class two. Test roles: |type|`class_two`
Public_functions:
	function_one, function_two
Function_overview:
	function_one:
		Brief description of function one. Test roles: |func|`function_one`
	function_two:
		Brief description of function two. Test roles: |func|`function_two`
Public_methods:
	method_one, method_two
Method_overview:
	method_one:
		Brief description of method one. Test roles: |func|`method_one`
	method_two:
		Brief description of method two. Test roles: |func|`method_two`
Public_types:
	type_one:
		Description of type one. Test roles: |type|`type_one`
	type_two:
		Description of type two. Test roles: |type|`type_two`
Public_variables:
	VAR_ONE:
		Description of variable one. Test roles: |value|`1`
	VAR_TWO:
		Description of variable two. Test roles: |value|`2`
Public_constants:
	CONST_ONE:
		Description of constant one. Test roles: |value|`1`
	CONST_TWO:
		Description of constant two. Test roles: |value|`2`
Parameters:
	x:
		Description of parameter x. Test roles: |var|`x`
	y:
		Description of parameter y. Test roles: |var|`y`
	not a par:
		Invalid because it doesn't follow the identifier format\
		and cannot be used as a parameter name.
Returns:
	|Must| return |Self|, due to fluent interface. Test roles: |type|`ABC`
Raises:
	ValueError:
		|Must| raise if the input is invalid. Test roles: |type|`ValueError`
	CustomError:
		|May| propagate from function |func|`some_function`. Test roles: |type|`CustomError`.
Notes:
	Roles:
		* |attr|`ABC` — |lit|`|attr|`, for attributes in XML, keys in JSON...
		* |class|`ABC` — |lit|`|class|`, classes
		* |cmd|`ABC` — |lit|`|cmd|`, commands and subcommand with CLI
		* |dfn|`ABC` — |lit|`|dfn|`, a term being defined
		* |file|`/path/to/ABC` — |lit|`|file|`, files but also URLs
		* |func|`ABC` — |lit|`|func|`, functions
		* |key|`CTRL` — |lit|`|label|`, keys on the keyboard
		* |label|`ABC` — |lit|`|label|`, titles, labels
		* |lit|`ABC` — |lit|`|lit|`, catch-all for literal text
		* |mod|`ABC` — |lit|`|mod|`, modules
		* |norm|`should` — |lit|`|norm|`, normativity keywords (meta, when talking about keywords)
		* |op|`>>` — |lit|`|op|`, operators
		* |opt|`--abc` — |lit|`|opt|`, options for CLI commands
		* |pkg|`sdv.tty` — |lit|`|pkg|`, packages
		* |tag|`ABC` — |lit|`|tag|`, enum values, symbolic values
		* |term|`ABC` — |lit|`|term|`, referencing a term defined in |label|`Definitions`
		* |type|`float` — |lit|`|type|`, types in programming or markup languages
		* |url|`https://pypi.org/project/sdv-doc-waterloo/` — |lit|`|url|`, for URLs (currently pretty simple)
		* |value|`12345` — |lit|`|value|`, R-values, unnamed values
		* |var|`xyz` — |lit|`|var|`, variables, but also named constants
		* |var_type|`xyz:float` — |lit|`|var_type|`, variable and type with colon.
	Todo at 2026-06-25:
		Implement 'pkg' for 'package' as opposed to importable module.
See_also:
	other.class, other.function
"""
import sys

class MyClassA:
	"""
	Preamble:
		profile:
			class
		scope:
			core
	Notes:
		Not a docstring:
			Missing Contract - Testing edge case in pygemnts lexer.
	"""

class MyClassB:
	def __init__(self):
# Trying to confuse the lexer with a string which is not a valid docstring.
		a = "Preamble:\n\tprofile:\n\t\tfunction\nContract:\n"

def bar():
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
	Parameters:
	Returns:
	Raises:
	"""
	pass

#----- Pygments Lexer edge cases -----------------------------#

def foo_no_preamble(a: int) -> float:
	"""
	Notes:
		Not a valid docstring:
			The content looks like a docstring but has no Preamble.
	Returns:
		float: The input converted to a float.
	"""
	return float(a)

def foo_no_contract(a: int) -> float:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Notes:
		Not a valid docstring:
			The content looks like a docstring but has no Contract.
	Returns:
		float: The input converted to a float.
	"""
	return float(a)

def foo_mixed_indent(a: int) -> float:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| provide a test case with mixed indentation
			(tabs and spaces) in the Contract section.
	Notes:
		Not a valid docstring:
		    This line is indented with spaces, while
			the previous line is indented with a tab.
			This is valid in Python (because it's inside
			a docstring) but invalid as a docstring
			according to the waterloo specification.
	Returns:
		float: The input converted to a float.
	"""
	return float(a)

def foo_empty_lines(a: int) -> float:
	"""
	Preamble:   
		profile:
			function
		normative_sections:
			Contract, Parameters
			
			Returns, Raises
	Contract:
		general:
			|Must| provide a test case with empty lines in CSV-like sections.
			Tools |must| accept these empty lines as part of the section content.
			|Must| provide a test for deliberately inserted whitespace in
			ref-directives, which should be preserved as part of the content.
			|Must| provide a test for semantics roles not defined in waterloo.
			|Must| provide a test for linesline connectors followed by whitespace.
	Notes:
		Trailing whitespace in Section labels:
			"Preamble:" in this docstring has trailing spaces,
			which should be ignored when parsing the section label.
		Testing ref:
			|ref|`label < target_in_rst>`
			|ref|` label <wtrl://qi.of.documented.object>`
			|ref|`label <https://link.com> `
			|ref|`label https://link.com`
			|ref|`label`
		Testing undefined roles:
			|my_fancy_role|`some content` <- should be treated as literal text, not a role.
			|not_valid| <- should be treated as literal text, not a role.
		Testing line connectors with whitespace:
			This is a line with a connector at the end, followed by three spaces. \\   
			This is the continuation of the previous line.
	Returns:
		float: The input converted to a float.
	"""
	return float(a)

def foo_state_leak_a():
	"""
	Not a waterloo docstring
	"""
def foo_state_leak_b():
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| provide test cases for state leak between functions.
	"""
def foo_state_leak_c():
	"""
	Not a waterloo docstring
	"""


#----- VSCode generateDocstring edge cases -------------------#

def func_with_comment_edgecase() -> None: # todo
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| provide an edge case for an inline comment in the function signature.
	Parameters:
	Returns:
		|None|
	Raises:
	Notes:
		Edge case:
			The function signature contains an inline comment,
			which should not interfere with synthesizing a function
			definition by appending "pass".
	"""
	pass
