.. _chapter_examples:

Examples
########

This section covers cases that are not necessarily contained in the reference documentation,
such as

* factories
* properties
* decorators
* coroutines
* classes within classes
* constants in classes
* type aliases in classes

Factories
---------

.. wtrl_push_current_module:: test_docitem_factory_vec2d

This section illustrates the use of the :wtrl_label:`Factory` section. In this context,
:wtrl_label:`Factory` does not refer to the well-known design pattern, but to the
practical notion of a function that creates an instance of a class and
encapsulates the constructor.

In Python, several patterns exist for defining factory functions.
In the sample program, we focus on the following:

* module-level functions with explicit signatures,
* class methods with explicit signatures,
* functions or class methods using runtime polymorphism.

The use of :wtrl_attr:`@singledispatch` is intentionally omitted.

The inventory of factory functions in this example is intentionally redundant
for demonstration purposes. In practice, the choice among these patterns
depends on personal style and design preferences.

The class :wtrl_type:`Vec2d` represents two-dimensional vectors.
We would like to create a vector in the following ways:

* without arguments, yielding the zero vector,
* by passing two :wtrl_type:`float`-valued components :wtrl_var:`x` and :wtrl_var:`y`,
* by passing another two-dimensional vector in order to create a copy.

The corresponding implementation is shown below:

.. literalinclude:: ../examples/test_docitem_factory_vec2d_no_doc.py
	:language: python

There are eight factory functions, all of which form part of the class API.
The Waterloo docstring format captures this relationship by means of a
:wtrl_label:`Factory` section, as shown in the following excerpt:

.. literalinclude:: ../examples/test_docitem_factory_vec2d.py
	:language: python
	:start-after: #-----8<-----1
	:end-before: #----->8-----1

Validation ensures that each factory entry listed in this section
is resolvable. In the generated HTML artifact, the labels of the
factory entries are rendered as links to the documentation boxes
of the referenced objects.

.. wtrl_autodoc_class_full:: Vec2d

.. wtrl_autodoc_function:: vec2d

.. wtrl_pop_current_module:: test_docitem_factory_vec2d


Properties
----------

The following example shows how properties can be documented.
A property is conceptually a member variable of a class and therefore
it is listed under :wtrl_label:`Public_variables`.

Internally, the accessor methods :wtrl_func:`fget`, :wtrl_func:`fset`,
and :wtrl_func:`fdel` are extracted from the property object and rendered
as regular methods. Their docstrings provide the normative specification
of the property's behavior, while the property itself defines the public API surface.

.. wtrl_autodoc_class_full:: test_docitem_method_property.X

Decorators
----------

.. wtrl_push_current_module:: test_docitem_method_decorator

In this section we test the graphic representation of function and method signatures
in presence of decorators, such as :wtrl_attr:`@classmethod` and :wtrl_attr:`@staticmethod`.
Consider the following test snippet:

.. literalinclude:: ../examples/test_docitem_method_decorator.py
	:language: python

In the document source we have:

.. code:: rst

	.. wtrl_method_signature:: X.f_method

	.. wtrl_method_signature_block:: X.f_method

	.. wtrl_method_signature:: X.f_classmethod

	.. wtrl_method_signature_block:: X.f_classmethod

	.. wtrl_method_signature:: X.f_staticmethod

	.. wtrl_method_signature_block:: X.f_staticmethod

The output for methods without decorator is:

.. wtrl_method_signature:: X.f_method

.. wtrl_method_signature_block:: X.f_method

For class method we have:

.. wtrl_method_signature:: X.f_classmethod

.. wtrl_method_signature_block:: X.f_classmethod

And for static methods:

.. wtrl_method_signature:: X.f_staticmethod

.. wtrl_method_signature_block:: X.f_staticmethod

An example with more than one decorator. The inline representation is
not really helpful, and we recommend to switch to the block representation.

.. wtrl_method_signature:: fib

.. wtrl_method_signature_block:: fib


.. wtrl_pop_current_module:: test_docitem_method_decorator

Coroutines
----------

Let's take a look at how coroutines are rendered. The important keyword is
:wtrl_attr:`async`. The inline signature looks like this:

.. wtrl_function_signature:: test_docitem_coroutine.make_coffee

In the block representation, we get:

.. wtrl_function_signature_block:: test_docitem_coroutine.make_coffee

Apart from that, coroutines behave like other methods and functions in terms of documentation.
The code segment

.. literalinclude:: ../examples/test_docitem_coroutine.py
	:language: python
	:start-after: #-----8<-----1
	:end-before: #----->8-----1

is rendered as:

.. wtrl_autodoc_function:: test_docitem_coroutine.make_coffee

For generators we get:

.. wtrl_function_signature:: test_docitem_coroutine.get_marmalade

and

.. wtrl_function_signature_block:: test_docitem_coroutine.get_marmalade

from source code:

.. literalinclude:: ../examples/test_docitem_coroutine.py
	:language: python
	:start-after: #-----8<-----2
	:end-before: #----->8-----2

Definitions
-----------

A :wtrl_label:`Definitions` section can be provided for modules, classes, and callables.
Each subsection label consists of a comma-separated list of identifiers.
The first identifier denotes the :wtrl_term:`Term`, while any following identifiers
denote :wtrl_term:`Variations` of that term.

The purpose of allowing multiple identifiers is to capture morpho-syntactic
and orthographic variations of the same term. In the following example,
we define the term :wtrl_dfn:`sensitive`, as well as the capitalized form
:wtrl_dfn:`Sensitive` (for sentence-initial usage) and the nominalized form
:wtrl_dfn:`Sensitivity`.


