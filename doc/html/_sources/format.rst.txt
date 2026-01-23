Docstring format
================

This section is normative.

.. _section_meta: 

Meta
----

In this section, we specify that all normative rules for defining the Waterloo project are given IDs, and how we construct these IDs.
We do this by the following set of rules.

.. rubric:: Lint rule (informative)

A :wtrl_dfn:`lint rule` is a normative requirement that can be checked unambiguously by a tool against the docstring text
and the available program context (e.g. signatures, importability, symbol tables).
Normative guidance that is not intended to be tool-enforced does not require a rule ID.

* [META-000] -- Each normative rule that is intended to be enforced by tools (a "lint rule") |must|
  be assigned a unique, unchangeable ASCII-string-valued rule ID.

* [META-001] -- A rule ID |must| consist of one or more uppercase ASCII letters :wtrl_lit:`[A-Z]+`,
  followed by a hyphenation character (ASCII 45), followed by three digits :wtrl_lit:`[0-9]{3}`.
  (Informative note: The set of possible rule IDs is countably infinite.)

* [META-002] -- Rule IDs |must_not| be re-used if a rule becomes obsolete.
  A new rule |must| always be assigned an ID that did not exist before.

* [META-003] -- Rule IDs |must| be treated as stable external references for tooling, configuration,
  automated validation reports, and documentation. Tools |should| include the rule ID in every diagnostic message
  derived from a normative rule.

* [META-004] -- Rules, as free-form text in documentation, |must| start with the Rule ID delimited by square brackets,
  followed by a whitespace character which allows simple, unique and robust parsing of the Rule ID.
  Informative: In this document which is written in reST, we insert a space (ASCII 32), a double-hyphen (en-dash),
  and another space (ASCII 32) between the braced Rule ID and the rule free-form text.


.. _section_definitions: 

Definitions
-----------

.. _rubric_normativity_keywords:

.. rubric:: Normativity Keyword

A :wtrl_dfn:`Normativity Keyword` is a typographically distinct word from the following set:
{|must|, |must_not|, |Must|, |Must_not|, |should|, |should_not|, |Should|, |Should_not|, |may|, |May|}.
In the Waterloo docstring format these keywords are realized as the plain word enclosed by "|" (ASCII 124).
Whenever we talk about Normativity Keywords (with capitals), we always mean the tokenized form with delimiters "|".

.. rubric:: Identifier

An :wtrl_dfn:`Identifier` is a string value that matches the regular expression :wtrl_lit:`[a-zA-Z_][a-zA-Z0-9_]*`.

.. rubric:: Qualified Identifier

A :wtrl_dfn:`Qualified Identifier` is a string formed by concatenating Identifiers (at least one) with a dot as separator.

This section defines the structure of Waterloo docstrings.
in human-readable form. The structure is presented as lists for the various sections
with embedded lists for subsections. The following patterns occur in any order:

.. code:: none

	<Section>:
		<Subsection>:
			<Free-Form-Content>
		...
		<Subsection>:
			<List-Of-Identifiers>
		...
		<Subsection>:
			<List-Of-Qualified-Identifiers>
		...

and also, in any order

.. code:: none

	<Section>:
		<Free-Form-Content>
	...
	<Section>:
		<List-Of-Identifiers>
	...
	<Section>:
		<List-Of-Qualified-Identifiers>

The label string is defined as the substring between the first non-indentation character of the line and the last colon in the line.
Since a label line |must_not| contain any non-whitespace characters after that last colon, this rule is unambiguous.
Tools |must| reject a label line that contains any non-whitespace characters after the last colon.

A section label is always an identifier followed by a colon. Subsection labels may be identifiers,
qualified identifiers or plain non-empty human-readable string followed by a colon. The precise form
of the subsection label depends on the subsection type and purpose. In either case it matches a string
parsed greedily and closed by colon.

The indentation in the patterns above reflects the (relative) indentation for sections, subsections, and content in the docstring.

Conventions

-----------

We shall use a simple dot notation in order to refer to subsections in the docstring format, like :wtrl_label:`Preamble.normative_sections` or :wtrl_label:`Definitions.<DefItem>`.

Building the AST
----------------

The Abstract Syntax Tree (AST) is created in two steps. In the first step ("tokenization") the lines of the docstring are analyzed and mapped
to the data structure described below in this section. We allow two indentation schemes namend :wtrl_dfn:`TAB` using tab (ASCII 0x09) as indentation unit
and :wtrl_dfn:`SPC4` using four spaces (ASCII 0x20) as indentation unit.
The indentation |must_not| be mixed within a docstring.
The grammar of the tokenizer in Pseudo-EBNF is:

.. code:: none

	(* Possible ways to indent *)
	spc		= "\x20" ;
	tab		= "\x09" ;
	newline		= "\n" | "\r\n" ;
	non_ws_char	= ? All characters but tab and spc ? ;
	non_nl_char	= ? All character but newline ? ;

	(* either *)
	indent_unit	= tab ;
	(* or *)
	indent_unit	= spc, spc, spc, spc ;
	(* must be fixed ahead of or during parsing
	   by analyzing leading whitespace of each line. *)

	(* A docstring consists of a set of sections *)
	wldocstring	= { section } ;

	(* A section consists of an indentation, a line and possibly an indented block *)
	section		= indent_token , line , [ block ] ;

	(* A block increasses indentation by one unit *)
	block		= indent_increase , { section } , indent_decrease ;

	(* A line must not start with tab or spc *)
	line		= non_ws_char , { non_nl_char } , newline ;

	(* Abstraction of indentation *)
	indent_increase = ? matches {indent_unit} if indent increases by one indent_unit ? ;
	indent_decrease = ? matches {indent_unit} if indent decreases by one indent_unit ? ;
	indent_token    = ? current indentation string, a multiple of indent_unit ? ;

The normative rules derived from this grammar are:

	* [TKN-001] -- The indentation scheme |must| be consistent within a docstring.
	* [TKN-002] -- In indentation scheme SPC4, indentation |must| be a multiple of 4.
	* [TKN-003] -- The indentation schema |must| be either TAB or SPC4.
	* [TKN-004] -- Indentation from one line to the next |must_not| increase by more than one unit.
	* [TKN-999] -- Implementation |must| be correct. Informative: This rule is a catch-all for unspecified tokenizer errors. Should never occur in practice.

In order to describe the tokenizer we define a type (in Python for practical reasons):

.. code:: python

	docstring_tree = List[ Union[ str, "docstring_tree"]]

A :wtrl_dfn:`DocstringTree` is a value of this type.

The tokenizer manages a state engine, which consists of the following components:

	1. A DocstringTree (initial state: :wtrl_value:`[]`), given by a variable e.g. :wtrl_var:`target`.
	2. A stack the elements of which point to :wtrl_var:`target` or any subtree thereof
	   (see recursive definition of :wtrl_type:`docstring_tree`; initial state is :wtrl_value:`[target]`),
	   represented by a variable :wtrl_var:`stack`.
	3. An integer variable :wtrl_var:`cur_indent` which represents the current level
	   of indendation during line parsing. The initial value results from analyzing
	   the docstring lines ahead of tokenization; it is the greatest common indentation value
	   over all non-empty docstring lines, measured in inden units (tab or four spaces).
	   Empty lines and whitespace-only lines |MUST| be ignored
	   for indentation analysis and |MUST| not affect the tokenizer state (stack, cur_indent).

The parser transforms the DocstringTree into an Abstract Syntax Tree, the node classes
of which are documented normatively in the Reference section of this document.
During parsing, the tokenizer |must| do the following:

For each incoming line (as defined in the Pseudo-EBNF, i.e. without indent),
processed sequentially, the following happens:
If the indentation level remains unchanged, the line is appended as a string
to the subtree represented by the top element of stack. If the indentation
level increases, an empty DocstringTree is appended to the subtree
referenced by the top element of :wtrl_var:`stack` and a reference to this DocstringTree
is pushed to :wtrl_var:`stack`. If the indentation level decreases by :wtrl_value:`n` indentation units,
an element is popped from :wtrl_var:`stack` for each of the :wtrl_value:`n` indentation levels.

The resulting DocstringTree only contains two categories of tokens, strings and lists.
The Tokenizer |must| produce a DocstringTree where each nested list corresponds to exactly
one indentation increase relative to its parent.
The Docstring is then parsed as described in section :ref:`common_sections` ff.
The Parser |must| treat the top-level as sequence of sections; each section node begins with a label-line.
Labels are parsed from strings and sets of strings or subsections are parsed from lists
in the DocstringTree. Parsing is sussessful, if the structure of the DocstringTree
is compatible to the section and subsection requirements as given below.


Inline markup in free-form content
----------------------------------

This subsection is normative.

Waterloo docstrings are primarily plain text. However, a small set of inline markup tokens is defined to allow
machine-verifiable references and consistent rendering in target formats (e.g. reST/Sphinx).

Inline markup tokens |may| occur only in *free-form content lines* (i.e. in lines that are not section labels,
subsection labels, or identifier list entries).

Tools |must_not| interpret inline markup tokens inside:

	* section labels,
	* subsection labels,
	* list entries in sections that are defined as "List-Of-Identifiers" or "List-Of-Qualified-Identifiers".

