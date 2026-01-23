Introduction
============

Waterloo ist ein Format fuer Python-Docstrings, das auf
maschinenverifizierbare Normativitaet abzielt. Dabei ist von Bedeutung,
dass Docstrings einem sauber definierten, eindeutigen Format entsprechen,
und dass genau spezifiziert werden kann, welche Abschnitte als normativ,
das heisst bindend im Sinne eines API-Vertrags, betrachtet werden sollen.

Das Projekt Waterloo besteht aus folgenden Komponenten.

* Es definiert normativ ein Format fuer Python Docstrings,
  mittels einer Grammatikdarstellung in EBNF.

* Es stellt Parser-Funktionen und Node-Klassen zum Aufbau
  eines Abstrakten Syntax-Baums (AST) und Validatoren
  fuer ASTs bereit.

* Es stellt eine Sphinx-Extension zur Darstellung des ASTs in reST/Sphinx-Dokumenten
  bereit.

Die Konsistenz des Projekts wird durch automatisierte Tests gesichert.

Why normative documentation?
----------------------------

Most documentation in software projects is written as free-form prose. This works well for humans:
we infer intent from context, tolerate ambiguity, and fill gaps using experience. However,
prose is inherently underspecified. It often answers what something roughly does,
but not what must always be true.

Normative documentation closes this gap by expressing requirements as explicit rules.
Instead of "this function returns a value" it states: it must return :wtrl_value:`None`,
it must not modify input, or it should raise :wtrl_type:`RuntimeError` under defined circumstances.
Such statements define a contract: a set of constraints that the implementation and its callers can rely on.

This is valuable for three reasons:

.. rubric:: Consistency and reviewability

Normative rules make assumptions visible. They reduce misunderstandings and make API
reviews less subjective, because requirements can be checked against a concrete list of obligations.

.. rubric:: Machine-verifiable structure

When rules are written in a structured format, tools can validate them. A validator
can detect missing sections, incomplete parameter coverage, unknown exceptions, or inconsistent API listings. This improves documentation quality without requiring "perfect prose".

.. rubric:: A specification layer for automation and AI

Modern development increasingly involves automated tooling and AI assistants.
These systems benefit from explicit constraints. A normative contract provides a compact, unambiguous representation of intent that is easier to interpret than informal text and helps reduce guesswork and hallucination.

Waterloo uses a docstring format that keeps the machine-readable part strict and predictable
while allowing free-form human explanation where appropriate. The goal is not to replace
readable documentation, but to add a reliable contract layer that can be validated and used by tools.


Project status
--------------

We use :wtrl_lit:`mypy` for static typechecking. The Modules

* :wtrl_file:`sdv.doc.docitem`
* :wtrl_file:`sdv.doc.docitem_helper`
* :wtrl_file:`sdv.doc.docitem_tokenizer`
* :wtrl_file:`sdv.doc.docitem_sphinx`

are validated on a regular basis. The current status is

.. literalinclude:: _static/type_checking_report.txt
	:language: none

Our :wtrl_lit:`mypy`-configuration is:

.. literalinclude:: ../../mypy.ini

Exceptions from typechecking are:

.. literalinclude:: _static/type_checking_exceptions.txt
	:language: none


How to use
----------

By the time you get interested in this project you most likely
already have installed Sphinx. So let us proceed with

.. rubric:: Set up a sphinx documentation project

The file :wtrl_file:`conf.py` consists of various sections. In "Path setup"
add the paths required for importing the modules you would like to
write a documentation for.

In section "General configuration" add the path to your module:

.. code:: python

	sys.path.insert(0, os.path.abspath('/path/to/my/moduledir'))

Also in section "General configuration" add the Waterloo Sphinx extension to the list of extensions:

.. code:: python

	extensions = [
		...
		"sdv.doc.waterloo.docitem_sphinx",
		]


* Add a code segment like this one  in section "HTML output"

