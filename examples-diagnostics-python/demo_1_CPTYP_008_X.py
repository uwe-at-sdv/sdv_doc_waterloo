#!/usr/bin/env python3

class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types
	Contract:
		general:
			|Must| demonstrate that Public_types entries must be TypeAlias or NewType.
		constructor:
			default
	Public_types:
		MyFancyType:
			Not a type alias
	"""
	class MyFancyType:
		pass

