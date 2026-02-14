.. _chapter_examples_minimax:

Docstrings - minimal and full examples
--------------------------------------

In this section, we will systematically look at the docstrings for the
various categories, modules, classes, and functions or methods. The aim
is to clarify which sections and subsections are optional and which
are mandatory, and what purpose they serve.

Module docstrings -- minimal example
....................................

The minimum requirements for any Waterloo docstring are a valid :wtrl_label:`Preamble`
with subsections :wtrl_label:`profile` and :wtrl_label:`normative_sections`,
and a :wtrl_label:`Contract`.

.. rubric:: Mandatory

:wtrl_label:`Preamble` -- The :wtrl_label:`Preamble` represents the metadata of the docstring.
It specifies what type of object is being documented (here :wtrl_label:`profile:` :wtrl_value:`module`)
and which sections of the docstring are normative (:wtrl_label:`normative_sections`). Sections not listed
here are not normative.

.. rubric:: Mandatory and always normative

:wtrl_label:`Contract` -- The :wtrl_label:`Contract` is the central section in which it is normatively documented
what an object is used for, what it must be capable of, what preconditions must be fulfiled
in order to use it, and what guarantees the object provides for the result.
In the case of the module, there is a subsection named :wtrl_label:`general`.

.. literalinclude:: ../examples/test_docitem_module_minimal.py
	:language: python

.. wtrl_autodoc_module:: test_docitem_module_minimal

Module docstrings -- full example
.................................

The following example shows all possible sections and subsections in a module docstring.
Some of the sections must always be listed as normative, some only under
certain conditions (e.g. if they contain normativity keywords),
while others are explicitly non-normative and must not be listed as normative.

.. rubric:: Mandatory and always normative

Sections :wtrl_label:`Contract`

.. rubric:: Optional and always normative

Sections :wtrl_label:`Definitions`, :wtrl_label:`Public_classes`, :wtrl_label:`Public_functions`,
:wtrl_label:`Public_types`, :wtrl_label:`Public_variables`, :wtrl_label:`Public_constants`

.. rubric:: Optional and normative under conditions

Sections :wtrl_label:`Description` and :wtrl_label:`See_also` are normative under
certain conditions.
If the description contains at least one normativity keyword in tokenized form,
it must be listed under :wtrl_label:`normative_sections` -- and vice versa.
For :wtrl_label:`See_also` the following rule applies:
Any validator will check whether the objects listed under :wtrl_label:`See_also`
can be resolved. If the section is listed as normative, resolution failure leads
to an error. If it is not listed, resolution failure only leads to a warning.


.. rubric:: Optional and never normative

* The :wtrl_label:`Terminology` and :wtrl_label:`Notes` sections are intended
  for human-readable explanations and notes. Since one of the basic principles
  of the Waterloo format is the strict separation between normative and
  informative content, certain sections must never be listed as normative.

* Sections :wtrl_label:`Class_overview` and :wtrl_label:`Function_overview`
  are informative by design. Normative statements in :wtrl_label:`*_overview`
  sections would violate |SSoT| by introducing an additional normative source
  besides the class or function docstring. They would also violate |LoII|, as
  normative information would be distributed across multiple docstrings.
  The split between :wtrl_label:`*_overview` and :wtrl_label:`Public_*`
  sections is therefore necessary to satisfy BinNorm. Without this split,
  sections would contain a mixture of normative and informative content.

.. literalinclude:: ../examples/test_docitem_module_full.py
	:language: python

.. wtrl_autodoc_module:: test_docitem_module_full

Class docstrings -- minimal example
...................................

Many sections and subsections are equivalent to their
counterparts in module docstring, but there are sections
and subsections specific to class docstrings:


.. rubric:: Mandatory and always normative

:wtrl_label:`Contract.constructor` -- Each instance of a class is constructed in one or the other way.
Therefore the Waterloo format demands a normative statement
on the class constructor in section :wtrl_label:`Contract`.

.. literalinclude:: ../examples/test_docitem_class_minimal.py
	:language: python

.. wtrl_autodoc_class:: test_docitem_class_minimal.MyClass

Class docstrings -- full example
................................