.. code:: python

	rst_prolog = r"""
	.. |Must| replace:: :wtrl_norm:`Must`
	.. |must| replace:: :wtrl_norm:`must`
	.. |Must_not| replace:: :wtrl_norm:`Must not`
	.. |must_not| replace:: :wtrl_norm:`must not`
	.. |Should| replace:: :wtrl_norm:`Should`
	.. |should| replace:: :wtrl_norm:`should`
	.. |Should_not| replace:: :wtrl_norm:`Should not`
	.. |should_not| replace:: :wtrl_norm:`should not`
	.. |May| replace:: :wtrl_norm:`May`
	.. |may| replace:: :wtrl_norm:`may`
	.. |May_not| replace:: :wtrl_norm:`May not`
	.. |may_not| replace:: :wtrl_norm:`may not`
	.. |empty| replace:: <empty>
	"""

Fill in the roles you would like to see for the normative keywords.
Alternatively you can add the replacement rules directly in your reST-document,
see documentation of Sphinx for details.

If you want generate an RFC 2119 style document, you may rather have replacements like

.. code:: python

	rst_prolog = r"""
	.. |Must| replace:: MUST
	.. |must| replace:: MUST
	.. |Must_not| replace:: MUST NOT
	.. |must_not| replace:: MUST NOT
	.. |Should| replace:: SHOULD
	.. |should| replace:: SHOULD
	.. |Should_not| replace:: SHOULD NOT
	.. |should_not| replace:: SHOULD NOT
	.. |May| replace:: MAY
	.. |may| replace:: MAY
	.. |May_not| replace:: MAY not
	.. |may_not| replace:: MAY not
	.. |empty| replace:: <empty>
	"""



Introductory examples
---------------------

This section is informative.


Module
......

Let us do an example: In directory :wtrl_file:`doc/examples` you see a file :wtrl_file:`test_docitem_module.py`.
On module level this is equipped with a basic Waterloo docstring:

.. literalinclude:: ../examples/test_docitem_module.py
	:language: python

In order to render this in Sphinx, we add the directive

.. code::

	.. wtrl_autodoc_module:: test_docitem_module

at the position in the document where the docstring is supposed to be rendered, and get:

.. wtrl_autodoc_module:: test_docitem_module

Although this example is oversimplified and pretty useless, because no API has been declared,
we can point out some of the principles of the Waterloo format.

	* First of all, it is based on indentation. This means it uses a considerable amount of
	  space on the input side, but remains human-readable. Indentation can be done by
	  multiples of tab characters or four spaces. We prefer tab characters for our
	  examples.

Within the docstring we then have :wtrl_dfn:`sections`, and within the sections there may be
:wtrl_dfn:`subsections` (or text content, as we shall see later). Let us have a look at the details: 

	* Each docstring starts with a :wtrl_label:`Preamble`, which contains a subsection
	  :wtrl_label:`profile` allowing a certain set of profile specifiers. In our case
	  it reads :wtrl_value:`module` because we are going to implement the docstring of
	  a module. The extension could derive this information from the context, yet for
	  normativity it is important to create self-contained documentation snippets
	  instead of relying on non-documentary context.

	* The :wtrl_label:`Preamble` requires a subsection :wtrl_label:`normative_sections`
	  which clearly and uniquely specifies which of the subsequent sections are normative.
	  All others are informative by definition.

	* Each Waterloo docstring must contain a section :wtrl_label:`Contract`, as shown in the example,
	  and it must be declared normative.

Module and class
................

In the next example we have a module and a class docstring, and we consider the class as
part of the public API of the module:

.. literalinclude:: ../examples/test_docitem_module_2.py
	:language: python

We render the module docstring as before:

.. code::

	.. wtrl_autodoc_module:: test_docitem_module_2

and the class docstring by

.. code::

	.. wtrl_autodoc_class:: test_docitem_module_2.MyClass

The result is:

.. wtrl_autodoc_module:: test_docitem_module_2

.. wtrl_autodoc_class:: test_docitem_module_2.MyClass


Module, class and method
........................

Finally, let us add a method to the class and attach a docstring.

.. literalinclude:: ../examples/test_docitem_module_3.py
	:language: python

The module, class and method docstrings are rendered by

