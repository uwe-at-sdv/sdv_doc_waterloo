r"""
Preamble:
	profile:
		class
	normative_sections:
		Definitions, Contract, Derived_from, Factory, Public_classes, Public_methods,\
		Public_types, Public_variables, Public_constants
	scope:
		public
Definitions:
	Example:
		A class used to demonstrate class-specific Authoring JSON sections.
Contract:
	general:
		|Must| represent one configurable demonstration object.
	constructor:
		|Must| accept one |var|`mode` value.
	traits:
		final
Description:
	Class descriptions can combine prose with structured tables.
	|
	|begin_table|
	|columns|
	Mode |tab| Effect
	|rows|
	simple |tab| Use the compact demonstration.
	full |tab| Enable every optional feature.
	|end_table|
Derived_from:
	waterloo_authoring_showcase.BaseExample
Factory:
	waterloo_authoring_showcase.Example.from_config:
		Create an Example from configuration values.
		|
		|begin_table|
		|columns|
		Key |tab| Meaning
		|rows|
		mode |tab| Selected demonstration mode.
		|end_table|
Public_classes:
	waterloo_authoring_showcase.Example.Nested
Class_overview:
	Nested:
		A nested supporting class.
Public_methods:
	waterloo_authoring_showcase.Example.describe
Method_overview:
	describe:
		Return a human-readable description.
Public_types:
	State_t:
		A type alias for Example state values.
Public_variables:
	mode:
		The active demonstration mode.
Public_constants:
	DEFAULT_MODE:
		The mode selected when configuration omits one.
Notes:
	Factory:
		Factory entries are class-specific and use qualified function identifiers as keys.
"""
