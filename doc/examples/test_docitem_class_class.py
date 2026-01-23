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
	api:
		Public_classes
Public_methods:
	greeting:
		A simple test method.
Public_classes:
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
		Contract
		Public_methods
Contract:
	general:
		A class, nested in class :wtrl_type:`X`, |must| do nothing.
	constructor:
		|Must| be default-constructible
	api:
		Public_methods
Public_methods:
		"""
		pass
