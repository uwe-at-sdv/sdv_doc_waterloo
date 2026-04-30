r"""
Preamble:
	profile:
		module
	normative_sections:
		Definitions, Contract
Definitions:
	Mod_Term_A, Mod_Term_A_var:
		Definition of |term|`Mod_Term_A` and a variation `Mod_Term_A_var`.
Contract:
	general:
"""

class X_01:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Definitions, Contract
	Definitions:
		Term_A:
			Definition of |term|`Term_A`.
		Term_B:
			Illegal_subsection:
				Not allowed
	Contract:
		general:
			|Must| demonstrate bad definition: `Term_B` has an illegal subsection, which is not allowed in a Definitions section.
		constructor:
			default
	"""
class X_02:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| demonstrate bad terminology: `Term_D` has an illegal subsection, which is not allowed in a Terminology section.
		constructor:
			default
	Terminology:
		Term C:
			Some informative explanation.
		Term D:
			Illegal_subsection:
				Not allowed
	"""
class X_03:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Definitions, Contract
	Definitions:
		Term_A:
			Definition of |term|`Term_A`.
		Term_A:
			Duplicate not allowed
	Contract:
		general:
			|Must| demonstrate bad definition: duplicate definition of `Term_A`.
		constructor:
			default
	"""
class X_04_PRSR_002:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Definitions, Contract
	Definitions:
		Term_A, Term_B, Term_A:
			Definition of |term|`Term_A` and `Term_B`.
	Contract:
		general:
			|Must| demonstrate a bad Definitions section: double definition of `Term_A`.
		constructor:
	"""
class X_05_DEF_018:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Definitions, Contract
	Definitions:
		_inherit:
			Mod_Term_A, Mod_Term_A_var
	Contract:
		general:
			|Must| demonstrate bad inheritance: Mod_Term_A_var is a variation of Mod_Term_A, so it cannot be inherited.
			Only terms can be inherited, not variations.
		constructor:
	"""
class X_06_LQID_004:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Definitions, Contract
	Definitions:
		_inherit:
			Mod_Term_A, Mod_Term_A
	Contract:
		general:
			|Must| demonstrate bad inheritance: Mod_Term_A is being inherited twice, which is not allowed.
		constructor:
	"""
class X_07:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Definitions, Contract
	Definitions:
		Term_A:
			Definition of |dfn|`Term_A`.
	Terminology:
		Term_A:
			Illegal repetition of `Term_A` in Terminology section.
	Contract:
		general:
			|Must| demonstrate bad terminology: `Term_A` is defined in the Definitions section, so it cannot be repeated in the Terminology section.
		constructor:
			default
	"""