The set of tokens currently available is:

	* Token :wtrl_lit:`\|Must\|`, :wtrl_lit:`\|must\|`, ... as listed in :ref:`rubric_normativity_keywords`.
		- Usage: :wtrl_lit:`|Must|`, :wtrl_lit:`|must_not|`, ...

	* Token :wtrl_lit:`\|term\|`
		- Usage: :wtrl_lit:`|term|\`my_term\``
		- The argument (inside the tick delimiters) |must| match the pattern of an Identifier.
		- The argument |must| refer to an existing definition item :wtrl_label:`Definitions.<DefItem>`.
		- [DEF-007] -- If token :wtrl_lit:`|term|` is used at least once, section :wtrl_label:`Definitions` |must| exist and be listed as normative.
		- [DEF-008] -- Each token :wtrl_lit:`|term|` |must| reference a defined term in section :wtrl_label:`Definitions`.
		- Tools |must| report an error if the referenced definition item does not exist.
		- Renderers |should| translate this markup to a suitable construct in the target format (e.g. a term/definition role in reST).
		- If the target format does not support such a construct, tools |must| fall back to rendering only the argument text.

	* Token :wtrl_lit:`|None|`
		- Usage: :wtrl_lit:`|None|`
		- The token denotes the Python value :wtrl_value:`None`.
		- Renderers |should| translate this token to a suitable representation in the target format.
		- Tools |must| preserve the token text if no translation is available.

	* Token :wtrl_lit:`|Self|`
		- Usage: :wtrl_lit:`|Self|`
		- The token denotes the implicit receiver of a method or fluent API, i.e. Python :wtrl_value:`self` or typing :wtrl_type:`Self`.
		- Renderers |should| translate this token to a suitable representation in the target format.
		- Tools |must| preserve the token text if no translation is available.

	* Token :wtrl_lit:`|True|`
		- Usage: :wtrl_lit:`|True|`
		- The token denotes the Python value :wtrl_value:`True`.
		- Renderers |should| translate this token to a suitable representation in the target format.
		- Tools |must| preserve the token text if no translation is available.

	* Token :wtrl_lit:`|False|`
		- Usage: :wtrl_lit:`|False|`
		- The token denotes the Python value :wtrl_value:`False`.
		- Renderers |should| translate this token to a suitable representation in the target format.
		- Tools |must| preserve the token text if no translation is available.


Examples (informative)
^^^^^^^^^^^^^^^^^^^^^^

	* :wtrl_lit:`|Must| return |None| if no result is available.`
	* :wtrl_lit:`|Must| return |Self| to support fluent APIs.`
	* :wtrl_lit:`|Must| accept a |term|\`Qualified_Identifier\` as input.`


Rules not bound to a particular section
---------------------------------------

* [DOC-001] -- Each module, class, function, or method object subject to validation |must| have a docstring.
* [DOC-007] -- The docstring |must_not| be empty after whitespace-stripping.
* [DOC-002] -- Validation |must| only be applied to modules, classes, functions, or methods; other object types |must_not| be validated.

* [PRSR-001] -- Sections and subsections |must| start with a label line, that is a line containing a label.
* [PRSR-002] -- The line containing the section or subsection label |must| start with a non-empty label string after stripping indentation.
* [PRSR-003] -- The label string |must| be followed by a colon (ASCII 58).
* [PRSR-004] -- No characters other than optional whitespace |may| follow the colon on a label line.
* [PRSR-005] -- The label of a section |must| match the pattern of an Identifier followed by a colon.
* [PRSR-006] -- The label of a subsection |may| be any non-empty human-readable string followed by a colon.


.. _common_sections:

Common sections for all profiles
--------------------------------

* :wtrl_label:`Preamble:`
	- [PRE-001] -- The section |must| exist and it |must| be the first of all sections.
	- [PRE-002] -- The section |must_not| list itself in :wtrl_label:`normative_sections`. (to be implemented)
	- [PRE-015] -- |Must_not| have subsections other than { :wtrl_label:`profile`, :wtrl_label:`normative_sections` }.
	- :wtrl_label:`profile:`
		* [PRE-003] -- The subsection |must| exist.
		* [PRE-004] -- The subsection |must| have exactly one entry.
		* [PRE-014] -- The entry |must| match the pattern of an Identifier.
		* [PRE-005] -- The entry |must| be one of {:wtrl_value:`module`, :wtrl_value:`class`, :wtrl_value:`function`, :wtrl_value:`method`, :wtrl_value:`inherited_method`}.
	- :wtrl_label:`normative_sections:`
		* [PRE-006] -- The subsection |must| exist.
		* [PRE-007] -- Each line in Preamble.normative_sections |may| contain one or more Identifiers separated by commas.
		* [PRE-008] -- Whitespace around the Identifiers |must| be stripped by any tool.
		* [PRE-009] -- Each Identifier |must| occur at most once.
		* [PRE-010] -- Tools |must| treat the result as a flat list of Identifiers.
		* [PRE-011] -- The subsection |must| list the normative sections of the documentation block.
		* [PRE-012] -- Each section listed in this subsection |must| exist.
		* [PRE-013] -- Each section or subsection in the docstring that contains a Normativity Keyword must be listed in this subsection.