For demonstration purposes, the constructor signature in this example
covers all supported ways to pass and accept parameters. Subsection
:wtrl_label:`Contract.constructor` should describe the constructor
parameters, how they are passed, and what the constructor does.

In addition to the sections described for module docstrings, class
docstrings support the following optional sections and subsections.

.. rubric:: Optional and always normative

:wtrl_label:`Contract.traits` --
This optional subsection allows to declare certain semantic properties
of a class. A limited set of trait identifiers is defined by this
specification, including :wtrl_value:`abstract` for classes that are
intended to serve primarily as base classes, and :wtrl_value:`final`
for classes that are explicitly not meant to be extended.
If the subsection is absent, the default is that the class is neither
:wtrl_value:`abstract` nor :wtrl_value:`final`, meaning that it can be
instantiated and may serve as a base class.
The purpose of this subsection is to provide a normative way to express
design intent, such as indicating that a class is part of an API surface
only, or that it must not be used as a base for further extensions.

:wtrl_label:`Derived_from` --
This optional section is related to :wtrl_label:`Contract.traits`. It
normatively extends the public API of the documented class by declaring
which base classes contribute public methods, types, variables, constants,
or semantic guarantees.
Validators verify that the classes listed in this section can be resolved
using Python's import mechanism. This serves as an anti-drift mechanism:
if a base class is renamed, removed, or moved without updating this
section, validation fails.

:wtrl_label:`Public_methods` --
This section defines which methods of the class are part of the public
API and is therefore normative.

:wtrl_label:`Method_overview` --
This section is informative. It may be used to provide human-readable
descriptions for selected methods, explaining their purpose or typical
usage. This section may only be present if section
:wtrl_label:`Public_methods` exists.


.. literalinclude:: ../examples/test_docitem_class_full.py
	:language: python

.. wtrl_autodoc_class:: test_docitem_class_full.MyClass

Function docstrings -- minimal example
......................................

The following minimal example illustrates the essential structure of a
function docstring. While deliberately simple, it highlights the sections
that appear in every function docstring.

Apart from :wtrl_label:`Preamble` and :wtrl_label:`Contract`, which are already
known from module and class docstrings, the following sections are present.

.. rubric:: Mandatory and always normative

:wtrl_label:`Parameters` --
Each subsection of this normative section represents a parameter of the
function. The minimal example shown below does not define any parameters.

:wtrl_label:`Returns` --
This section describes the return value. It is normative by definition,
but it is up to the author whether to formulate requirements using
Normativity Keywords or to keep the description purely descriptive.

:wtrl_label:`Raises` --
Each subsection is labelled by an exception class and describes, normatively,
the circumstances under which the exception is raised.

.. literalinclude:: ../examples/test_docitem_function_minimal.py
	:language: python

.. wtrl_function_signature:: test_docitem_function_minimal.spam

.. wtrl_autodoc_function:: test_docitem_function_minimal.spam

A typical way to populate the :wtrl_label:`Raises` section is as follows:
An exception |must| be raised if it is a direct consequence of the function's
own behavior. An exception |may| be raised if it originates from a function
called internally, potentially even from a different package.

Since the behavior of external functions may change over time (for example
due to refactoring), the most conservative approach for such cases is to
document exception propagation explicitly:

.. code:: python3

	"""
	Raises:
		BaseException:
			|May| propagate from functions ... and ...
	"""


Function and method docstrings -- intermediate example
......................................................

The following example demonstrates a non-trivial method docstring that
goes beyond the minimal structure, but does not yet use all available
sections and subsections.

The method shown here is part of an abstract base class. It documents
expected behavior, required preconditions, and possible failure modes,
even though the method itself is not implemented in the base class.

This pattern is typical for framework-style code, where derived classes
are expected to provide the actual implementation while adhering to a
shared contract.

Most of the sections used in this example have already been introduced
for module and class docstrings. However, the :wtrl_label:`Contract`
section now contains a :wtrl_label:`requires` subsection, which is
optional but normative as part of the contract.

The :wtrl_label:`requires` subsection should be used to specify the
conditions that must be satisfied by the caller in order for the
function to operate correctly.

