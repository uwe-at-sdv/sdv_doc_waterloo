r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions, Public_classes, Public_functions,
		Public_types, Public_variables, Public_constants 
Contract:
	general:
Description:
	We test several freeform and bullet-list scenarios. A |label|`Description` section
	is freeform content. A single pipe character "|" separates paragraphs
	within the freeform text.
	|
	This is the second paragraph. Here is an enumeration:
	# Item 1
	# Item 2
Definitions:
	Term_A:
		Definition content is freeform  A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		This is the second paragraph. Here is an enumeration
		# Numbered item with long text, so that we use \
		the backslash in order to create a logical line.
		# Numbered item
Terminology:
	Term B:
		Terminology content is freeform. A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		This is the second paragraph. Here is an item list:
		* Item 1
		* Item 2
		Some text after the item list.
Notes:
	About:
		Notes content is freeform. A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		This is the second paragraph. Here is an item list:
		* Item 1
		* Item 2
		Some text after the item list.
Public_classes:
	X
Public_functions:
	f
Class_overview:
	X:
		A class overview is not normative. The content
		is a sequence of paragraphs.
		|
		This is the second paragraph. A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		Itemizations and enumerations are possible:
		* An item
		# Numbered item
		# Numbered item
		* An item
Function_overview:
	f:
		A function overview is not normative. The content
		is a sequence of paragraphs.
		|
		This is the second paragraph. A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		Itemizations and enumerations are possible:
		# Numbered item
		* An item
		* An item
		# Numbered item
Public_types:
	MyType:
		|label|`Public_types` is normative. The content
		is a sequence of paragraphs.
		This is the second paragraph. A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		Itemizations and enumerations are possible:
		# Numbered item
		* An item
		* An item
		# Numbered item
Public_variables:
	my_variable:
		|label|`Public_variables` is normative. The content
		is a sequence of paragraphs.
		This is the second paragraph. A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		Itemizations and enumerations are possible:
		# Numbered item
		* An item
		* An item
		# Numbered item
Public_constants:
	my_constant:
		|label|`Public_constants` is normative. The content
		is a sequence of paragraphs.
		This is the second paragraph. A single pipe character "|" separates paragraphs
		within the freeform text.
		|
		Itemizations and enumerations are possible:
		* An item
		+ A subitem
		- A subsubitem
		- A subsubitem
		+ A subitem
		* An item
"""

from __future__ import annotations
from typing import Final, List, Tuple, TypeAlias

MyType: TypeAlias = Tuple[int,float]
my_variable: str = ""
my_constant: Final[str] = ""

class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Factory, Public_methods
	Contract:
		general:
			Subsections in |label|`Contract` are line-based. This is\
			the first logical line. Use backslash to merge physical lines\
			to a logical line.
			This is the second logical line. Itemization is not supported\
			inside these logical lines.
			A sequence of logical lines in the contract is meant to represent\
			a line-by-line executable contract.
		constructor:
			Same format as |label|`Contract.general`.
			This is the second logical line.
	Factory:
		make_X:
			Line-based text flow is enforced as in |label|`Contract`.\
			Use backslash to merge physical lines to a logical line.
			This is the second logical line. Factories are not so different\
			from constructors in terms of documentation. The content\
			is interpreted as a line-by-line executable contract.
	Public_methods:
		m
	Method_overview:
		m:
			A method overview is not normative. The content
			is a sequence of paragraphs.
			|
			This is the second paragraph. A single pipe character "|" separates paragraphs
			within the freeform text.
			|
			Itemizations and enumerations are possible:
			# Numbered item
			* An item
			* An item
			# Numbered item
	"""
	def m(self) -> None:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
		Parameters:
		Returns:
		Raises:
		"""
		pass

def make_X() -> X:
	pass

def f(rng: Tuple[int,int],b: str) -> Tuple[float,int,List[str]]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			Same format as for profile |value|`class`.
			Second line.
		requires:
			Same format as |label|`Contract.general`
			Second line.
		ensures:
			Same format as |label|`Contract.general`
			Second line.
		invariants:
			Same format as |label|`Contract.general`
			Second line.
	Returns:
		As opposed to the |label|`Contract` sections,
		the |label|`Return` section is intepreted as a freeform text.
		A single pipe character "|" separates paragraphs within the freeform text.
		|
		The free form allows us to itemize and enumerate. We can use this in
		order to describe the structure of the returned value, e.g.
		|
		The returned value has the form |var|`(u,v,[r,s])` where
		* |var|`u` is ...
		* |var|`v` is ...
		* |var|`[r,s]` consist of the following:
		+ |var|`r` which is ...
		+ |var|`s` which is ...
	Parameters:
		rng:
			Like the |label|`Returns` section, parameter entries support
			freeform text with itemization and enumeration, which allows
			to resolve the inner structure of parameters. Example
			* Component |value|`0` is the beginning of the range.
			* Component |value|`1` is the (eclusive) end of the range.
		b:
			Nonetheless, line-by-line executable contract style is
			possible by explicit itemization:
			* |Must| represent ...
			* |Must| fulfill ...
			This may overlap with the |label|`requires` section.
			In case of a thematic overlap, a detailed |label|`requires` section
			should be preferred.
	Raises:
	"""
	pass
