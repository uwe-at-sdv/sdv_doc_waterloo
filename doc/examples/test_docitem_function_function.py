"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| serve spam and eggs.
	
"""

def spam() -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns
	Contract:
		general:
			|Must| do nothing.
	Parameters:
	Returns:
		|Must| return |None|
	Raises:
	"""
	def eggs() -> None:
		"""
		Preamble:
			profile:
				function
			normative_sections:
				Contract, Returns
		Contract:
			general:
				|Must| do nothing.
		Parameters:
		Returns:
			|Must| return |None|
		Raises:
		"""
		pass
	eggs()