.. literalinclude:: ../examples/test_docitem_definitions.py
	:language: python

The result is

.. wtrl_autodoc_module:: test_docitem_definitions

Inherited Definitions
---------------------

The following example demonstrates how definition items can be inherited
from module level to class or function level in order to avoid unnecessary repetition.

.. literalinclude:: ../examples/test_docitem_definitions_inherited.py
	:language: python

The module docstring is rendered as shown below. It contains commonly used
definitions for :wtrl_term:`Identifier` and :wtrl_term:`Qualified_Identifier`.
By means of the subsection :wtrl_label:`Definitions._inherited`, each class or
function object defined in the module can reference these definitions in its
free-text sections.

.. wtrl_autodoc_module:: test_docitem_definitions_inherited

The class docstring inherits the terms :wtrl_term:`Identifier` and
:wtrl_term:`Term_Z`, and defines a new term
:wtrl_term:`Private_Identifier` based on :wtrl_term:`Identifier`.
Referencing inherited terms using :wtrl_lit:`\|term\|` is valid and
results in semantic highlighting in the generated HTML artifact.

.. wtrl_autodoc_class:: test_docitem_definitions_inherited.X

The method docstring inherits the terms
:wtrl_term:`Identifier` and :wtrl_term:`Qualified_Identifier`
and uses them to define a new term :wtrl_term:`Anchor`.

.. wtrl_autodoc_method:: test_docitem_definitions_inherited.X.spam


A display cabinet of sections
-----------------------------

The following example shows the docstring of one of Waterloo's built-in functions, :wtrl_func:`get_num_indent`.
The function has the following signature:

.. wtrl_function_signature_block:: sdv.doc.waterloo.docitem.get_num_indent

and the docstring reads:

.. code:: python

	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Definitions, Contract, Parameters, Returns, Raises
		status:
			stable
	Definitions:
		TAB:
			A scheme that demands indentation by means of an integer number\
			of tab characters (ASCII |value|`0x09`).\
			For this scheme, |var|`INDENT_UNIT` is a single tab character.
		SPC4:
			A scheme that demands indentation by means of an integer multiple\
			of four space characters (ASCII |value|`0x20`).
			For this scheme, |var|`INDENT_UNIT` consists of four space characters.
	Contract:
		general:
			|Must| accept a single line string and an indentation scheme.
			|Must| count the number of leading indentations of the input according\
			to the scheme passed.
			|Must| accept an empty string.
	Parameters:
		tr:
			Tracer for better error messages
		line:
			A single line string.
		indent_scheme:
			A symbolic value representing one of the two possible indentation\
			schemes |term|`TAB` or |term|`SPC4`.
	Returns:
		|Must| return the number of indentations found at the beginning of the string\
		in units as decribed by the indentation scheme passed.
	Raises:
		RuntimeError:
			|Must| raise if prefix contains a mix not representable\
			as |var|`n` repetitions of |var|`INDENT_UNIT`.
			|Must| raise if the white space characters (greedy match of\
			tab or space) at the beginning of the line\
			cannot be described by the indentation scheme passed.
	"""

Note that we have a section here called :wtrl_label:`Definitions`, which significantly
reduces the load on the normative sections :wtrl_label:`Parameters` and :wtrl_label:`Raises`.
:wtrl_label:`Definitions` is normative because we list it under :wtrl_label:`Preamble.normative_sections`,
although it does not contain a normativity keyword. Yet the definitions given there are binding
for the entire documentation box rendered from this docstring.

Subections :wtrl_label:`requires`, :wtrl_label:`ensures`, and :wtrl_label:`invariants` 
---------------------------------------------------------------------------------------

This example illustrates the use of the subsections :wtrl_label:`requires`, 
:wtrl_label:`ensures`, and :wtrl_label:`invariants`.
These labels follow the classic Design-by-Contract distinction between
preconditions, postconditions, and invariants:

- :wtrl_label:`requires` specifies obligations of the caller.  
  If a requirement is violated, the function's behaviour is undefined 
  within the normative model.

- :wtrl_label:`ensures` specifies guarantees provided by the function 
  upon successful completion, assuming all requirements were met.

- :wtrl_label:`invariants` specifies properties that must hold 
  independently of a particular call. They typically express structural,
  semantic, or algebraic constraints that characterize the function itself
  (e.g. idempotence, determinism, monotonicity).

Syntactically, these subsections are not treated differently from 
:wtrl_label:`general`. Their purpose is semantic refinement: they allow
normative statements to be grouped according to their logical role within
the contract. This separation improves clarity for both human readers and automated tooling,
as normative statements can be classified according to their contractual role.

.. wtrl_function_signature_block:: test_docitem_invariants_requires_ensures.normalize_identifier

.. wtrl_autodoc_function:: test_docitem_invariants_requires_ensures.normalize_identifier

Class within class
------------------

.. wtrl_push_current_module:: test_docitem_class_class

The following example of a class :wtrl_type:`Y` nested in another class :wtrl_type:`X`,
both equipped with a method, can be rendered by a single command

.. code:: rst

	.. wtrl_autodoc_class_full:: X

This directive recusrsively iterates over the class hierarchy and ramifies to the other
member, like e.g. methods. The source code is:

.. literalinclude:: ../examples/test_docitem_class_class.py
	:language: python

And the result is:

.. wtrl_autodoc_class_full:: X

.. wtrl_pop_current_module:: test_docitem_class_class

Formatting tests
----------------

A simple test for demonstrating the pipe operator convention in the output layer.

.. wtrl_autodoc_function:: test_docitem_function_pipe.f


