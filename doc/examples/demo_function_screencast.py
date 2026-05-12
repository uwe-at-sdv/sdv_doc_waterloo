from __future__ import annotations

# Example
def factorial(n: int) -> int:
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
