r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions
Contract:
	general:
		|Must| provide a |label|`Definitions` section for demonstration purposes.
Definitions:
	Identifier:
		A string that matches the regular expression |value|`[a-zA-Z_][a-zA-Z0-9_]*`
	Qualified_Identifier:
		A |term|`Qualified_Identifier` is a string formed by concatenating |term|`Identifier` values\
		separated by a dot.
	Term_Z:
		|term|`Term_Z` is another term inherited by objects in this module.
"""

class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Definitions
	Contract:
		general:
			|Must| demonstrate inherited definition items.
		constructor:
			default
	Definitions:
		Private_Identifier:
			A |term|`Private_Identifier` is an |term|`Identifier` that starts with a double underscore.
		_inherit:
			Identifier
			Term_Z
	"""
	def spam(self) -> None:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Definitions, Parameters, Returns, Raises
		Contract:
			general:
				|Must| demonstrate inherited definition items.
		Definitions:
			_inherit:
				Identifier,Qualified_Identifier
			Anchor:
				An |term|`Anchor` is a special string computed from a |term|`Qualified_Identifier`
				in the following way: 1. The |term|`Qualified_Identifier` is split into segments,
				where each segment is an |term|`Identifier`. 2. To each segment the string
				|value|`"<n>:"` is prepended where |var|`<n>` stands for the length of the segment.
				3. The results are concatenated with |value|`"-"` as separator.
				Example: The |term|`Anchor` of |value|`AAA.BB.C` is |value|`3:AAA-2:BB-1:C`.
		Parameters:
		Returns:
			|None|
		Raises:
		"""

