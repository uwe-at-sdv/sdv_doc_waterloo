from __future__ import annotations
from typing import Final

_MAX_N: Final[int] = 20  # 20! fits into 64-bit signed; adjust as desired

def test() -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Description:
	By this function we test the See_also section in factorial.
	Since :trl_label:`See_also` is normative (in this case)
	the docstring in the referred object must be a valid Waterloo string.
Contract:
	general:
		|Must| do nothing.
Parameters:
Returns:
	|None|
Raises:
	"""

def factorial(n: int) -> int:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Definitions, Contract, Parameters, Returns, Raises, See_also

Definitions:
	factorial:
		For a non-negative integer n, factorial(n) is defined recursively by:
		factorial(0) = 1 and factorial(n) = n * factorial(n-1) for n > 0.
	positive:
		An integer x is called ``positive`` if x > 0.

Description:
	This function provides a simple, deterministic reference implementation.
	It is intended to demonstrate a full Waterloo function docstring with a
	clear contract and well-defined failure modes.

Terminology:
	recursion:
		The definition uses recursion; the implementation does not have to.

Contract:
	general:
		|Must| compute |term|`factorial` for the given argument.
		|Must| be thread-safe.
	requires:
		|var|`n` |must| be an integer.
		|var|`n` |must| be greater than or equal to 0.
		|var|`n` |must| be less than or equal to |var|`_MAX_N`.
	ensures:
		The return value |must| be an integer.
		If |var|`n` is 0, the result |must| be 1.
		If |var|`n` is greater than 0, the result |must| be |term|`positive`.
		The result |must| be divisible by |var|`n` for all |var|`n` > 0.

Parameters:
	n:
		Non-negative integer input.

Returns:
	The factorial value.

Raises:
	TypeError:
		|Must| raise if |var|`n` is not an |type|`int`.
	ValueError:
		|Must| raise if |var|`n` is negative.
	OverflowError:
		|Must| raise if |var|`n` is greater than |var|`_MAX_N`.
See_also:
	math.factorial, test
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
