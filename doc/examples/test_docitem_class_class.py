class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods, Public_classes
	Contract:
		general:
			|Must| provide a method for writing a greeting message.
		constructor:
			|Must| be default-constructible
	Public_methods:
		greeting
	Method_overview:
		greeting:
			A simple test method.
	Public_classes:
		Y
	Class_overview:
		Y:
			A nested class for testing purposes.
	"""
	def greeting(self):
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns,Raises
		Contract:
			general:
				|Must| render a greeting message to ``stdout``.
		Parameters:
		Returns:
			|None|
		Raises:
		"""
		print("Hello world!")
	class Y:
		"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract, Public_methods
		Contract:
			general:
				A class, nested in class :wtrl_type:`X`, |must| do nothing.
			constructor:
				|Must| be default-constructible
		Public_methods:
			greeting_but_in_Y
		"""
		def greeting_but_in_Y(self):
			"""
			Preamble:
				profile:
					method
				normative_sections:
					Contract, Parameters, Returns,Raises
			Contract:
				general:
					|Must| render a greeting message to ``stdout``.
			Parameters:
			Returns:
				|None|
			Raises:
			"""
			print("Hello world from Y!")
