r"""
Preamble:
	profile:
		module
	normative_sections:
		Definitions, Contract, Public_classes
Definitions:
	Sensitive, sensitive, Sensitivity, Sensitivities:
		A widget is |dfn|`sensitive` if and only if it responds to user interaction.
		|dfn|`Sensitivity` |must| be visually indicated, by graying out non-sensitive widgets.
Contract:
	general:
Public_classes:
	X
"""

class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Definitions, Contract
	Definitions:
		Visible, visible, Visibility:
			A widget is |dfn|`visible` if and only if it is rendered on the screen.
		_inherit:
			Sensitive
	Contract:
		general:
			|Must| demonstrate inheritance of definitions.
			|Must| allow to refer to the following terms:\
			- |dfn|`sensitive`
			- |dfn|`Sensitivity`
			- |dfn|`Visible`
			- |dfn|`Visibility`
		constructor:
			Default
	"""
	def __init__(self):
		pass   
