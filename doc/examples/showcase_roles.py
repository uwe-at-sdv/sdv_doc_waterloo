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
		|Must| do this and that. Test roles: |term|`ABC`
		|Should_not| do other things. Test roles: |term|`ABC`
Notes:
	Roles:
		* |attr|`ABC` — |lit|`|attr|`, for attributes in XML, keys in JSON...
		* |cmd|`ABC` — |lit|`|cmd|`, commands and subcommand with CLI
		* |dfn|`ABC` — |lit|`|dfn|`, a term being defined
		* |file|`/path/to/ABC` — |lit|`|file|`, files but also URLs
		* |func|`ABC` — |lit|`|func|`, functions
		* |label|`ABC` — |lit|`|label|`, titles, labels
		* |lit|`ABC` — |lit|`|lit|`, catch-all for literal text
		* |mod|`ABC` — |lit|`|mod|`, modules
		* |norm|`should` — |lit|`|norm|`, normativity keywords
		* |op|`>>` — |lit|`|op|`, operators
		* |opt|`--abc` — |lit|`|opt|`, options for CLI commands
		* |pkg|`sdv.tty` — |lit|`|pkg|`, packages
		* |tag|`ABC` — |lit|`|tag|`, enum values, symbolic values
		* |term|`ABC` — |lit|`|term|`, referencing a term defined in |label|`Definitions`
		* |type|`float` — |lit|`|type|`, types in programming or markup languages
		* |value|`12345` — |lit|`|value|`, R-values, unnamed values
		* |var|`xyz` — |lit|`|var|`, variables, but also named constants
		* |var_type|`xyz:float` — |lit|`|var_type|`, variable and type with colon.
	Todo at 2026-06-25:
		* Implement 'pkg' for 'package' as opposed to importable module.
		* Implement 'var_type'
"""
