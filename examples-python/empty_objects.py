# This file is required for Pytests for waterlint commands
# gen-minimal and gen-full. Adapt and run Pytests after editing!

class EmptyClass:
	pass

def empty_function(a: int,b: str) -> None:
	pass

class X:
	class EmptySubclass:
		pass
	class Y:
		"""Some non-Waterloo-Docstring"""
		# Non-documentable by docstring
		# (but documentable in Y->Public_variables)
		q: int = 42

		def method_in_subclass(self,a: float,b: bool) -> None:
			# Non-documentable because does not exist in global scope.
			def non_documentable_function() -> None:
				pass
			class NonDocumentabelClass:
				pass
	def empty_method(self,a: int,b: str) -> None:
		pass
	@staticmethod
	def f() -> None:
		"""Some non-Waterloo-Docstring"""
		
