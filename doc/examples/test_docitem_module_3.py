"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes
Contract:
	general:
		|Must| provide an example class.
Public_classes:
	MyClass:
		An empty class
"""
class MyClass:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| provide nothing.
		constructor:
			|Must| be default-constructible.
	Public_methods:
		greeting:
			Function which prints a greeting.
	"""
	def greeting(self) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| render a greeting message to ``stdout``.
		Parameters:
		Returns:
			|Must| return |None|
		Raises:
		"""
		print("Hello world!")


