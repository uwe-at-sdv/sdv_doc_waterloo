def normalize_identifier(name: str) -> str:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| normalize a user-provided identifier to a canonical Waterloo Identifier form.
	requires:
		|Must| be passed a non-empty string.
	ensures:
		|Must| return a string that matches the Identifier pattern :wtrl_lit:`[a-zA-Z_][a-zA-Z0-9_]*`.
		|Must| return a value that is semantically equivalent to the input name under the tool's normalization policy.
	invariants:
		|Must| be idempotent: normalize_identifier(normalize_identifier(name)) == normalize_identifier(name).
		|Must| be deterministic: repeated calls with equal input return equal output.
Parameters:
	name:
		Input identifier string.
Returns:
	|Must| return the canonical identifier.
Raises:
	"""
