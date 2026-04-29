
class A:
	class B:
		u : int = 0
		class C:
			def c_method(self) -> None:
				pass
			@staticmethod
			def c_staticmethod() -> None:
				pass
			@classmethod
			def c_classmethod(cls) -> None:
				pass
		def b_method(self) -> None:
			pass
	def a_method(self) -> None:
		pass
def z() -> None:
	class Z:
		pass
	pass
