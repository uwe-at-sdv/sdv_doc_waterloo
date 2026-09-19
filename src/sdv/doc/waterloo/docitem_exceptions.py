#===== Exceptions =============================================#

class ParseError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class ValidationError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class SectionNotFoundError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class SubsectionNotFoundError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class NoContentError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
