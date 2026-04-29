r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions
Definitions:
	Nested_List_Example:
		We test the waterlint subcommand render-html\
		by the following nested lists.
		|
		Begin-Test
		* Item a
		* Item b
		+ Item b.a
		# Item b.a.1
		# Item b.a.2
		+ Item b.b
		- Item b.b.a
		+ Item b.c
		* Item c
		# Item c.1
		# Item c.2
		+ Item c.2.a
		# Item c.3
		End-Test
Contract:
	general:
		|Must| demonstrate nested lists in freeform sections.
	
"""
