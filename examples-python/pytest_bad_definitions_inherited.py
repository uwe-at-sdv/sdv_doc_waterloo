r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions
Contract:
	general:
		|Must| provide a |label|`Definitions` section for demonstartion purposes.
Definitions:
	Term_A:
		|term|`Term_A` is an important thing.
	Term_B:
		|term|`Term_B` is another important thing.
	Term_Z:
		|term|`Term_Z` is surprisingly unimportant.
"""

class X_term_not_in_module:
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
		Term_C:
			|term|`Term_C` is like |term|`Term_A` but different.
		Term_D:
			|term|`Term_D` is like |term|`Term_B` but different.
		_inherit:
			Term_A,Term_B
			Term_Z, Term_Y_does_not_exist
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
				|Must| refer to |term|`Term_Z` inherited here,\
				but defined at module level.
		Definitions:
			_inherit:
				Term_Z
		Parameters:
		Returns:
			|None|
		Raises:
		"""

class X_duplicate_term:
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
		Term_C:
			|term|`Term_C` is like |term|`Term_A` but different.
		Term_D:
			|term|`Term_D` is like |term|`Term_B` but different.
		_inherit:
			Term_A,Term_B
			Term_Z,Term_B
	"""

class X_duplicate_inherited:
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
		Term_C:
			|term|`Term_C` is like |term|`Term_A` but different.
		Term_D:
			|term|`Term_D` is like |term|`Term_B` but different.
		_inherit:
			Term_A,Term_B
		_inherit:
			Term_Z
	"""

class X_term_not_an_identifier:
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
		Term_C:
			|term|`Term_C` is like |term|`Term_A` but different.
		Term_D:
			|term|`Term_D` is like |term|`Term_B` but different.
		_inherit:
			Term_@_not_an_identifier
	"""

class X_term_redefined:
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
		Term_C:
			|term|`Term_C` is like |term|`Term_A` but different.
		Term_Z:
			|term|`Term_Z` is like |term|`Term_B` but different.
		_inherit:
			Term_A,Term_B,Term_Z
	"""

