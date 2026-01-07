Documentation
=============

Documentation blocks
--------------------

This section is normative. It defines the required structure of documentation blocks.
A :cdml_dfn:`documentation block` is a graphical or textual representation of a Python docstring.

All documentation blocks contain the following meta information:

* :cdml_label:`Preamble:`
	- :cdml_label:`profile`
		* This entry |must| contain one out of a fixed set
		  of keywords which specify the category being documented, e.g.
		  class, function or method. The categories have different requirements
		  which sections must be present and which are not allowed.
	- :cdml_label:`Normative sections`
		* This entry |must| list the normative
		  sections of the documentation block.

Class documentation blocks
--------------------------

A class documentation blocks |must| contain the following sections and subsections:

* :cdml_label:`Contract:`
	- The section |must| be marked as normative.
	- :cdml_label:`General`
		* |Must| contain an explanation of the purpose of the class sufficient to decide
		  whether the class is applicable to a given use case.
	- :cdml_label:`Constructor`
		* |Must| contain an explanation or a reference to an explanation for each parameter.
	- :cdml_label:`Api`
		* |Must| list all sections whose contents define the public method set.
		  The union of these sections defines the public method set.
* :cdml_label:`Derived from`
	- |Must| list the base classes that contribute public functions, attributes, or semantic guarantees.
* :cdml_label:`Public methods`
	- |Must| define which methods are considered public regardless of whether or not they
	  are accessible in a technical sense.

If instances of a class are created via factories:

* :cdml_label:`Factory`
	- |Must| list all factory functions with full signature and either
		a. an explanation of their behavior or
		b. a reference to a section providing that explanation.

Since the contract of the class is usually spread over more than one section,
the contract section |should| contain a subsection

* :cdml_label:`Contract`
	- :cdml_label:`forward:`
		* |Must| mention or list all sections with normative character.
		  required for understanding the class.

Function documentation blocks
-----------------------------

Function documentation blocks |must| contain sections and subsections:

* :cdml_label:`Contract`
	- The section |must| be marked as normative.
	- :cdml_label:`General`
		|Must| contain an explanation of what the function is good for.
* :cdml_label:`Parameters`
	- |Must| list all parameters and an explanation for each parameter
* :cdml_label:`Returns`
	- |Must| explain the return value of the function.
* :cdml_label:`Raises`
	- |Must| list all exception classes that may raise under normal circumstances,
	  that means, the caller has been typechecked with similarly strict rules
	  as the module containg the called function.
	- Informative: Typechecking should be considered undispensable in modern
	  Python. CLQL does not runtime-check for precise usage of types, when this
	  can be covered by static typechecking tools.

