
class B:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
		constructor:
	"""
	pass

class X:
	class B:
		r"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract
		Contract:
			general:
			constructor:
		"""
		pass
	class Y:
		class B:
			r"""
			Preamble:
				profile:
					class
				normative_sections:
					Contract
			Contract:
				general:
				constructor:
			"""
			pass
		class Z:
			r"""
			Preamble:
				profile:
					class
				normative_sections:
					Contract
			Contract:
				general:
				constructor:
			"""
			class B:
				r"""
				Preamble:
					profile:
						class
					normative_sections:
						Contract
				Contract:
					general:
					constructor:
				"""
				pass

class Y(B,X.B,X.Y.B,X.Y.Z.B):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from
	Contract:
		general:
		constructor:
	Derived_from:
		test_docitem_derived_from_mro.B, X.B, X.Y.B, X.Y.Z.B
	"""
	pass

class Z(B, X.B):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from
	Contract:
		general:
		constructor:
	Derived_from:
		X.Y.Z.B
	"""
	pass
