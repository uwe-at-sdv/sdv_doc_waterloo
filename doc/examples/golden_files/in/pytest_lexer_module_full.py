r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions, Public_classes, Public_functions
		Public_types, Public_variables, Public_constants
Definitions:
	MyItem:
		This is a term named |term|`MyItem` in section "Definitions".
		This section is always normative and |must| be listed
		in "normative_sections". You can refer to this term by using the
		syntax token "|" + term + "|" followed by the referred term in
		backticks. Any validator will ensure that the terms you refer to
		by this token are defined in section "Definitions".
	My_Other_Item:
		Here is another example. Note that term names are Identifiers
		like variable names in most programming languages, restricted to
		letters, digits, and underscore.
Terminology:
	Fancy-Unicorn:
		The section "Terminology" allows to define terms in an informative
		manner. Typically, this subsection would start like
		"A Fancy-Unicorn is ..." followed by an explanation.
		The section "Terminology" is never normative, never listed
		in "normative_sections" and does not contain normativity keywords
		in tokenized form. As opposed to section "Definitions", any non-empty
		string is allowed, like here "Fancy-Unicorn".
		Take care, however, that the name does not collide with syntax rules
		of the intermediate document language (like reST in our case).
	
Contract:
	general:
		|Must| demonstrate all sections and subsection\
		and syntax tokens like backslash for continued lines.
		|Must| point out that logical lines are interpreted\
		as items, so here we have two logical lines, i.e. two items.
		This docstring |may| refer to |term|`MyItem` for demonstration purposes.
Description:
	The purpose of this module is to demonstrate waterloo docstrings
	on module level. A linter will accept this docstring, but
	coverage is not given, because the classes and function mentioned
	herein do not have docstrings. The example also demonstrates the
	role |class|`MyClass` for class names.
	|
	The section "Description" allows free form text and the usage of
	the pipe character "|" in order to subdivide the text into paragraphs.
	|
	A section "Description" may be normative, but in this example it is not,
	since it does not contain normativity keywords in tokenized form.
Notes:
	What is it good for:
		Section "Notes" allows you to add informative content.
	What it is not good for:
		The section is never normative, it is never listed in
		"normative_sections" and it must not contain normativity
		keywords in tokenized form.
	Syntax:
		The section "Notes" is subdivided into subsections with
		user-defined labels like in this example "What is it good for:",
		"What it is not good for:" and "Syntax:"
Public_classes:
	MyClass
Class_overview:
	MyClass:
		Class for nothing
Public_functions:
	my_function
Function_overview:
	my_function:
		Important for demonstration but does nothing
Public_types:
	MyTypeAlias_t:
		|Must| represent a union of :wtrl_type:`float` and :wtrl_type:`int`.\
		This section is always normative. All relevant information about the\
		type alias is specified here, as type aliases do not provide their own\
		machine-verifiable docstrings.
Public_variables:
	my_variable:
		|Must| represent a value for this and that.\
		This section is always normative. All relevant information is specified\
		here, since variables do not have standardized, machine-verifiable\
		docstrings.
Public_constants:
	MY_CONSTANT:
		|Must| represent a constant value annotated as :wtrl_type:`Final`.\
		This section is always normative. All relevant information is specified\
		here, as constants do not provide their own machine-verifiable\
		docstrings.
		
See_also:
	test_docitem_module_minimal
"""

from typing import Final, TypeAlias

class MyClass:
	pass

def my_function() -> None:
	pass

MyTypeAlias_t: TypeAlias = float | int

my_variable : MyTypeAlias_t = 1.2345

MY_CONSTANT : Final[int] = 42