* :wtrl_label:`Definitions:`
	- [DEF-001] -- The section |may| exist.
	- [DEF-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [DEF-003] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<DefItem>:`
		* [DEF-004] -- Any number of subsections |may| exist provided :wtrl_label:`<DefItem>` matches the pattern of an Identifier.
		* [DEF-005] -- :wtrl_label:`<DefItem>` stands for the term to be defined normatively.
		* [DEF-006] -- The subsection |must| allow multiline free-form text.
		* [DEF-009] -- The subsection content |should| not be empty.
* :wtrl_label:`Terminology:`
	- [TERM-001] -- The section |may| exist.
	- [TERM-002] -- It |must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [TERM-003] -- It |must_not| contain Normativity Keywords.
	- [TERM-004] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Term>:`
		* [TERM-005] -- Any number of subsections |may| exist provided :wtrl_label:`<Term>` is a non-empty human-readable string.
		* [TERM-006] -- :wtrl_label:`<Term>` stands for the term to be explained informatively.
		* [TERM-007] -- The subsection |must| allow multiline free-form text.
		* [TERM-008] -- The subsection content |should| not be empty.
* :wtrl_label:`Description:`
	- [DESC-001] -- The section |may| exist.
	- [DESC-002] -- It |may| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [DESC-003] -- If it contains at least one Normativity Keyword, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [DESC-004] -- The content |may| consist of any number of free-form lines.
	- [DESC-005] -- Lines containing only a single character "|" (ASCII 124) |may| occur and |must| be interpreted as separator between paragraphs.
* :wtrl_label:`Notes:`
	- [NOTE-001] -- The section |may| exist.
	- [NOTE-002] -- It |must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [NOTE-003] -- It |must_not| contain Normativity Keywords.
	- [NOTE-004] -- Tools |must| treat the content of section :wtrl_label:`Notes` as informative and must not derive normative requirements from it.
	- [NOTE-005] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Note>:`
		* [NOTE-006] -- Any number of subsections |may| exist provided :wtrl_label:`<Note>` is a non-empty human-readable string.
		* [NOTE-007] -- The content |may| consist of any number of free-form lines.
* :wtrl_label:`See_also:`
	- [SEE-001] -- The section |may| exist.
	- [SEE-002] -- Each entry in the section |must| be an Identifier or a Qualified Identifier.
	- [SEE-003] -- If the section is not listed as normative each entry |should| refer to an existing public object (module, class, function, or method).
	- [SEE-004] -- If the section is listed as normative each entry |must| refer to an existing public object (module, class, function, or method).
	- [SEE-005] -- An entry in :wtrl_label:`See_also` |must_not| refer to the documented object itself.
	- [SEE-006] -- An entry in :wtrl_label:`See_also` |should| refer to an object that has a docstring.
	- Informative: Listing :wtrl_label:`See_also` as normative increases strictness and allows tools to rely on resolvable references.
	- Informative: Resolution may be limited across module boundaries, since object resolution typically follows the import hierarchy.
	- Tools |may| treat unresolved references as errors only in normative mode.
	  

Sections for module docstrings
------------------------------

In addition to the sections described in :ref:`common_sections`
a module docstring |must| have the following structure:

* [DOC-003] -- Module docstrings |must_not| contain sections other than { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`, :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract`, :wtrl_label:`Public_classes`, :wtrl_label:`Public_functions`, :wtrl_label:`Public_types`, :wtrl_label:`Public_variables`, :wtrl_label:`Public_constants` }.
* :wtrl_label:`Contract:`
	- [CON-001] -- The section |must| exist.
	- [CON-002] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CON-028] -- |Must_not| have subsections other than { :wtrl_label:`general`, :wtrl_label:`api` }.
	- :wtrl_label:`general:`
		* [CON-022] -- The subsection |must| exist.
		* [CON-003] -- |Must| contain an explanation of the purpose of the module sufficient to decide
		  whether the module is applicable to a given use case.
	- :wtrl_label:`api:`
		* [CON-029] -- The subsection |may| exist. If it exists:
		* [CON-030] -- |Must| list all sections whose contents define the public method set. The union of these sections defines the public API.
		* [CON-031] -- By default, the API is defined by the sections named "Public_*" listed in :wtrl_label:`Preamble.normative_sections`. An existing subsection :wtrl_label:`api:` overrides the default behaviour.
* :wtrl_label:`Public_classes:`
	- [PCL-001] -- The section |may| exist.
	- [PCL-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PCL-003] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Class>:`
		* [PCL-004] -- <Class> |must| match the pattern of an Identifier.
		* [PCL-005] -- Any number of subsections |may| exist provided :wtrl_label:`<Class>` can be resolved to a class with valid docstring.
		* [PCL-006] -- The content |may| consist of any number of lines.
	- [PCL-014] -- Each class with a valid docstring |should| be listed in :wtrl_label:`Public_classes`.
	- [PCL-015] -- Each class listed in :wtrl_label:`Public_classes` |must| exist in the module.
	- [PCL-016] -- Each entry in :wtrl_label:`Public_classes` |must| refer to a class object.
	- [PCL-017] -- Each class listed in :wtrl_label:`Public_classes` |must| have a valid docstring.
	- [PCL-022] -- A class not listed in :wtrl_label:`Public_classes` |may| have an invalid or missing docstring.
* :wtrl_label:`Public_functions:`
	- [PFN-001] -- The section |may| exist.
	- [PFN-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PFN-003] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Function>:`
		* [PFN-004] -- :wtrl_label:`<Function>` |must| match the pattern of an Identifier.
		* [PFN-005] -- Any number of subsections |may| exist provided :wtrl_label:`<Function>` can be resolved to a function with valid docstring.
		* [PFN-006] -- The content |may| consist of any number of lines.
	- [PFN-008] -- Each function with a valid docstring |should| be listed in :wtrl_label:`Public_functions`.
	- [PFN-009] -- Each function listed in :wtrl_label:`Public_functions` |must| exist in the module.
	- [PFN-010] -- Each entry in :wtrl_label:`Public_functions` |must| refer to a function object and have a valid docstring.
	- [PFN-011] -- A function not listed in :wtrl_label:`Public_functions` |may| have an invalid or missing docstring.
* :wtrl_label:`Public_types:`
	- [PTY-001] -- The section |may| exist.
	- [PTY-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PTY-003] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Type>:`
		* [PTY-004] -- :wtrl_label:`<Type>` |must| match the pattern of an Identifier.
		* [PTY-005] -- Any number of subsections |may| exist provided :wtrl_label:`<Type>` can be resolved to an existing TypeAlias or NewType.
		* [PTY-006] -- The content |may| consist of any number of lines.
	- [PTY-007] -- Each type listed in :wtrl_label:`Public_types` |must| exist in the module.
* :wtrl_label:`Public_variables:`
	- [PVAR-001] -- The section |may| exist.
	- [PVAR-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PVAR-003] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Assignable>:`
		* [PVAR-004] --:wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [PVAR-005] -- Any number of subsections |may| exist provided :wtrl_label:`<Assignable>` can be resolved to an existing variable.
		* [PVAR-006] -- The content |may| consist of any number of lines.
	- [PVAR-013] -- Each variable listed in :wtrl_label:`Public_variables` |must| exist in the module.
	- [PVAR-014] -- If a variable listed in :wtrl_label:`Public_variables` is annotated, it |must| be annotated as :wtrl_type:`Final`.
* :wtrl_label:`Public_constants:`
	- [PCON-001] -- The section |may| exist.
	- [PCON-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PCON-003] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Assignable>:`
		* [PCON-004] -- :wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [PCON-005] -- Any number of subsections |may| exist provided :wtrl_label:`<Assignable>` can be resolved to an existing variable.
		* [PCON-006] -- If the variable is annotated, it |must| be annotated as :wtrl_type:`Final`.
		* [PCON-007] -- The content |may| consist of any number of lines.
	- [PCON-015] -- Each constant listed in :wtrl_label:`Public_constants` |must| exist in the module.
	- [PCON-016] -- Each constant listed in :wtrl_label:`Public_constants` that is annotated |must| be annotated as :wtrl_type:`Final`.

Sections for class docstrings
-----------------------------

In addition to the sections described in :ref:`common_sections`
a class docstring |must| have the following structure:

* [DOC-004] -- Class docstrings |must_not| contain sections other than { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`, :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract`, :wtrl_label:`Derived_from`, :wtrl_label:`Public_classes`, :wtrl_label:`Public_methods`, :wtrl_label:`Public_types`, :wtrl_label:`Public_variables`, :wtrl_label:`Public_constants`, :wtrl_label:`Factory` }.
* :wtrl_label:`Contract:`
	- [CON-004] -- The section |must| exist.
	- [CON-005] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CON-032] -- |Must_not| have subsections other than { :wtrl_label:`general`, :wtrl_label:`constructor`, :wtrl_label:`api`, :wtrl_label:`traits` }.
	- :wtrl_label:`general:`
		* [CON-023] -- The subsection |must| exist.
		* [CON-006] -- |Must| contain an explanation of the purpose of the class sufficient to decide
		  whether the class is applicable to a given use case.
	- :wtrl_label:`constructor:`
		* [CON-007] -- The subsection |must| exist.
		* [CON-008] -- |Should| contain a brief explanation of the constructor or point to special method :wtrl_func:`__init__` with a valid docstring.
	- :wtrl_label:`api:`
		* [CON-009] -- The subsection |may| exist. If it exists:
		* [CON-010] -- |Must| list all sections whose contents define the public method set. The union of these sections defines the public API.
		* [CON-011] -- By default, the API is defined by the sections named "Public_*" listed in :wtrl_label:`Preamble.normative_sections`. An existing subsection :wtrl_label:`api:` overrides the default behaviour.
	- :wtrl_label:`traits:`
		* [CON-012] -- The subsection |may| exist.
		* [CON-013] -- If it exists, it |must| be a list of Identifiers (one per line or comma-separated).
		* [CON-014] -- The subsection |must| list zero or more trait identifiers.
		* [CON-015] -- Each trait identifier |must| match the pattern of an Identifier.
		* [CON-016] -- Trait identifiers |must_not| occur more than once.
		* [CON-017] -- Only the traits listed here are allowed.
		* [CON-018] -- The following trait identifiers are defined by this specification:
			+ :wtrl_value:`final` -- A class marked :wtrl_value:`final` |must_not| be derived from.
			+ :wtrl_value:`abstract` -- A class marked :wtrl_value:`abstract` |must_not| be instantiated directly.
