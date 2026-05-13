from __future__ import annotations

# Example
def factorial(n: int) -> int:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Definitions, Contract, Parameters, Returns, Raises, See_also
		status:
			stable
		scope:
			public
	Definitions:
		ExampleTerm:
			...
	Terminology:
		Example term:
			...
	Contract:
		general:
			|Must| define the externally visible behavior of this callable.
		invariants:
			|Must| preserve all documented invariants across valid calls.
		requires:
			|Must| define preconditions for valid input.
		ensures:
			|Must| define postconditions for successful execution.
	Description:
		...
	Parameters:
		n:
			...
	Returns:
		|Must| return ...
	Raises:
		BaseException:
			|Must| raise if...
	Notes:
		General note:
			...
	See_also:
	"""
	if not isinstance(n, int):
		raise TypeError("factorial: n must be an int")
	if n < 0:
		raise ValueError("factorial: n must be >= 0")
	if n > _MAX_N:
		raise OverflowError(f"factorial: n must be <= {_MAX_N}")

	# Deterministic iterative implementation
	result = 1
	for k in range(2, n + 1):
		result *= k
	return result
