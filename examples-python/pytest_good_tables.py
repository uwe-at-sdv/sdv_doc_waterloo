"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Description
Contract:
	general:
		|Must| provide a valid table fixture for JSON rendering tests.
Description:
	Text before the table.
	|begin_table|
	|columns|
	Name |tab| Type |tab| Meaning
	|rows|
	alpha |tab| |type|`str` |tab| First value.
	|title|
	Output values for |class|`Result` |Must| be serializable.
	|columns|
	Name |tab| Type |tab| Meaning
	|rows|
	beta |tab| |type|`int` |tab| Second value.
	|end_table|
	Text after the table.
"""
