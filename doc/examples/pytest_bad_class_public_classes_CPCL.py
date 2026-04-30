# Works normally
class X_00:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger nothing in validation.
			|Must| trigger CPCL-007 in coverage.
		constructor:
			default
	Public_classes:
		Y
	"""
	class Y:
		"""
		"""


class X_01:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger CPCL-002 in validation.
		constructor:
			default
	Public_classes:
		Y
	"""
	class Y:
		pass

class X_02:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CPCL-004 in validation.
		constructor:
			default
	Public_classes:
		Y
	"""

class X_03:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CPCL-005 in validation.
		constructor:
			default
	Public_classes:
		Y
	"""
	def Y() -> None:
		pass

class X_04:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CPCL-006 in coverage.
		constructor:
			default
	Public_classes:
	"""
	class Y:
		"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract
		Contract:
			general:
				|Must| do nothing.
			constructor:
				default
		"""


		