* :wtrl_label:`Derived_from:`
	- [DER-001] -- The section |may| exist. If it exists:
	- [DER-002] -- |Must| list the base classes that contribute public functions, types, constants, attributes, or semantic guarantees.
	- [DER-003] -- Each entry |must| refer to a direct base class of the documented class.
* :wtrl_label:`Public_classes:` (nested/inner classes)
	- [PCL-007] -- The section |may| exist.
	- [PCL-008] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PCL-009] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Class>:`
		* [PCL-010] -- :wtrl_label:`<Class>` |must| match the pattern of an Identifier.
		* [PCL-011] -- Any number of subsections |may| exist provided :wtrl_label:`<Class>` can be resolved to a class with valid docstring.
		* [PCL-012] -- The content |may| consist of any number of lines.
	- [PCL-018] -- Each nested class listed in :wtrl_label:`Public_classes` |must| exist as an attribute on the documented class.
	- [PCL-021] -- Each nested class with a valid docstring |should| be listed in section :wtrl_label:`Public_classes`.
	- [PCL-019] -- Each entry in :wtrl_label:`Public_classes` |must| refer to a class object.
	- [PCL-020] -- Each nested class listed in :wtrl_label:`Public_classes` |must| have a valid docstring.
	- [PCL-023] -- A nested class not listed in :wtrl_label:`Public_classes` |may| have an invalid or missing docstring.
* :wtrl_label:`Public_methods:`
	- [PMET-001] -- The section |may| exist.
	- [PMET-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PMET-003] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Method>:`
		* [PMET-004] -- :wtrl_label:`<Method>` |must| match the pattern of an Identifier.
		* [PMET-005] -- Any number of subsections |may| exist provided :wtrl_label:`<Method>` can be resolved to a method with valid docstring.
		* [PMET-006] -- The content |may| consist of any number of lines.
	- [PMET-008] -- Each method with a valid docstring |should| be listed in section :wtrl_label:`Public_methods`.
	- [PMET-009] -- Each method listed in section :wtrl_label:`Public_methods` |must| exist and be a method/function.
	- [PMET-010] -- Each method listed in section :wtrl_label:`Public_methods` |must| have a valid docstring.
	- [PMET-011] -- A method not listed in :wtrl_label:`Public_methods` |may| have an invalid or missing docstring.