.. code::

	.. wtrl_autodoc_module:: test_docitem_module_3

	.. wtrl_autodoc_class:: test_docitem_module_3.MyClass

	.. wtrl_autodoc_method:: test_docitem_module_3.MyClass.greeting

and the result is:

.. wtrl_autodoc_module:: test_docitem_module_3

.. wtrl_autodoc_class:: test_docitem_module_3.MyClass

.. wtrl_autodoc_method:: test_docitem_module_3.MyClass.greeting


Convenience: module and class stack
-----------------------------------

Repeating the module and the class each time a function, method, type or constant
is addressed by means of qualified identifier (dot notation) can become a little annoying.
Therefore the extension is equipped with state stacks for modules and classes.

.. rubric:: Modules

Once you push a module name to the stack, all subsequent
qualified identifiers for objects will be assumed to belong to that module:

.. code:: rst

	.. wtrl_push_current_module:: test_docitem_module_3

This pushes the module name to the module stack and creates a message in the document:

.. wtrl_push_current_module:: test_docitem_module_3

Now since we have a default module, a class in the module is simply addressed by for instance:

.. code:: rst

	.. wtrl_autodoc_class:: MyClass

instead of

.. code:: rst

	.. wtrl_autodoc_class:: test_docitem_module_3.MyClass

In order to close the domain of the default module, add a directive:

.. code:: rst

	.. wtrl_pop_current_module:: test_docitem_module_3

and in the text you will see:

.. wtrl_pop_current_module:: test_docitem_module_3

.. rubric:: Classes

The same mechanism is provided for class level as well. The purpose here is to avoid
repeating the class name over and over again in comprehensive documentations
of methods. The push-command reads:

.. code:: rst

	.. wtrl_push_current_class:: test_docitem_module_3.MyClass

which creates a text snippet:

.. wtrl_push_current_class:: test_docitem_module_3.MyClass

whereas the pop-command is

.. code:: rst

	.. wtrl_pop_current_class:: test_docitem_module_3.MyClass

which is rendered as:

.. wtrl_pop_current_class:: test_docitem_module_3.MyClass

More examples
-------------

The following example shows the docstring of one of Waterloo's built-in functions, :wtrl_func:`get_num_indent`.
The function has the following signature:
:wtrl_function_signature:`sdv.doc.waterloo.docitem.get_num_indent`

and the docstring reads:

.. code:: rst

	Preamble:
		profile:
			function
		normative_sections:
			Definitions, Contract, Parameters, Returns, Raises
	Definitions:
		TAB:
			A scheme that demands indentation by means of an integer number of tab characters (ASCII :wtrl_value:`0x09`).
			For this scheme, :wtrl_var:`INDENT_UNIT` is a single tab character.
		SPC4:
			A scheme that demands indentation by means of an integer multiple of four space characters (ASCII :wtrl_value:`0x20`).
			For this scheme, :wtrl_var:`INDENT_UNIT` consists of four space characters.
	Contract:
		general:
			|Must| accept a single line string and an indentation scheme.
			|Must| count the number of leading indentations of the input according to the scheme passed.
			|Must| accept an empty string.
	Parameters:
		tr:
			Tracer for better error messages
		line:
			A single line string.
		indent_scheme:
			A symbolic value representing one of the two possible indentation schemes TAB or SPC4.
	Returns:
		|Must| return the number of indentations found at the beginning of the string in units as decribed by the indentation scheme passed.
	Raises:
		RuntimeError:
			|Must| raise if prefix contains a mix not representable as :wtrl_var:`n` repetitions of :wtrl_var:`INDENT_UNIT`.
			|Must| raise if the white space characters (greedy match of tab or space) at the beginning of the line cannot be described by the indentation scheme passed.

Note that we have a section here called :wtrl_label:`Definitions`, which significantly
reduces the load on the normative sections :wtrl_label:`Parameters` and :wtrl_label:`Raises`.
:wtrl_label:`Definitions` is normative because we list it under :wtrl_label:`Preamble.normative_sections`,
although it does not contain a normativity keyword. Yet the definitions given there are binding
for the entire documentation box rendered from this docstring.
