class X_01:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Notes
	Contract:
		general:
			|Must| demonstrate pasing an validation failure in the Notes section.
		constructor:
			default
	Notes:
		Must not be normative:
			But is, which is incorrect.
	"""

class X_02:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract 
	Contract:
		general:
			|Must| demonstrate pasing an validation failure in the Notes section.
		constructor:
			default
	Notes:
		Bad note:
			We |should_not| have a note like this one.
	"""

class X_03:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract 
	Contract:
		general:
			|Must| demonstrate pasing an validation failure in the Notes section.
		constructor:
			default
	Notes:
		Bad note:
			Illegal subsection:
				Don't do this.
	"""

class X_04:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract 
	Contract:
		general:
			|Must| demonstrate pasing an validation failure in the Notes section.
		constructor:
			default
	Notes:
		:
			Empty label
	"""

class X_05:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract 
	Contract:
		general:
			|Must| demonstrate pasing an validation failure in the Notes section.
		constructor:
			default
	Notes:
		Empty content:
	"""