* :wtrl_label:`Public_variables:`
	- [PVAR-007] -- The section |may| exist.
	- [PVAR-008] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PVAR-009] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Assignable>:`
		* [PVAR-010] --:wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [PVAR-011] -- Any number of subsections |may| exist provided :wtrl_label:`<Assignable>` can be resolved to an existing variable.
		* [PVAR-012] -- The content |may| consist of any number of lines.
	- [PVAR-021] -- Each variable listed in :wtrl_label:`Public_variables` |must| exist on the documented class.
	- [PVAR-022] -- If a variable listed in :wtrl_label:`Public_variables` is annotated, it |must| be annotated as :wtrl_type:`Final`.
* :wtrl_label:`Public_constants:`
	- [PCON-008] -- The section |may| exist.
	- [PCON-009] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PCON-010] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Assignable>:`
		* [PCON-011] -- :wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [PCON-012] -- Any number of subsections |may| exist provided :wtrl_label:`<Assignable>` can be resolved to an existing variable.
		* [PCON-013] -- If the variable is annotated, it |must| be annotated as :wtrl_type:`Final`.
		* [PCON-014] -- The content |may| consist of any number of lines.
	- [PCON-021] -- Each constant listed in :wtrl_label:`Public_constants` |must| exist on the documented class.
	- [PCON-022] -- Each constant listed in :wtrl_label:`Public_constants` that is annotated |must| be annotated as :wtrl_type:`Final`.
