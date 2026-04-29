class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must_not| trigger anything.
		constructor:
			default
	Public_methods:
		m
	Method_overview:
		m:
			A method
	"""
	def m(self) -> None:
		pass
	
class X_CMTO_002:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods, Method_overview
	Contract:
		general:
			|Must| trigger CMTO-002.
		constructor:
			default
	Public_methods:
		m
	Method_overview:
		m:
			A method
	"""
	def m(self) -> None:
		pass
	
class X_CMTO_003:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger CMTO-003.
		constructor:
			default
	Method_overview:
		m:
			A method
	"""
	def m(self) -> None:
		pass
	
class X_CMTO_005:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CMTO-005.
		constructor:
			default
	Public_methods:
		m
	Method_overview:
		not_@_good_name:
			Bad name
	"""
	def m(self) -> None:
		pass
class X_CMTO_006:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CMTO-006.
		constructor:
			default
	Public_methods:
		m
	Method_overview:
		m:
			Unallowed_subsection:
				Not allowed
	"""
	def m(self) -> None:
		pass
class X_CMTO_007:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CMTO-007.
		constructor:
			default
	Public_methods:
		m
	Method_overview:
		m:
			|Must| not contain any Normativity Keyword.
	"""
	def m(self) -> None:
		pass
class X_CMTO_008:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CMTO-008.
		constructor:
			default
	Public_methods:
	Method_overview:
		m:
			Not resolvable
	"""

class X_CMTO_009:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CMTO-009.
		constructor:
			default
	Public_methods:
	Method_overview:
		m:
			Not a method
	"""
	m: str = "abc"
class X_CMTO_011:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| trigger CMTO-011.
		constructor:
			default
	Public_methods:
	Method_overview:
		m:
			Not in Public_methods
	"""
	def m(self) -> None:
		pass


class X_CCLO_002:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes, Class_overview
	Contract:
		general:
			|Must| trigger CCLO-002.
		constructor:
			default
	Public_classes:
		Y
	Class_overview:
		Y:
			A nested class
	"""
	class Y:
		pass


class X_CCLO_003:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| trigger CCLO-003.
		constructor:
			default
	Class_overview:
		Y:
			A nested class
	"""
	class Y:
		pass

class X_CCLO_005:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CCLO-005.
		constructor:
			default
	Public_classes:
		Y
	Class_overview:
		not_@_good_name:
			Bad name
	"""
	class Y:
		pass


class X_CCLO_006:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CCLO-006.
		constructor:
			default
	Public_classes:
		Y
	Class_overview:
		Y:
			Unallowed_subsection:
				Not allowed
	"""
	class Y:
		pass


class X_CCLO_007:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CCLO-007.
		constructor:
			default
	Public_classes:
		Y
	Class_overview:
		Y:
			|Must| not contain any Normativity Keyword.
	"""
	class Y:
		pass


class X_CCLO_008:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CCLO-008.
		constructor:
			default
	Public_classes:
	Class_overview:
		Y:
			Not resolvable
	"""


class X_CCLO_009:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CCLO-009.
		constructor:
			default
	Public_classes:
	Class_overview:
		Y:
			Not a class
	"""
	Y: str = "abc"

class X_CCLO_011:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes
	Contract:
		general:
			|Must| trigger CMTO-011.
		constructor:
			default
	Public_classes:
	Class_overview:
		Y:
			Not in Public_classes
	"""
	class Y:
		pass
