import inspect

class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| provide a property for demonstration purposes.
		constructor:
			default
	Public_variables:
		value:
			A property object providing controlled access to an internal value.
	"""
	def __init__(self):
		self._value: int = 5
	@property
	def value(self) -> int:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| provide the implementation of the getter of property |var|`self.value`.
		Parameters:
		Returns:
			|Must| return the current value of the property.
		Raises:
		"""
		print("getter invoked")
		return self._value
	@value.setter
	def value(self,v: int) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| provide the implementation of the setter of property |var|`self.value`.
		Parameters:
			v:
				Value to set.
		Returns:
			|None|
		Raises:
		"""
		print("setter invoked")
		self._value = v

if __name__ == "__main__":
	x = X()
	print(x.value)
	x.value = 7
	print(x.value)

	prop = inspect.getattr_static(X, "value")
	print(prop)
	print(prop.fget)
	print(prop.fget(X()))
	print(prop.fget.__name__)
	print(prop.fset)
	print(prop.fset(X(),7))