* :wtrl_label:`Factory:`
	- [FAC-001] -- The section |may| exist.
	- [FAC-002] -- If it contains at least one Normativity Keyword, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [FAC-003] -- If it exists, it |should| list all factory functions with full signature.
	- [FAC-004] -- Each entry in the section |must| have the form of a subsection. Pattern:
	- :wtrl_label:`<Function>:`
		* [FAC-005] -- :wtrl_label:`<Function>` |must| match the pattern of an Identifier.
		* [FAC-006] -- Any number of subsections |may| exist provided :wtrl_label:`<Function>` can be resolved to an existing function.
		* [FAC-007] -- The content |may| consist of any number of lines.


.. _function_sections:

Sections for function/method docstrings
---------------------------------------

In addition to the sections described in :ref:`common_sections`
a function or method docstring |must| have the following structure:

* [DOC-005] -- Function or method docstrings |must_not| contain sections other than { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`, :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract`, :wtrl_label:`Parameters`, :wtrl_label:`Returns`, :wtrl_label:`Raises` }.
* :wtrl_label:`Contract:`
	- [CON-019] -- The section |must| exist.
	- [CON-020] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CON-027] -- |Must_not| have subsections other than { :wtrl_label:`general`, :wtrl_label:`invariants` }.
	- :wtrl_label:`general:`
		* [CON-024] -- The subsection |must| exist.
		* [CON-021] -- |Must| contain an explanation of the purpose of the function sufficient to decide
		  whether the function is applicable to a given use case.
	- :wtrl_label:`invariants:`
		* [CON-025] -- The subsection |may| exist.
		* [CON-026] -- If it exists, it |must| allow multiline free-form text.
* :wtrl_label:`Parameters:`
	- [PAR-001] -- The section |must| exist.
	- [PAR-002] -- It |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PAR-003] -- |Must| list all parameters and an explanation for each parameter
	- :wtrl_label:`<Par>:`
		* [PAR-006] -- :wtrl_label:`<Par>` |must| match the pattern of an Identifier.
		* [PAR-004] -- Each parameter in the function's signature |must| exist here as an entry addressed by :wtrl_label:`<Par>`.
		* [PAR-005] -- The parameter addressed by :wtrl_label:`<Par>` must appear in the function's signature.
* :wtrl_label:`Returns:`
	- [RET-001] -- The section |must| exist.
	- [RET-002] -- It |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [RET-003] -- |Must| explain the return value of the function.
	- [RET-004] -- If the documented object is a function or method with return type :wtrl_type:`bool`, section :wtrl_label:`Returns` |should| mention at least one of the tokens :wtrl_value:`|True|` or :wtrl_value:`|False|`.
	- [RET-005] -- The section |must_not| contain subsections.
* :wtrl_label:`Raises:`
	- [RAI-001] -- The section |must| exist.
	- [RAI-002] -- It |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [RAI-003] -- |Must| list all exception classes that may raise under normal circumstances,
	  that means, the caller has been typechecked with similarly strict rules
	  as the module containing the called function. Pattern:
	- :wtrl_label:`<Exception>:`
		* [RAI-008] -- :wtrl_label:`<Exception>` |must| be a Qualified Identifier.
		* [RAI-004] -- Any number of subsections |may| exist provided :wtrl_label:`<Exception>` can be resolved to an existing (exception) class.
		* [RAI-005] -- The content |may| consist of any number of lines.
		* [RAI-006] -- The content |must| explain the circumstances which must or may lead to raising the exception addressed by :wtrl_label:`<Exception>`.
		* [RAI-007] -- Each exception listed |must| be a subclass of :wtrl_type:`BaseException`.

Sections for inherited method docstrings
----------------------------------------

.. rubric:: Liskov-compatible (informative)

A method is :wtrl_dfn:`Liskov-compatible` if it satisfies the Liskov Substitution Principle (LSP)
in relation to the method it overrides. Tools may check type-level compatibility (e.g. contravariance of arguments and covariance of return types)
if sufficient type information is available. Behavioral consistency (pre-/post-conditions and exception behavior)
is generally not statically verifiable and is therefore out of scope for mandatory validation.

The following section is normative.

In addition to the sections described in :ref:`common_sections`
an inherited method docstring |must| have the following structure:

* [DOC-006] -- Inherited method docstrings |must_not| contain sections other than
  { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`,
  :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract` }.

* :wtrl_label:`Contract:`
	- [CON-033] -- The section |must| exist.
	- [CON-034] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CON-035] -- The section |must_not| have subsections other than { :wtrl_label:`general`, :wtrl_label:`base` }.

	- :wtrl_label:`general:`
		* [CON-036] -- The subsection |must| exist.
		* [CON-037] -- |Must| contain an explanation of the purpose of the method sufficient to decide
		  whether the method is applicable to a given use case.
		* [CON-038] -- |Should| point out in how far the method differs from the base method referenced in :wtrl_label:`Contract.base`.

	- :wtrl_label:`base:`
		* [CON-039] -- The subsection |must| exist.
		* [CON-040] -- The subsection |must| contain exactly one entry.
		* [CON-041] -- The entry |must| be a Qualified Identifier.
		* [CON-042] -- The entry |must| be resolvable to a function or method object.
		* [CON-043] -- The resolved object |must| be a method of a base class of the documented class.
		* [CON-044] -- The name of the resolved object |must| equal the name of the documented method.
		* [CON-045] -- The referenced base method |must| have a valid docstring.
		* [CON-046] -- Tools |should| check type-level Liskov compatibility against the referenced base method if sufficient type information is available.


