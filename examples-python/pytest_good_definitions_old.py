r"""
Preamble:
	profile:
		module
	normative_sections:
		Definitions, Contract, Public_classes
Definitions:
	Sensitive:
		A widget is |dfn|`sensitive` if and only if it responds to user interaction.
	sensitive:
		Form of |dfn|`Sensitive`.
	Sensitivity:
		|dfn|`Sensitivity` |must| be visually indicated, by graying out non-sensitive widgets.
	Sensitivities:
		Plural form of |dfn|`Sensitivity`.
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
		Visible:
			A widget is |dfn|`visible` if and only if it is rendered on the screen.
		visible:
			Form of |dfn|`Visible`.
		Visibility:
			Noun form of |dfn|`Visible`.
		_inherit:
			Sensitive, sensitive, Sensitivity, Sensitivities
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
