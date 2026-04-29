"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
	scope:
		core
Contract:
	general:
		|Must| demonstrate a violation of the Scope Monotonicity Rule.
Public_classes:
	X_extension
"""

class X_extension:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
		scope:
			extension
	Contract:
		general:
			|Must| demonstrate a violation of the Scope Monotonicity Rule.
		constructor:
			|Must| be default-constructible.
	Public_methods:
		f_public
	"""

	def f_public(self) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
			scope:
				public
		Contract:
			general:
				|Must| do nothing.
				|Must| be public.
		Parameters:
		Returns:
			|None|
		Raises:
		"""
		pass
	def f(self) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
			scope:
				extension
		Contract:
			general:
				|Must| do nothing.
		Parameters:
		Returns:
			|None|
		Raises:
		"""
		pass

class Y_public(X_extension):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from, Public_methods
		scope:
			public
	Contract:
		general:
			|Must| demonstrate a violation of the Scope Monotonicity Rule.
		constructor:
			|Must| be default-constructible.
	Derived_from:
		X_extension
	Public_methods:
		f
	"""
	def f(self) -> None:
		"""
		Preamble:
			profile:
				inherited_method
			normative_sections:
				Contract
			scope:
				public
		Contract:
			general:
				|Must| do nothing.
			base:
				pytest_bad_scope.X_extension.f
		"""
		pass
	def f_bad_scope(self) -> None:
		"""
		Preamble:
			profile:
				inherited_method
			normative_sections:
				Contract
			scope:
				not_a_valid_scope
		Contract:
			general:
				|Must| do nothing.
			base:
				pytest_bad_scope.X_extension.f
		"""
		pass
	