Coverage rules and intended workflow
------------------------------------

This section is informative.

The Waterloo specification contains a set of rules that connect docstring validity and public API listings
in sections such as :wtrl_label:`Public_classes`, :wtrl_label:`Public_functions`, and :wtrl_label:`Public_methods`.
Taken together, these rules define an intended workflow and an interpretation of documentation "coverage".

In short, Waterloo treats the :wtrl_label:`Public_*` sections as an explicit declaration of public API surface.
Listing an object in a :wtrl_label:`Public_*` section is a commitment: the specification requires the object to exist,
and requires the object to have a valid docstring.

Conversely, the existence of a valid docstring does not automatically make an object part of the public API.
The specification recommends listing documented objects in :wtrl_label:`Public_*` sections, but does not require it.
This supports incremental documentation work, experimentation, and internal documentation without forcing immediate API exposure.

Module-level coverage
^^^^^^^^^^^^^^^^^^^^^

At module level, the specification expresses the following principles:

	* The specification recommends that each class with a valid docstring is listed in :wtrl_label:`Public_classes`
	  (PCL-014).

	* The specification requires that each class listed in :wtrl_label:`Public_classes` has a valid docstring
	  (PCL-017).

	* The specification recommends that each function with a valid docstring is listed in :wtrl_label:`Public_functions`
	  (PFN-008).

	* The specification requires that each entry in :wtrl_label:`Public_functions` refers to a function object and has a valid docstring
	  (PFN-010).

	* The specification requires that each type listed in :wtrl_label:`Public_types` exists in the module
	  (PTY-007).

	* The specification requires that each variable listed in :wtrl_label:`Public_variables` exists in the module
	  (PVAR-013).

	* The specification requires that each constant listed in :wtrl_label:`Public_constants` exists in the module
	  (PCON-015).

Class-level coverage
^^^^^^^^^^^^^^^^^^^^

At class level, the specification expresses the following principles:

	* The specification requires that each class listed in :wtrl_label:`Public_classes` exists as an attribute on the documented class
	  (PCL-018).

	* The specification recommends that each embedded class with a valid docstring is listed in section :wtrl_label:`Public_classes`
	  (PCL-021).

	* The specification recommends that each method with a valid docstring is listed in section :wtrl_label:`Public_methods`
	  (PMET-008).

	* The specification requires that each method listed in section :wtrl_label:`Public_methods` exists and is a method/function
	  (PMET-009).

	* The specification requires that each variable listed in :wtrl_label:`Public_variables` exists on the documented class
	  (PVAR-021).

	* The specification requires that each constant listed in :wtrl_label:`Public_constants` exists on the documented class
	  (PCON-021).

Practical consequence
^^^^^^^^^^^^^^^^^^^^^

These rules allow authors to write many valid docstrings without immediately declaring the documented objects as public.
Only objects explicitly listed in :wtrl_label:`Public_*` sections are treated as part of the public API surface and are
therefore subject to strict coverage expectations.

Distinction :wtrl_label:`Description` vs :wtrl_label:`Notes`
------------------------------------------------------------

This section is informative.

The :wtrl_label:`Description` and :wtrl_label:`Notes` sections overlap thematically. We would like
to suggest the following semantics: :wtrl_label:`Description` describes the object to be documented for normal use,
whereas :wtrl_label:`Notes` are intended more for edge cases, caveats, race conditions, restrictions, and todos.
We have deliberately implemented :wtrl_label:`Notes` as non-normative in order to prevent runaway growth
of self-defined normative sections. Notes of a normative nature should be added to the :wtrl_label:`Contract` section instead.

Distinction :wtrl_label:`general` vs :wtrl_label:`invariants`
-------------------------------------------------------------

This section is informative.

The :wtrl_label:`Contract.general` and :wtrl_label:`Contract.invariants` subsections overlap thematically.
We would like to suggest the following semantics: :wtrl_label:`Contract.general` describes the object to be documented
for normal use, focusing on its purpose and applicability, whereas :wtrl_label:`Contract.invariants` is intended for
non-trivial properties that are expected to hold for all valid inputs and states.

Invariants are typically statements about closure properties, idempotence, determinism, round-trip behaviour,
and other guarantees that are especially useful for targeted automated tests.
Invariants of a normative nature should be placed in :wtrl_label:`Contract.invariants` rather than being scattered
throughout free-form prose.

Invariants may be more technical in nature and may refer to internal representations such as an AST or a DocstringTree.
