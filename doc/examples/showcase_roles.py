r"""
Preamble:
	profile:
		module
	scope:
		core
	normative_sections:
		Contract, Definitions
Definitions:
	ABC:
		A term |dfn|`ABC` we reference by role |lit|`|term|`.
Contract:
	general:
		|Must| do — "|" + |lit|`Must` + "|"
		|must| do — "|" + |lit|`must` + "|"
		|Must_not| do — "|" + |lit|`Must_not` + "|"
		|must_not| do — "|" + |lit|`must_not` + "|"
		|Should| do — "|" + |lit|`Should` + "|"
		|should| do — "|" + |lit|`should` + "|"
		|Should_not| do — "|" + |lit|`Should_not` + "|"
		|should_not| do — "|" + |lit|`should_not` + "|"
		|May| do — "|" + |lit|`May` + "|"
		|may| do — "|" + |lit|`may` + "|"
Notes:
	Flavour:
		Normativity keywords are rendered in flavour |value|`rfc-2119` in this showcase, i.e. capitalized.
	Roles:
		* |attr|`ABC` — |lit|`|attr|`, for attributes in XML, keys in JSON...
		* |cmd|`ABC` — |lit|`|cmd|`, commands and subcommand with CLI
		* |dfn|`ABC` — |lit|`|dfn|`, a term being defined
		* |file|`/path/to/ABC` — |lit|`|file|`, files but also URLs
		* |func|`ABC` — |lit|`|func|`, functions
		* |key|`CTRL` — |lit|`|label|`, keys on the keyboard
		* |label|`ABC` — |lit|`|label|`, titles, labels
		* |lit|`ABC` — |lit|`|lit|`, catch-all for literal text
		* |mod|`ABC` — |lit|`|mod|`, modules
		* |norm|`should` — |lit|`|norm|`, normativity keywords (meta, when talking about keywords)
		* |op|`>>` — |lit|`|op|`, operators
		* |opt|`--abc` — |lit|`|opt|`, options for CLI commands
		* |pkg|`sdv.tty` — |lit|`|pkg|`, packages
		* |tag|`ABC` — |lit|`|tag|`, enum values, symbolic values
		* |term|`ABC` — |lit|`|term|`, referencing a term defined in |label|`Definitions`
		* |type|`float` — |lit|`|type|`, types in programming or markup languages
		* |url|`https://pypi.org/project/sdv-doc-waterloo/` — |lit|`|url|`, for URLs (currently pretty simple)
		* |value|`12345` — |lit|`|value|`, R-values, unnamed values
		* |var|`xyz` — |lit|`|var|`, variables, but also named constants
		* |var_type|`xyz:float` — |lit|`|var_type|`, variable and type with colon.
	Values:
		* |Self| — |lit|`|Self|`
		* |None| — |lit|`|None|`
		* |True| — |lit|`|True|`
		* |False| — |lit|`|False|`
	Todo at 2026-06-25:
		Styles for pkg and url required.
"""

class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Definitions
	Contract:
		general:
			|Must| demonstrate the use of |lit|`|term|` in a class.
		constructor:
	Definitions:
		_inherit:
			ABC
	Notes:
		Roles:
			* |term|`ABC` — |lit|`|term|`, referencing a term defined in |label|`Definitions`
		Compound examples:
			|cmd|`waterlint validate` |opt|`--basedir` |file|`/path/to/dir` |opt|`--obj` |mod|`mymod`
	"""
	pass