The functionality of :wtrl_label:`requires` partially overlaps with
:wtrl_label:`Raises`, as unmet prerequisites often lead to error
conditions. Since such error behavior can also be described in
:wtrl_label:`Raises`, the :wtrl_label:`requires` subsection itself is
optional.

.. literalinclude:: ../examples/test_docitem_function_medium.py
	:language: python
	:start-after: #-----8<-----1
	:end-before: #----->8-----1

Note that the function signature is not repeated in the docstring.
Instead, it is included in the documentation via dedicated directives,
ensuring that the rendered documentation remains complete without
violating the Single Source of Truth principle (|SSoT|).

In this example, the function signature is annotated and treated as the
sole authoritative source of type information, in accordance with the
Single Source of Truth principle. This prevents the function
signature and its documentation from drifting apart, supporting the
Drift Prevention (|DrPrv|) principle.

As a consequence, the function signature must be explicitly included in
the rendered documentation. This can be achieved using the directive

.. code:: rst

	.. wtrl_function_signature:: test_docitem_function_medium.docitem_base.parse

.. wtrl_method_signature:: test_docitem_function_medium.docitem_base.parse

For more complex type annotations, the directive

.. code:: rst

	.. wtrl_function_signature_block:: test_docitem_function_medium.docitem_base.parse

may be used, which renders one line per parameter:

.. wtrl_method_signature_block:: test_docitem_function_medium.docitem_base.parse

While there is some flexibility in how the signature is presented, it
must be included in order to make the documentation complete.

.. wtrl_autodoc_method:: test_docitem_function_medium.docitem_base.parse

Interlude -- Docstring for inherited methods
............................................

The following example shows how to build a docstring for an inherited method.
It is noticeable that, apart from the usual sections :wtrl_label:`Preamble`
and :wtrl_label:`Contract`, there are no other mandatory sections. In particular,
the sections :wtrl_label:`Parameters`, :wtrl_label:`Returns`, and :wtrl_label:`Raises`
are missing because they are already included in the normative documentation of the
base method. In section :wtrl_label:`Contract`, we see how this base method
is explicitly referenced using the mandatory subsection :wtrl_label:`base`.

.. literalinclude:: ../examples/test_docitem_function_medium.py
	:language: python
	:start-after: #-----8<-----2
	:end-before: #----->8-----2

.. wtrl_method_signature_block:: test_docitem_function_medium.docitem_traits.parse

.. wtrl_autodoc_method:: test_docitem_function_medium.docitem_traits.parse

 
Apart from these differences, there are optional sections that are used
in the same way as for modules, classes, and functions. So, all in all we have:

.. rubric:: Mandatory and always normative

Subsection :wtrl_label:`base` is mandatory and normative. It unambiguously refers
to the base method whose contract is authoritative for the derived method.

A derived method docstring |may| add additional normative statements, but it |must|
remain substitutable for the base method.

* Preconditions:
  A derived method |must_not| strengthen the base method's preconditions.
  In particular, any requirement that constrains valid inputs |must| be expressed
  in :wtrl_label:`Contract.requires` and |must| be compatible with the base method.

* Guarantees:
  A derived method |must| preserve all guarantees of the base method.
  A derived method |may| provide additional guarantees by adding or refining
  :wtrl_label:`Contract.ensures`. Callers that only rely on the base contract
  |may| ignore such additional guarantees.

* Failure modes documented in the base method |must_not| be replaced by weaker
  guarantees. Additional failure modes |must_not| occur for inputs that satisfy
  the base preconditions, unless they are explicitly permitted by the base contract.

.. rubric:: Optional and always normative

* Section :wtrl_label:`Definitions`
* Subsection :wtrl_label:`Contract.requires` as discussed above under "Preconditions"
* Subsection :wtrl_label:`Contract.ensures` as discussed above under "Guarantees"

.. rubric:: Optional and normative under conditions

Sections :wtrl_label:`Description` and :wtrl_label:`See_also`

.. rubric:: Optional and never normative

Sections :wtrl_label:`Terminology` and  :wtrl_label:`Notes`

Function docstrings -- full example
...................................

.. literalinclude:: ../examples/test_docitem_function_full.py
	:language: python

.. wtrl_method_signature:: test_docitem_function_full.factorial

.. wtrl_autodoc_method:: test_docitem_function_full.factorial
