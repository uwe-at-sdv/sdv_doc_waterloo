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
.. |Self| replace:: :wtrl_value:`Self`
.. |None| replace:: :wtrl_value:`None`
.. |True| replace:: :wtrl_value:`True`
.. |False| replace:: :wtrl_value:`False`
.. |empty| replace:: :wtrl_value:`<empty>`

.. |LastReview| replace:: **Last review**
.. |ObsoleteRules| replace:: **Obsolete rules**
.. |Rationale| replace:: **Rationale** (informative)
.. |Informative| replace:: **Informative**

.. _chapter_format:

Docstring format
================

.. _section_definitions: 

Definitions
-----------

This section is normative.

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

Terminology
-----------

This section is informative.

.. rubric:: Documentation Coverage

:wtrl_dfn:`Documentation Coverage` is the property of a documented code base
that all objects explicitly declared as public are accompanied by valid
Waterloo docstrings.

An object is considered *explicitly declared as public* if it is listed in
a section of the form :wtrl_label:`Public_*` in the enclosing documentation
scope (module or class).

Documentation coverage is evaluated solely based on the presence, structure,
and validity of docstrings, and is independent of the semantic correctness
or completeness of their contents.

.. rubric:: Lint rule

A :wtrl_dfn:`lint rule` is a normative requirement that can be checked unambiguously by a tool against the docstring text
and the available program context (e.g. signatures, importability, symbol tables).
Normative guidance that is not intended to be tool-enforced does not require a rule ID.

.. rubric:: Liskov-compatible

A method is :wtrl_dfn:`Liskov-compatible` if it satisfies the Liskov Substitution Principle (LSP)
in relation to the method it overrides. Tools may check type-level compatibility (e.g. contravariance of arguments and covariance of return types)
if sufficient type information is available. Behavioral consistency (pre-/post-conditions and exception behavior)
is generally not statically verifiable and is therefore out of scope for mandatory validation.

.. rubric:: Scope Monotonicity Rule

A rule defined in chapter :ref:`chapter_scopes_and_visibility`, which states that each object
(depending on the circumstances) should have a scope that is no more restrictive than any
of its dependent objects. For example, a class with the scope :wtrl_value:`core`
cannot have nested classes or methods with the scope :wtrl_value:`public` -- If this were allowed,
a :wtrl_value:`public` user would have to deal with objects that are explicitly restricted
to the smaller group of :wtrl_value:`core` users, which does not make sense.

Specification conventions
-------------------------

This section is informative.

The specification of rule-based normative topics throughout this document
follows a common structural pattern. The purpose of this pattern is to ensure
consistency, readability, and long-term maintainability of the specification
text.

A specification block may consist of the following components, in the order
listed below:

* **Normative rules**

  One or more rules identified by rule IDs.
  These define the formal semantics and validation requirements.

* **Obsolete rules** (optional)

  A list of previously defined rules that have been superseded.
  Each obsolete rule should indicate the version in which it became obsolete
  and, if applicable, the rule that replaces it.

* **Rationale** (informative, optional)

  Explanatory text describing the intent, design considerations, or background
  of the preceding rules.
  The rationale does not introduce additional normative requirements.

* |LastReview| (editorial, optional)

  A date indicating the most recent editorial review of the section.
  This item has no normative effect.

Not all components are mandatory. Their presence depends on the complexity,
maturity, and historical evolution of the topic under consideration.
This structural pattern serves as a guideline for authors and editors of this
specification. It is intended to promote uniformity without constraining future
refinement.

.. _section_meta: 

Meta
----

This section is normative.

In this section, we specify that all normative rules and error codes for defining the Waterloo project are given IDs, and how we construct these IDs.
We do this by the following set of rules.

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
  When a rule is merely mentioned but not introduced, square brackets |should_not| be used.

* [META-005] -- Obsolete rule IDs, when mentioned in prose, |must_not| be introduced with square brackets;
  square brackets |must| be reserved for the point where a rule is defined.

Rule taxonomy
-------------

This section is informative.

The prefixes of rule IDs have a mnemonic function.
The following list explains the mnemonic prefixes and their semantics.

.. rubric:: Meta

* META: Meta: rules defining the concept of rules

.. rubric:: Parsing and validation

* DOC: Docstrings in general
* PNB: Partial Normativity Bugs
* PRSR: Parser
* TKN: Tokenizer

.. rubric:: Helper ruleset

* LQID: List of [Qualified] Identifiers

.. rubric:: Sections and subsections

* CON: All profiles: Section :wtrl_label:`Contract`

* CCLO: Profile :wtrl_value:`class`: Section :wtrl_label:`Class_overview`
* CMTO: Profile :wtrl_value:`class`: Section :wtrl_label:`Method_overview`
* CPCL: Profile :wtrl_value:`class`: Section :wtrl_label:`Public_classes`
* CPMT: Profile :wtrl_value:`class`: Section :wtrl_label:`Public_methods`
* CPTYP: Profile :wtrl_value:`class` Section :wtrl_label:`Public_types`
* CPVAR: Profile :wtrl_value:`class`: Section :wtrl_label:`Public_variables`
* CPCON: Profile :wtrl_value:`class`: Section :wtrl_label:`Public_constants`

* DEF: All profiles: Section :wtrl_label:`Definitions`
* DER: Profile :wtrl_value:`class`: Section :wtrl_label:`Derived_from`
* DESC: All profiles: Section :wtrl_label:`Description`
* FAC: Profile :wtrl_value:`class`: Section :wtrl_label:`Factory`

* MCLO: Profile :wtrl_value:`module`: Section :wtrl_label:`Class_overview`
* MFNO: Profile :wtrl_value:`module`: Section :wtrl_label:`Function_overview`
* MPCL: Profile :wtrl_value:`module`: Section :wtrl_label:`Public_classes`
* MPFN: Profile :wtrl_value:`module`: Section :wtrl_label:`Public_functions`
* MPTYP: Profile :wtrl_value:`module` Section :wtrl_label:`Public_types`
* MPVAR: Profile :wtrl_value:`module`: Section :wtrl_label:`Public_variables`
* MPCON: Profile :wtrl_value:`module`: Section :wtrl_label:`Public_constants`

* NOTE: All profiles: Section :wtrl_label:`Notes`
* PAR: Profiles :wtrl_value:`function`, :wtrl_value:`method`: Section :wtrl_label:`Parameters`
* PRE: All profiles: Section :wtrl_label:`Preamble`
* RAI: Profiles :wtrl_value:`function`, :wtrl_value:`method`: Section :wtrl_label:`Raises`
* RET: Profiles :wtrl_value:`function`, :wtrl_value:`method`: Section :wtrl_label:`Returns`
* SCP: All profiles: Subsection :wtrl_label:`scope`
* SEE: All profiles: Section :wtrl_label:`See_also`
* STA: All profiles: Subsection :wtrl_label:`status`
* TERM: All profiles: Section :wtrl_label:`Terminology`

.. rubric:: Tools and extensions

* TOOL: Error messages from :wtrl_cmd:`waterlint` (or other tools)
* JPTR: Error messages related to JSON Pointer references in tool-generated JSON
* JSCH: Error messages related to JSON and JSON Schema
* AXMPL: Error messages related to example mapping (e.g. for :wtrl_cmd:`waterlint add-example-json`)
* CARVE: Error messages related to carving walk input into JSON objects
* RHTM: Error messages related to rendering HTML (e.g. for :wtrl_cmd:`waterlint render-html5`)
* XTNSN: Error messages related to extensions (e.g. for IDEs)
* MCPS: Error messages returned by an MCP server
* MCPA: Error messages returned by the MCP admin helper and related admin flows
* DCKR: Error messages related to rendering Docker builder output (e.g. for :wtrl_cmd:`waterlint render-docker`)
* XPLN: Error messages related to explain commands (e.g. for :wtrl_cmd:`waterlint explain-section` and :wtrl_cmd:`waterlint explain-subsection`)

.. rubric:: Miscellaneous

* VLII: Warning for a section or subsection that violates the LoII principle.
  The warning will remain in place until the section or subsection is generally accepted
  and recognized as having practical benefits that outweigh the LoII principle.

.. rubric:: Obsolete

* PTY: Profiles :wtrl_value:`module`, :wtrl_value:`class`: Section :wtrl_label:`Public_types`
* PVAR: Profiles :wtrl_value:`module`, :wtrl_value:`class`: Section :wtrl_label:`Public_variables`
* PCON: Profiles :wtrl_value:`module`, :wtrl_value:`class`: Section :wtrl_label:`Public_constants`


The structure of Waterloo docstrings
------------------------------------

This section is informative.

This section defines the structure of Waterloo docstrings.
It does so in human-readable form. The structure is presented as lists for the various sections
with embedded lists for subsections. The following patterns occur in any order:

.. code:: none

	<Section>:
		<Subsection>:
			<Free-Form-Content>
		...
		<Subsection>:
			<Itemized-Content>
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
		<Itemized-Content>
	...
	<Section>:
		<List-Of-Identifiers>
	...
	<Section>:
		<List-Of-Qualified-Identifiers>

In the patterns above, :code:`<Free-Form-Content>` denotes paragraph-capable
text. It may contain ordinary prose as well as explicitly marked bullet lists
or enumerations. This form is typically used where explanation, descriptive
structure, or more flexible text layout is required.

:code:`<Itemized-Content>` denotes line-oriented content that is interpreted as
a sequence of individual items. In practice, this form is often used for
contract-like statements such as obligations, preconditions, postconditions, or
other entries that are naturally read item by item rather than as connected
prose.

On the docstring level, both forms are represented as indented text blocks.
They differ primarily in their intended interpretation and in the way tools and
output layers are expected to present them.
For systematic examples and test cases that illustrate this distinction, see
:ref:`flow_control`.

The label string is defined as the substring between the first non-indentation character of the line and the last colon in the line.
Since a label line must not contain any non-whitespace characters after that last colon, this rule is unambiguous.
Tools must reject a label line that contains any non-whitespace characters after the last colon.

A section label is always an identifier followed by a colon. Subsection labels may be identifiers,
qualified identifiers or plain non-empty human-readable string followed by a colon. The precise form
of the subsection label depends on the subsection type and purpose. In either case it matches a string
parsed greedily and closed by colon.

The indentation in the patterns above reflects the (relative) indentation for sections, subsections, and content in the docstring.

Conventions
-----------

This section is informative.

We shall use a simple dot notation in order to refer to subsections in the docstring format, like :wtrl_label:`Preamble.normative_sections` or :wtrl_label:`Definitions.<DefItem>`.

Building the AST
----------------

This section is normative.

The Abstract Syntax Tree (AST) is created in two steps. In the first step ("tokenization")
the docstring is transformed into an intermediate tree representation
as defined in this section. In the second step ("parsing"),
the intermediate representation is transformed into the AST.

We allow two indentation schemes named :wtrl_dfn:`TAB`
(using tab, ASCII 0x09, as indentation unit)
and :wtrl_dfn:`SPC4`
(using four spaces, ASCII 0x20, as indentation unit).
The indentation scheme |must_not| be mixed within a single docstring.

The grammar of the tokenizer in Pseudo-EBNF is:

.. code:: none

	(* Possible ways to indent *)
	spc         = "\x20" ;
	tab         = "\x09" ;
	newline     = "\n" | "\r\n" ;
	backslash   = "\x5c" ;
	ws_char     = spc | tab ;
	non_ws_char = ? all characters but spc and tab ? ;
	non_nl_char = ? all characters but newline ? ;

	(* either *)
	indent_unit = tab ;
	(* or *)
	indent_unit = spc, spc, spc, spc ;
	(* chosen by analyzing leading whitespace of the first indented non-empty line *)

	(* A docstring consists of a set of sections *)
	wldocstring = { section } ;

	(* A section is one logical line plus an optional nested block *)
	section     = indent_token, logical_line, [ block ] ;

	block       = indent_increase, { section }, indent_decrease ;

	(* A logical line is one or more physical lines joined by trailing backslash.
	   Constraint: all physical lines of one logical line have the same indentation level. *)
	logical_line = physical_line, { continuation } ;

	(* A physical line has non-whitespace content *)
	physical_line = content, newline ;

	(* Continuation: previous content ends with backslash (ignoring trailing whitespace).
	   The following physical line is joined; one ASCII space is inserted at the join point. *)
	continuation = indent_nochange, content_cont, newline ;

	(* Content of the first physical line: must not start with ws *)
	content      = non_ws_char, { non_nl_char } ;

	(* Content of a continued physical line: same constraint *)
	content_cont = non_ws_char, { non_nl_char } ;

	(* Abstraction of indentation *)
	indent_increase = ? indentation increases by one indent_unit ? ;
	indent_decrease = ? indentation decreases by one indent_unit ? ;
	indent_nochange = ? indentation remains unchanged ? ;
	indent_token    = ? current indentation string, a multiple of indent_unit ? ;

The tokenizer operates on :wtrl_dfn:`logical lines`.

A logical line is the result of joining one or more physical lines
according to the rule :wtrl_type:`logical_line` defined above.
Physical lines serve only as input units and have no independent
semantic meaning once logical lines have been formed.

Empty lines and whitespace-only lines do not form logical lines.
They |must| be ignored for indentation analysis and |must| not affect
the tokenizer state.

The normative rules derived from this grammar are:

	* [TKN-001] -- The indentation scheme |must| be consistent within a docstring.
	* [TKN-002] -- In indentation scheme SPC4, indentation |must| be a multiple of 4.
	* [TKN-003] -- The indentation scheme |must| be either TAB or SPC4.
	* [TKN-004] -- Indentation from one logical line to the next |must_not| increase by more than one unit.
	* [TKN-005] -- A physical content line |may| be continued on the next physical line
	  by placing a backslash (ASCII 92) as the last non-whitespace character.
	* [TKN-006] -- Line continuation according to TKN-005 |must| only join lines
	  at the same indentation level.
	* [TKN-007] -- A physical content line that ends with a backslash according to TKN-005
	  |should_not| be the last physical line within an indentation block.
	* [TKN-008] -- Tools |must| join continued lines by removing the backslash
	  and newline and inserting a single ASCII space character at the join position.
	* [TKN-009] -- Tools |must| emit a warning if
		- **either** a trailing backslash used for line continuation is not escaped,
		- **or** the enclosing Python string literal is not declared as a raw string.
	* [TKN-999] -- The tokenizer implementation |must| not produce undefined behavior.
	  Informative: This rule serves as a catch-all for unspecified tokenizer errors.

In order to describe the tokenizer state, we define the following type
(in Python for practical reasons):

.. code:: python

	DocstringTree = List[ Union[ str, "DocstringTree"]]

A :wtrl_dfn:`DocstringTree` is a value of this type.

The tokenizer maintains the following state:

	1. A DocstringTree (initial state: :wtrl_value:`[]`),
	   represented by a variable such as :wtrl_var:`target`.
	2. A stack whose elements reference :wtrl_var:`target`
	   or any subtree thereof (see recursive definition of :wtrl_type:`DocstringTree`).
	   The initial state is :wtrl_value:`[target]`.
	   The stack is represented by a variable :wtrl_var:`stack`.
	3. An integer variable :wtrl_var:`cur_indent` representing the current indentation level.
	   The initial value is computed as the greatest common indentation
	   over all non-empty physical lines of the docstring,
	   measured in indent units (TAB or SPC4).

For each logical line, processed sequentially,
the tokenizer performs the following:

	If the indentation level remains unchanged,
	the logical line is appended as a string
	to the subtree referenced by the top element of :wtrl_var:`stack`.

	If the indentation level increases by one indent unit,
	an empty DocstringTree is appended to the subtree referenced
	by the top element of :wtrl_var:`stack`,
	and a reference to this new subtree is pushed onto :wtrl_var:`stack`.

	If the indentation level decreases by :wtrl_value:`n` indent units,
	an element is popped from :wtrl_var:`stack`
	for each of the :wtrl_value:`n` indentation levels.

The resulting DocstringTree contains only two kinds of elements:
strings and lists.

The tokenizer |must| produce a DocstringTree in which each nested list
corresponds to exactly one indentation increase relative to its parent.

The parser then transforms the DocstringTree into an Abstract Syntax Tree (AST).
The parser |must| treat the top-level DocstringTree as a sequence of candidate
sections and interpret strings and nested lists according to the section and
subsection rules defined below.

In particular, the tokenizer does not decide whether a given logical line is a
valid section label, subsection label, or content line. These classifications
are determined only during parsing, based on the rule-based section and
subsection specifications in section :ref:`common_sections` ff.

Parsing is successful if and only if the structure of the DocstringTree is
compatible with those section and subsection requirements.

Inline markup in free-form content
----------------------------------

This subsection is normative.

Waterloo docstrings are primarily plain text. However, a small set of inline markup tokens is defined to allow
machine-verifiable references and consistent rendering in target formats (e.g. reST/Sphinx).

Inline markup tokens |may| occur in free-form content lines.
Inline markup tokens |must_not| occur in:

	* section labels,
	* subsection labels,
	* list entries in sections that are defined as "List-Of-Identifiers" or "List-Of-Qualified-Identifiers".

Tokens
^^^^^^

This subsection is normative.

The set of tokens currently available is:

	* Token :wtrl_lit:`\|Must\|`, :wtrl_lit:`\|must\|`, ... as listed in :ref:`rubric_normativity_keywords`.
		- Usage: :wtrl_lit:`|Must|`, :wtrl_lit:`|must_not|`, ...

	* Token :wtrl_lit:`\|term\|`
		- Usage: :wtrl_lit:`|term|\`my_term\``
		- The argument (inside the tick delimiters) |must| match the pattern of an Identifier.
		- The argument |must| refer to an existing definition item :wtrl_label:`Definitions.<DefItem>`.
		- [DEF-007] -- If token :wtrl_lit:`|term|` is used at least once, section :wtrl_label:`Definitions` |must| exist and be listed as normative.
		- [DEF-008] -- Each token :wtrl_lit:`|term|` |must| reference a defined or inherited term in section :wtrl_label:`Definitions`.
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

	* Tokens :wtrl_lit:`|attr|`, :wtrl_lit:`|class|`, :wtrl_lit:`|cmd|`, :wtrl_lit:`|dfn|`, :wtrl_lit:`|file|`, :wtrl_lit:`|func|`, :wtrl_lit:`|label|`, :wtrl_lit:`|key|`, :wtrl_lit:`|lit|`, :wtrl_lit:`|mod|`, :wtrl_lit:`|norm|`, :wtrl_lit:`|op|`, :wtrl_lit:`|opt|`, :wtrl_lit:`|pkg|`, :wtrl_lit:`|ref|`, :wtrl_lit:`|tag|`, :wtrl_lit:`|type|`, :wtrl_lit:`|url|`, :wtrl_lit:`|value|`, :wtrl_lit:`|var|`, :wtrl_lit:`|var_type|`
		- Usage: Tools |must| accept the form :wtrl_lit:`|role|\`content\``,
		  where :wtrl_lit:`role` is one of the above tokens and
		  :wtrl_lit:`content` is a non-empty string that does not contain backticks.
		- These tokens |must| only be used inside Waterloo docstrings.
		  Using them in accompanying reST documents |may| trigger warnings
		  or errors from the Sphinx builder.
		- These tokens represent semantic roles. When building the Abstract Syntax Tree,
		  tools |must| preserve them without modification.
		- Tools translating to a target format (e.g. :wtrl_lit:`reST`)
		  |must| map these roles to well-defined constructs in the target format.
		- Semantic role :wtrl_lit:`|norm|` identifies a normativity keyword as a meta-token.
		  It is primarily useful when discussing normativity keywords themselves.
		- Informative: The tokens improve semantic clarity for human readers
		  and may assist automated tools or AI agents. Tools that are not tied
		  to a specific rendering target may ignore them.

As mentioned above, the tokenized form using the pipe character "\|"
is defined only within Waterloo docstrings.
The Waterloo Sphinx extension additionally defines equivalent roles
in native reST form, e.g. :wtrl_lit:`:wtrl_file:\`path/to/file\``.

Textflow tokens
^^^^^^^^^^^^^^^

This subsection is informative.
It describes the current interpretation used by output layers, but the
description is not yet intended as a complete normative definition.

Textflow tokens are interpreted at the rendering stage and influence the
visual structure of the output without affecting the logical structure
of the docstring.

.. rubric:: Paragraph token

A line starting with a single pipe character :wtrl_lit:`|`,
optionally followed only by whitespace, denotes a paragraph boundary.
This token is used to visually separate blocks of text into distinct
paragraphs in the rendered output.


.. rubric:: List tokens

The following characters at the beginning of a line are interpreted as
list markers:

	:wtrl_lit:`*` :wtrl_lit:`+` :wtrl_lit:`-` :wtrl_lit:`#`

A list marker is recognized only if it is immediately followed by a
space character (ASCII 32).

Consecutive lines starting with a list marker form a list block.
List nesting is determined by the order of occurrence of distinct list
markers within such a block. Each distinct marker introduces
a new nesting level within the block.
Indentation of lines within a list block |must_not| be used to express
nesting. Nesting |must| be determined solely by the choice of list marker.

The marker :wtrl_lit:`#` denotes an ordered list. In the current
implementation, ordered lists are rendered using Arabic numerals
followed by a period.





Semantic role :wtrl_lit:`|ref|`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This subsection is normative.

Semantic role :wtrl_lit:`|ref|` is used to create references.
The following forms are supported:

	* :wtrl_lit:`|ref|\`Name <DocutilsLabel>\`` --
	  A reference to a :wtrl_mod:`docutils` label,
	  equivalent to :wtrl_lit:`:ref:\`Name <DocutilsLabel>\``.

	* :wtrl_lit:`|ref|\`Name <https://some.url>\`` --
	  A reference to an external HTTP or HTTPS target.

	* :wtrl_lit:`|ref|\`Name <wtrl://Module.Class.Object>\`` --
	  A reference to the documentation of a Waterloo object.
	  The object path |must| be resolvable by the Waterloo name resolution mechanism.
	  Partial qualification is permitted if the reference can be resolved
	  unambiguously in the current resolution context.

In HTML rendering, the visible label is preserved even when the target
cannot be turned into a link. The target part is still parsed so that
it can be resolved when possible, but the displayed text remains the
label.

Current implementation limitation:

	An object defined in a different document is reachable via
	:wtrl_lit:`|ref|` only if the target document is built before
	the document containing the reference.


Examples
^^^^^^^^

This subsection is informative.

	* :wtrl_lit:`|Must| return |None| if no result is available.`
	* :wtrl_lit:`|Must| return |Self| to support fluent APIs.`
	* :wtrl_lit:`|Must| accept a |term|\`Qualified_Identifier\` as input.`


Rules not bound to a particular section
---------------------------------------

This section is normative.

* [DOC-001] -- Each module, class, function, or method object subject to validation |must| have a docstring.
* [DOC-007] -- The docstring |must_not| be empty after whitespace-stripping.
* [DOC-002] -- Validation |must| only be applied to modules, classes, functions, or methods; other object types |must_not| be validated.

* [PRSR-001] -- Sections and subsections |must| start with a label line, as specified below.
* [PRSR-002] -- The line containing the section or subsection label |must| start with a non-empty label string after stripping indentation.
* [PRSR-003] -- The label string |must| be followed by a colon (ASCII 58).
* [PRSR-004] -- No characters other than optional whitespace |may| follow the colon on a label line.
* [PRSR-005] -- The label of a section |must| match the pattern of an Identifier followed by a colon.
* [PRSR-006] -- The label of a subsection |may| be any non-empty human-readable string followed by a colon.
* [PRSR-007] -- Any section label |must_not| occur more than once on a docstring.
* [PRSR-008] -- Any subsection label |must_not| occur more than once inside its parent section.

The following set of rules applies to both lists of Identifiers and lists of
Qualified Identifiers.
Whenever rule LQID-001 is referenced, the surrounding context |must| explicitly
state whether it applies to Identifiers or to Qualified Identifiers.
[Rules last reviewed on 2026-03-03]

* [LQID-001] -- Lists of [Qualified] Identifiers |must| obey rules LQID-002 through LQID-005.
* [LQID-002] -- Each logical line |may| contain zero or more [Qualified] Identifiers, separated by commas.
* [LQID-003] -- Whitespace surrounding each [Qualified] Identifier |must| be stripped by tools.
* [LQID-004] -- Each [Qualified] Identifier |must| occur at most once in the resulting list.
* [LQID-005] -- Tools |must| treat the result as a flat list of [Qualified] Identifiers, without preserving line structure or grouping.
* [LQID-006] -- If a CSV list is wrapped across multiple physical lines, every non-final physical line |must| end with a comma.

The following warning rule applies when a section appears in a docstring but violates the LoII principle.
This happens, for example, when definitions are imported from a module docstring into a class, function, or method docstring.
Since definitions are normative, that import introduces non-locality.

* [VLII-001] -- A warning with this rule ID |may| be issued if a section appears in a docstring
  that violates the LoII principle. Informative: The section that triggers this warning is
  not deprecated unless explicitly stated.

Normativity keyword handling
----------------------------

This section is normative.

The following rules apply to free-form textual content
within normative sections. They ensure that normativity
keywords are used in a machine-detectable and unambiguous way.
In the following rules "WS" stands for one or more whitespace characters.

* [PNB-001] -- Tools |must| detect the token sequences
  :wtrl_value:`|must|/|Must|` + WS +  :wtrl_value:`not/NOT`, :wtrl_value:`|should|/|Should|` + WS + :wtrl_value:`not/NOT`, and :wtrl_value:`|may|/|May|` + WS + :wtrl_value:`not/NOT`
  when they occur within a single logical content line.

* [PNB-002] -- If :wtrl_value:`|must|/|Must|` + WS +  :wtrl_value:`not/NOT` or :wtrl_value:`|should|/|Should|` + WS +  :wtrl_value:`not/NOT` is detected,
  tools |must| emit at least a warning.
  Informative: Use :wtrl_value:`|must_not|/|Must_not|` or :wtrl_value:`|should_not|/|Should_not|` instead.

* [PNB-003] -- If the token sequence :wtrl_value:`|may|/|May|` + WS +  :wtrl_value:`not/NOT` is detected,
  tools |must| emit at least a warning.
  Informative: The phrase "may not" is ambiguous in English
  and |should| be avoided in normative text.

* [PNB-004] -- Tools |should| warn if free-form textual content of normative
  sections and subsections contains :wtrl_value:`must`, :wtrl_value:`Must`,
  :wtrl_value:`should`, :wtrl_value:`Should`, :wtrl_value:`may`, or
  :wtrl_value:`May` outside Normativity Keyword token form and outside
  single-quoted, double-quoted, or backtick-quoted text.
  Informative: Use :wtrl_value:`|must|`, :wtrl_value:`|Must|`,
  :wtrl_value:`|should|`, :wtrl_value:`|Should|`,
  :wtrl_value:`|may|`, or :wtrl_value:`|May|` when the statement is
  intended to be normative.



Sections and subsections
------------------------

This section is normative.

Section property overview
^^^^^^^^^^^^^^^^^^^^^^^^^

This subsection is informative.

The following table gives an overview of common structural properties of
sections and subsections. In particular, it summarizes:

* the expected content kind,
* the typical normativity status, and
* the main rationale for using that form.

The table is intended as an orientation aid and as a preview of the more
detailed rule-based specifications below. The rules in the following
subsections remain the single source of truth.

In the `Normativity` column, `Not applicable` means that the specification does
not assign a normativity status because the corresponding subsection belongs to
the preamble and serves as metadata.

.. list-table::
   :header-rows: 1

   * - Section or subsection
     - Content kind
     - Normativity
     - Rationale
   * - :wtrl_label:`Preamble.profile`
     - identifier
     - Not applicable
     - Implied by content kind
   * - :wtrl_label:`Preamble.normative_sections`
     - list of identifiers
     - Not applicable
     - Implied by content kind
   * - :wtrl_label:`Preamble.status`
     - identifier
     - Not applicable
     - Implied by content kind
   * - :wtrl_label:`Preamble.scope`
     - list of identifiers
     - Not applicable
     - Implied by content kind
   * - :wtrl_label:`Definitions.<item>`
     - free-form text
     - Normative
     - Needs paragraph-capable text
   * - :wtrl_label:`Definitions._inherit`
     - list of identifiers
     - Normative
     - Implied by content kind
   * - :wtrl_label:`Terminology.<item>`
     - free-form text
     - Non-normative
     - Needs paragraph-capable text
   * - :wtrl_label:`Contract.general`
     - itemized text
     - Normative
     - Line-by-line contract
   * - :wtrl_label:`Contract.constructor`
     - itemized text
     - Normative
     - Line-by-line contract
   * - :wtrl_label:`Contract.base`
     - qualified identifier
     - Normative
     - Implied by content kind
   * - :wtrl_label:`Contract.traits`
     - list of identifiers
     - Normative
     - Implied by content kind
   * - :wtrl_label:`Contract.invariants`
     - itemized text
     - Normative
     - Line-by-line contract
   * - :wtrl_label:`Contract.requires`
     - itemized text
     - Normative
     - Line-by-line contract
   * - :wtrl_label:`Contract.ensures`
     - itemized text
     - Normative
     - Line-by-line contract
   * - :wtrl_label:`Description`
     - free-form text
     - Can be both
     - Needs paragraph-capable text
   * - :wtrl_label:`Derived_from`
     - list of qualified identifiers
     - Normative
     - Implied by content kind
   * - :wtrl_label:`Factory.<item>`
     - itemized text
     - Normative
     - Line-by-line contract
   * - :wtrl_label:`Public_classes`
     - list of qualified identifiers
     - Normative
     - Implied by content kind
   * - :wtrl_label:`Public_functions`
     - list of qualified identifiers
     - Normative
     - Implied by content kind
   * - :wtrl_label:`Public_methods`
     - list of qualified identifiers
     - Normative
     - Implied by content kind
   * - :wtrl_label:`Class_overview.<item>`
     - free-form text
     - Non-normative
     - Descriptive text preferred
   * - :wtrl_label:`Method_overview.<item>`
     - free-form text
     - Non-normative
     - Descriptive text preferred
   * - :wtrl_label:`Function_overview.<item>`
     - free-form text
     - Non-normative
     - Descriptive text preferred
   * - :wtrl_label:`Public_types.<item>`
     - free-form text
     - Normative
     - Needs paragraph-capable text
   * - :wtrl_label:`Public_variables.<item>`
     - free-form text
     - Normative
     - Needs paragraph-capable text
   * - :wtrl_label:`Public_constants.<item>`
     - free-form text
     - Normative
     - Needs paragraph-capable text
   * - :wtrl_label:`Parameters.<item>`
     - free-form text
     - Normative
     - Needs paragraph-capable text
   * - :wtrl_label:`Returns`
     - free-form text
     - Normative
     - Needs paragraph-capable text
   * - :wtrl_label:`Raises.<item>`
     - itemized text
     - Normative
     - Line-by-line contract
   * - :wtrl_label:`Notes.<item>`
     - free-form text
     - Non-normative
     - Needs paragraph-capable text
   * - :wtrl_label:`See_also`
     - list of qualified identifiers
     - Can be both
     - Implied by content kind

.. _common_sections:

Common sections for all profiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :wtrl_label:`Preamble:`
	- [PRE-001] -- The section |must| exist and it |must| be the first of all sections.
	- [PRE-002] -- The section |must_not| list itself in :wtrl_label:`normative_sections`.
	- [PRE-015] -- |Must_not| have subsections other than { :wtrl_label:`profile`, :wtrl_label:`normative_sections`, :wtrl_label:`status`, :wtrl_label:`scope`}.
	- :wtrl_label:`profile:`
		* [PRE-003] -- The subsection |must| exist.
		* [PRE-004] -- The subsection |must| have exactly one entry.
		* [PRE-014] -- The entry |must| match the pattern of an Identifier.
		* [PRE-005] -- The entry |must| be one of {:wtrl_value:`module`, :wtrl_value:`class`, :wtrl_value:`function`, :wtrl_value:`method`, :wtrl_value:`inherited_method`}.
	- :wtrl_label:`normative_sections:`
		* [PRE-006] -- The subsection |must| exist.
		* [PRE-021] -- The content |must| be a list of Identifiers according to rule LQID-001. In this context, "Identifier" (not "Qualified Identifier") applies.
		* [PRE-011] -- The subsection |must| list the normative sections of the documentation block.
		* [PRE-012] -- Each section listed in this subsection |must| exist.
		* [PRE-013] -- Each section or subsection in the docstring that contains a Normativity Keyword must be listed in this subsection.
	- :wtrl_label:`status:`
		* [PRE-016] -- The subsection |must_not| exist unless specified explicitly for a given profile.
	- :wtrl_label:`scope:`
		* [SCP-001] -- The subsection |may| exist.
		* [SCP-002] -- The content |must| be a list of Identifiers according to LQID-001.
		* [SCP-003] -- Entries in :wtrl_label:`Preamble.scope` |must| be valid scope identifiers as defined in :ref:`section_scope_values`.
		* [SCP-010] -- A missing or empty subsection |must| be interpreted as :wtrl_value:`public`.
		* [SCP-004] -- Scope assignments and internal references |must| obey the :wtrl_term:`Scope Monotonicity Rule` as defined in :ref:`chapter_scopes_and_visibility`.
		* [SCP-005] -- For every internal reference introduced by sections
		  :wtrl_label:`Public_classes`, :wtrl_label:`Public_functions`, or :wtrl_label:`Public_methods`,
		  the source object |must| be the documented module or class and the target object
		  |must| be the referenced public class/function/method.
		  The source object |must| be at least as public as the target object.
		  Validators |must| apply the scope
		  compatibility test defined in :ref:`section_scope_monotonicity_rule`.
		  Any violation of the scope compatibility test in this case |must| be reported as an error.
		* [SCP-006] -- If section :wtrl_label:`See_also` is listed in
		  :wtrl_label:`Preamble.normative_sections`, then for every internal reference in
		  :wtrl_label:`See_also` that resolves to a Waterloo-documented object, the source object
		  |must| be the referenced object and the target object |must| be the documented module or class.
		  The source object |must| be at least as public as the target object.
		  Validators |must| apply the scope compatibility test defined in
		  :ref:`section_scope_monotonicity_rule`.
		  Any violation of the scope compatibility test in this case |must| be reported as an error.
		* [SCP-007] -- If section :wtrl_label:`See_also` is not listed in
		  :wtrl_label:`Preamble.normative_sections`, then for every internal reference
		  in :wtrl_label:`See_also` that resolves to a Waterloo-documented object, the source
		  object |must| be the referenced object and the target object |must| be the documented module or class.
		  The source object |must| be at least as public as the target object.
		  Validators |must| apply the scope compatibility test defined in
		  :ref:`section_scope_monotonicity_rule`.
		  Any violation of the scope compatibility test in this case |must| be reported as a warning.
		* [SCP-008] -- For profile :wtrl_value:`inherited_method`, subsection
		  :wtrl_label:`Contract.base` introduces an internal reference from the derived
		  method to the referenced base method. The source object |must| be the referenced base method and the target object |must| be the derived
		  method.
		  The source object |must| be at least as public as the target object.
		  Validators |must| apply the scope compatibility test defined in :ref:`section_scope_monotonicity_rule` to this
		  reference. Any violation of the scope compatibility test in this case |must| be reported as an error.
		* [SCP-009] -- Section :wtrl_label:`Derived_from` introduces internal references
		  from the documented class to the referenced base classes. The source object |must|
		  be any of its referenced base classes and the target object |must| be the documented class.
		  The source object |must| be at least as public as the target object.
		  Validators |must| apply the scope compatibility test defined in
		  :ref:`section_scope_monotonicity_rule` to each such reference that resolves to
		  a Waterloo-documented object. Any scope-compatibility violation in this case
		  |must| be reported as an error.
	- |ObsoleteRules|
		* PRE-007 -- Obsolete since 0.5.5; superseded by PRE-021 and PRE-022.
		* PRE-008 -- Obsolete since 0.5.5; superseded by PRE-021 and PRE-022.
		* PRE-009 -- Obsolete since 0.5.5; superseded by PRE-021 and PRE-022.
		* PRE-010 -- Obsolete since 0.5.5; superseded by PRE-021 and PRE-022.
		* PRE-022 -- Obsolete since 0.5.5; Implied by other rules.

For the following section, we define:

:dfn:`Current Object`
	The object in which the docstring resides. This can be a class or a callable, but not a module.

:dfn:`Direct Module`
	The module that contains the :wtrl_dfn:`Current Object`.

:dfn:`Term`
	The first identifier in a :wtrl_label:`Definitions.<DefItem>` header.

:dfn:`Variation`
	Any identifier after the first one in a :wtrl_label:`Definitions.<DefItem>` header.

* :wtrl_label:`Definitions:`
	- [DEF-001] -- The section |may| exist.
	- [DEF-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [DEF-003] -- Each entry in the section |must| have the form of a subsection matching one of the following patterns:
	- :wtrl_label:`<DefItem>:`
		* [DEF-020] -- Any number of subsections |may| exist.
		* [DEF-004] -- :wtrl_label:`<DefItem>` |must| match `<Identifier> ( "," <Identifier> )*` with optional whitespace around commas.
		* [DEF-005] -- In :wtrl_label:`<DefItem>`, the first identifier denotes the :wtrl_term:`Term`; each following identifier denotes a :wtrl_term:`Variation` of that term.
		* [DEF-006] -- The subsection content |must| be free-form text.
		* [DEF-009] -- The subsection content |should| not be empty.
		* [DEF-010] -- :wtrl_label:`<DefItem>` |must_not| be :wtrl_label:`_inherit`.
	- :wtrl_label:`_inherit:`
		* [DEF-011] -- The subsection :wtrl_label:`_inherit` |must_not| appear in profile :wtrl_value:`module`.
		* [DEF-012] -- The subsection :wtrl_label:`_inherit` |may| appear in profiles :wtrl_value:`class`, :wtrl_value:`function`,
		  :wtrl_value:`method`, and :wtrl_value:`inherited_method`.
		* [DEF-014] -- If the subsection :wtrl_label:`_inherit` exists, the :wtrl_term:`Direct Module` |must| have a valid docstring.
		* [DEF-015] -- If the subsection :wtrl_label:`_inherit` exists, the docstring of the :wtrl_term:`Direct Module` |must| contain a :wtrl_label:`Definitions` section.
		* [DEF-016] -- The content of :wtrl_label:`_inherit` |must| be a list of identifiers according to LQID-001.
		* [DEF-017] -- Each entry in :wtrl_label:`_inherit` |must_not| occur as a :wtrl_term:`Term` or :wtrl_term:`Variation` in the :wtrl_label:`Definitions` section of the :wtrl_term:`Current Object`.
		* [DEF-018] -- Each entry in :wtrl_label:`_inherit` |must| occur as a :wtrl_term:`Term` in the :wtrl_term:`Direct Module` docstring's :wtrl_label:`Definitions` section.
		* [DEF-019] -- The use of the subsection :wtrl_label:`_inherit` |must| result in a warning with rule ID :wtrl_value:`VLII-001` at validation time.
		* [DEF-022] -- Implicitly, all :wtrl_term:`Variations` of an inherited :wtrl_term:`Term` are inherited as well.
	- |ObsoleteRules|
		* DEF-013 -- Obsolete since 0.5.2; superseded by PRSR-008.
	- |Rationale|

	  :wtrl_term:`Terms` and :wtrl_term:`Variations` are restricted to Identifiers for the following reasons:

		* They can be referenced in a machine-verifiable way via the semantic role :wtrl_lit:`\|term\|\`...\``.
		* They are robust with respect to formatting changes such as line wrapping.
		* They behave similarly to symbolic constants or macros in a programming language:
		  the identifier provides a stable symbolic anchor, while the definition body
		  provides the human-readable explanation.
	- |LastReview|: 2026-03-25
* :wtrl_label:`Terminology:`
	- [TERM-001] -- The section |may| exist.
	- [TERM-002] -- It |must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [TERM-003] -- It |must_not| contain Normativity Keywords.
	- [TERM-004] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Term>:`
		* [TERM-009] -- Any number of subsections |may| exist
		* [TERM-005] -- :wtrl_label:`<Term>` |must| be a non-empty human-readable string.
		* [TERM-006] -- :wtrl_label:`<Term>` stands for the term to be explained informatively.
		* [TERM-007] -- The subsection content |must| be free-form text.
		* [TERM-008] -- The subsection content |should| not be empty.
	- |Rationale|

	  In contrast to the :wtrl_label:`Definitions` section, the :wtrl_label:`Terminology` section
	  allows arbitrary human-readable labels and is intended solely for explanatory purposes.
	- |LastReview|: 2026-02-23

* :wtrl_label:`Description:`
	- [DESC-001] -- The section |may| exist.
	- [DESC-002] -- The section |may| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [DESC-004] -- The content |may| consist of any number of free-form lines.
	- |ObsoleteRules|:
		* DESC-003 -- Obsolete since 0.5.1; superseded by PRE-013.
		* DESC-005 -- Obsolete since 0.5.5 (pipe operator as separator); more general approach required.
* :wtrl_label:`Notes:`
	- [NOTE-001] -- The section |may| exist.
	- [NOTE-002] -- It |must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [NOTE-003] -- It |must_not| contain Normativity Keywords.
	- [NOTE-004] -- Tools |must| treat the content of section :wtrl_label:`Notes` as informative and must not derive normative requirements from it.
	- [NOTE-005] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Note>:`
		* [NOTE-008] -- Any number of subsections |may| exist
		* [NOTE-006] -- :wtrl_label:`<Note>` |must| be a non-empty human-readable string.
		* [NOTE-007] -- The subsection content |must| be free-form text.
		* [NOTE-009] -- The subsection content |should| not be empty.
	- |LastReview|: 2026-02-23
* :wtrl_label:`See_also:`
	- [SEE-001] -- The section |may| exist.
	- [SEE-011] -- The section |may| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [SEE-002] -- Each entry in the section |must| be an Identifier or a Qualified Identifier.
	- [SEE-003] -- If the section is not listed as normative each entry |should| refer to an existing public object.
	- [SEE-004] -- If the section is listed as normative each entry |must| refer to an existing public object.
	- [SEE-005] -- An entry in :wtrl_label:`See_also` |must_not| refer to the documented object itself.
	- [SEE-006] -- An entry in :wtrl_label:`See_also` |should| refer to an object that has a docstring, if the object is documentable (module, class, or callable).
	- [SEE-007] -- If the section is not listed as normative the object (module, class, function, or method) referred to by entry |should| have a valid Waterloo docstring.
	- [SEE-008] -- If the section is listed as normative the object (module, class, function, or method) referred to by entry |must| have a valid Waterloo docstring.
	- [SEE-009] -- Tools |must| treat unresolved references as errors when :wtrl_label:`See_also` is normative, and |must| treat them as warnings when :wtrl_label:`See_also` is informative.
	- [SEE-010] -- Rules SEE-007 and SEE-008 |must_not| be tested for built-ins. The criteria |must| be :wtrl_func:`inspect.ismodule`, :wtrl_func:`inspect.isclass`, and :wtrl_func:`inspect.isfunction`.
	- |Informative|: Listing :wtrl_label:`See_also` as normative increases strictness and allows tools to rely on resolvable references.
	- |Informative|: Resolution may be limited across module boundaries, since object resolution typically follows the import hierarchy.
	- |LastReview|: 2026-01-31

Sections for module docstrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the sections described in :ref:`common_sections`
a module docstring |must| have the following structure:

* [DOC-003] -- Module docstrings |must_not| contain sections other than { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`, :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract`, :wtrl_label:`Public_classes`, :wtrl_label:`Class_overview`, :wtrl_label:`Public_functions`, :wtrl_label:`Function_overview`, :wtrl_label:`Public_types`, :wtrl_label:`Public_variables`, :wtrl_label:`Public_constants` }.
* :wtrl_label:`Preamble:`
	- :wtrl_label:`profile:`
		* [PRE-017] -- The profile |must| be :wtrl_value:`module`.
* :wtrl_label:`Contract:`
	- [CON-001] -- The section |must| exist.
	- [CON-002] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CON-028] -- |Must_not| have subsections other than { :wtrl_label:`general` }.
	- :wtrl_label:`general:`
		* [CON-022] -- The subsection |must| exist.
		* [CON-003] -- |Must| contain an explanation of the purpose of the module sufficient to decide
		  whether the module is applicable to a given use case.
	- |ObsoleteRules|:
		* CON-029
		* CON-030
		* CON-031
* :wtrl_label:`Public_classes:`
	- [MPCL-001] -- The section |may| exist.
	- [MPCL-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [MPCL-003] -- The content |must| be a list of Qualified Identifiers according to LQID-001.
	- [MPCL-004] -- Each entry listed |must| be resolvable relative to the documented module.
	- [MPCL-005] -- Each entry listed |must| refer to a class.
	- [MPCL-006] -- Each class with a valid docstring |should| be listed in :wtrl_label:`Public_classes`.
	- [MPCL-007] -- Each class listed in :wtrl_label:`Public_classes` |should| have a valid docstring.
	- [MPCL-008] -- A class not listed in :wtrl_label:`Public_classes` |may| have an invalid or missing docstring.
* :wtrl_label:`Class_overview:`
	- [MCLO-001] -- The section |may| exist.
	- [MCLO-002] -- |Must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [MCLO-003] -- |Must_not| exist if there is no section :wtrl_label:`Public_classes:`
	- [MCLO-004] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Class>:`
		* [MCLO-005] -- :wtrl_label:`<Class>` |must| match the pattern of an Identifier.
		* [MCLO-006] -- The subsection content |must| be free-form text.
		* [MCLO-007] -- The subsection content is informative and |must_not| contain any Normativity Keyword.
		* [MCLO-008] -- :wtrl_label:`<Class>` |must| be resolvable relative to the documented module.
		* [MCLO-009] -- :wtrl_label:`<Class>` |must| refer to a class object.
		* [MCLO-011] -- :wtrl_label:`<Class>` |must| appear in section :wtrl_label:`Public_classes`.
	- [MCLO-010] -- Any number of subsections |may| exist.
	- |LastReview|: 2026-02-25
* :wtrl_label:`Public_functions:`
	- [MPFN-001] -- The section |may| exist.
	- [MPFN-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [MPFN-003] -- The content |must| be a list of Qualified Identifiers according to LQID-001.
	- [MPFN-004] -- Each entry listed |must| be resolvable relative to the documented module.
	- [MPFN-005] -- Each entry listed |must| refer to a function.
	- [MPFN-006] -- Each function with a valid docstring |should| be listed in :wtrl_label:`Public_functions`.
	- [MPFN-007] -- Each function listed in :wtrl_label:`Public_functions` |should| have a valid docstring.
	- [MPFN-008] -- A function not listed in :wtrl_label:`Public_functions` |may| have an invalid or missing docstring.
* :wtrl_label:`Function_overview:`
	- [MFNO-001] -- The section |may| exist.
	- [MFNO-002] -- |Must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [MFNO-003] -- |Must_not| exist if there is no section :wtrl_label:`Public_functions:`
	- [MFNO-004] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Function>:`
		* [MFNO-005] -- :wtrl_label:`<Function>` |must| match the pattern of an Identifier.
		* [MFNO-006] -- The subsection content |must| be free-form text.
		* [MFNO-007] -- The content is informative and |must_not| contain any Normativity Keyword.
		* [MFNO-008] -- :wtrl_label:`<Function>` |must| be resolvable relative to the documented module.
		* [MFNO-009] -- :wtrl_label:`<Function>` |must| refer to a function object.
		* [MFNO-011] -- :wtrl_label:`<Function>` |must| appear in section :wtrl_label:`Public_functions`.
	- [MFNO-010] -- Any number of subsections |may| exist.
	- |LastReview|: 2026-02-25
* :wtrl_label:`Public_types:`
	- [MPTYP-001] -- The section |may| exist.
	- [MPTYP-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [MPTYP-003] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Type>:`
		* [MPTYP-004] -- :wtrl_label:`<Type>` |must| match the pattern of an Identifier.
		* [MPTYP-006] -- The subsection content |must| be free-form text.
		* [MPTYP-005] -- :wtrl_label:`<Type>` |must| be resolvable relative to the documented module.
		* [MPTYP-008] -- :wtrl_label:`<Type>` |must| refer to a TypeAlias or NewType.
	- |ObsoleteRules|
		* MPTYP-007 -- Obsolete in version 0.5.3; duplicate of MPTYP-005.
	- |LastReview|: 2026-06-29
* :wtrl_label:`Public_variables:`
	- [MPVAR-001] -- The section |may| exist.
	- [MPVAR-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [MPVAR-003] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Assignable>:`
		* [MPVAR-004] -- :wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [MPVAR-006] -- The subsection content |must| be free-form text.
		* [MPVAR-005] -- :wtrl_label:`<Assignable>` |must| be resolvable relative to the documented module, either as a runtime attribute or as an annotated variable.
		* [MPVAR-008] -- :wtrl_label:`<Assignable>` |must| refer to a Named Value.
		* [MPVAR-009] -- If the object referenced by :wtrl_label:`<Assignable>` is annotated, the annotation |must_not| be wtrl_type:`Final`.
	- |ObsoleteRules|
		* MPVAR-007 -- Obsolete in version 0.5.3; duplicate of MPVAR-005.
	- |LastReview|: 2026-06-29
* :wtrl_label:`Public_constants:`
	- [MPCON-001] -- The section |may| exist.
	- [MPCON-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [MPCON-003] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Assignable>:`
		* [MPCON-004] -- :wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [MPCON-007] -- The subsection content |must| be free-form text.
		* [MPCON-005] -- :wtrl_label:`<Assignable>` |must| be resolvable relative to the documented module.
		* [MPCON-009] -- :wtrl_label:`<Assignable>` |must| refer to a Named Value.
		* [MPCON-006] -- If the object referenced by :wtrl_label:`<Assignable>` is annotated, the annotation  |must| be :wtrl_type:`Final`.
	- |ObsoleteRules|
		* MPCON-008 -- Obsolete in version 0.5.3; duplicate of MPCON-005.
	- |LastReview|: 2026-06-29

Sections for class docstrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the sections described in :ref:`common_sections`
a class docstring |must| have the following structure:

* [DOC-004] -- Class docstrings |must_not| contain sections other than { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`, :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract`, :wtrl_label:`Derived_from`, :wtrl_label:`Public_classes`, :wtrl_label:`Class_overview`, :wtrl_label:`Public_methods`, :wtrl_label:`Method_overview`, :wtrl_label:`Public_types`, :wtrl_label:`Public_variables`, :wtrl_label:`Public_constants`, :wtrl_label:`Factory` }.
* :wtrl_label:`Preamble:`
	- :wtrl_label:`profile:`
		* [PRE-018] -- The profile |must| be :wtrl_value:`class`.
* :wtrl_label:`Contract:`
	- [CON-032] -- |Must_not| have subsections other than { :wtrl_label:`general`, :wtrl_label:`constructor`, :wtrl_label:`api`, :wtrl_label:`traits` }.
	- :wtrl_label:`general:`
		* [CON-023] -- The subsection |must| exist.
		* [CON-006] -- |Must| contain an explanation of the purpose of the class sufficient to decide
		  whether the class is applicable to a given use case.
	- :wtrl_label:`constructor:`
		* [CON-007] -- The subsection |must| exist.
		* [CON-008] -- |Should| contain a brief explanation of the constructor or point to special method :wtrl_func:`__init__` with a valid docstring.
	- :wtrl_label:`traits:`
		* [CON-012] -- The subsection |may| exist.
		* [CON-053] -- If it exists, the content |must| be a list of Identifiers according to rule LQID-001. In this context, "Identifier" (not "Qualified Identifier") applies.
		* [CON-017] -- Each trait identifier |must| be one of the following
			+ :wtrl_value:`final` -- A class marked :wtrl_value:`final` |must_not| be derived from.
			+ :wtrl_value:`abstract` -- A class marked :wtrl_value:`abstract` |must_not| be instantiated directly.
	- |ObsoleteRules|
		* CON-004 -- Obsolete in version 0.5.5; Superseded by CON-001
		* CON-005 -- Obsolete in version 0.5.5; Superseded by CON-002
		* CON-009 -- Obsolete in version 0.5.5; Obsolete subsection :wtrl_label:`api`.
		* CON-010 -- Obsolete in version 0.5.5; Obsolete subsection :wtrl_label:`api`.
		* CON-011 -- Obsolete in version 0.5.5; Obsolete subsection :wtrl_label:`api`.
		* CON-018 -- Obsolete in version 0.5.5; Now covered by CON-017
		* CON-013 -- Obsolete in version 0.5.5; Superseded by CON-053
		* CON-014 -- Obsolete in version 0.5.5; Superseded by CON-053
		* CON-015 -- Obsolete in version 0.5.5; Superseded by CON-053
		* CON-016 -- Obsolete in version 0.5.5; Superseded by CON-053
* :wtrl_label:`Derived_from:`
	- [DER-001] -- The section |may| exist.
	- [DER-004] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [DER-009] -- If it exists, the content |must| be a list of [Qualified] Identifiers according to rule LQID-001.
	- [DER-002] -- |Must| list the base classes that contribute public functions, types, constants, attributes, or semantic guarantees.
	- [DER-003] -- Each entry |must| refer to a direct base class of the documented class.
	- [DER-010] -- Each entry |must| name one of the direct base classes either as a direct Identifier or as a Qualified Identifier.
	- [DER-011] -- A direct Identifier entry |must| resolve unambiguously to exactly one direct base class.
	- [DER-012] -- A Qualified Identifier entry |must| resolve to a direct base class by fully qualifying the name of that base class.
	- [DER-013] -- If a direct Identifier would match more than one direct base class, the entry |must| be qualified enough to resolve the ambiguity.
	- |ObsoleteRules|
		* DER-005 -- Obsolete in version 0.5.5; superseded by DER-009.
		* DER-006 -- Obsolete in version 0.5.5; superseded by DER-009.
		* DER-007 -- Obsolete in version 0.5.5; superseded by DER-009.
		* DER-008 -- Obsolete in version 0.5.5; superseded by DER-009.
* :wtrl_label:`Public_classes:`
	- [CPCL-001] -- The section |may| exist.
	- [CPCL-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CPCL-003] -- The content |must| be a list of Qualified Identifiers according to LQID-001.
	- [CPCL-004] -- Each entry listed |must| be resolvable relative to the documented class.
	- [CPCL-005] -- Each entry listed |must| refer to a class.
	- [CPCL-006] -- Each class with a valid docstring |should| be listed in :wtrl_label:`Public_classes`.
	- [CPCL-007] -- Each class listed in :wtrl_label:`Public_classes` |should| have a valid docstring.
	- [CPCL-008] -- A class not listed in :wtrl_label:`Public_classes` |may| have an invalid or missing docstring.
* :wtrl_label:`Class_overview:` (nested/inner classes)
	- [CCLO-001] -- The section |may| exist.
	- [CCLO-002] -- |Must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CCLO-003] -- |Must_not| exist if there is no section :wtrl_label:`Public_classes:`
	- [CCLO-004] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Class>:`
		* [CCLO-005] -- :wtrl_label:`<Class>` |must| match the pattern of an Identifier.
		* [CCLO-006] -- The subsection content |must| be free-form text.
		* [CCLO-007] -- The subsection content is informative and |must_not| contain any Normativity Keyword.
		* [CCLO-008] -- :wtrl_label:`<Class>` |must| be resolvable relative to the documented class.
		* [CCLO-009] -- :wtrl_label:`<Class>` |must| refer to a class object.
		* [CCLO-011] -- :wtrl_label:`<Class>` |must| appear in section :wtrl_label:`Public_classes`.
	- [CCLO-010] -- Any number of subsections |may| exist.
	- |LastReview|: 2026-02-25
* :wtrl_label:`Public_methods:`
	- [CPMT-001] -- The section |may| exist.
	- [CPMT-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CPMT-003] -- The content |must| be a list of Qualified Identifiers according to LQID-001.
	- [CPMT-004] -- Each entry listed |must| be resolvable relative to the documented class.
	- [CPMT-005] -- Each entry listed |must| refer to a method.
	- [CPMT-006] -- Each method with a valid docstring |should| be listed in section :wtrl_label:`Public_methods`.
	- [CPMT-007] -- Each method listed in section :wtrl_label:`Public_methods` |should| have a valid docstring.
	- [CPMT-008] -- A method not listed in :wtrl_label:`Public_methods` |may| have an invalid or missing docstring.
* :wtrl_label:`Method_overview:`
	- [CMTO-001] -- The section |may| exist.
	- [CMTO-002] -- |Must_not| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CMTO-003] -- |Must_not| exist if there is no section :wtrl_label:`Public_methods:`
	- [CMTO-004] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Method>:`
		* [CMTO-005] -- :wtrl_label:`<Method>` |must| match the pattern of an Identifier.
		* [CMTO-006] -- The subsection content |must| be free-form text.
		* [CMTO-007] -- The subsection content is informative and |must_not| contain any Normativity Keyword.
		* [CMTO-008] -- :wtrl_label:`<Method>` |must| be resolvable relative to the documented class.
		* [CMTO-009] -- :wtrl_label:`<Method>` |must| refer to a method.
		* [CMTO-011] -- :wtrl_label:`<Method>` |must| appear in section :wtrl_label:`Public_methods`.
	- [CMTO-010] -- Any number of subsections |may| exist.
	- |LastReview|: 2026-02-25
* :wtrl_label:`Public_types:`
	- [CPTYP-001] -- The section |may| exist.
	- [CPTYP-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CPTYP-003] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Type>:`
		* [CPTYP-004] -- :wtrl_label:`<Type>` |must| match the pattern of an Identifier.
		* [CPTYP-006] -- The subsection content |must| be free-form text.
		* [CPTYP-005] -- :wtrl_label:`<Type>` |must| be resolvable relative to the documented class.
		* [CPTYP-008] -- :wtrl_label:`<Type>` |must| refer to a TypeAlias or NewType.
	- |ObsoleteRules|
		* CPTYP-007 -- Obsolete in version 0.5.3; duplicate of CPTYP-005.
	- |LastReview|: 2026-06-29
* :wtrl_label:`Public_variables:`
	- [CPVAR-001] -- The section |may| exist.
	- [CPVAR-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CPVAR-003] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Assignable>:`
		* [CPVAR-004] -- :wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [CPVAR-006] -- The subsection content |must| be free-form text.
		* [CPVAR-005] -- :wtrl_label:`<Assignable>` |must| be resolvable relative to the documented class, either as a runtime attribute or as an annotated field.
		* [CPVAR-008] -- :wtrl_label:`<Assignable>` |must| refer to a Named Value.
		* [CPVAR-009] -- If the object referenced by :wtrl_label:`<Assignable>` is annotated, the annotation |must_not| be wtrl_type:`Final`.
	- |ObsoleteRules|
		* CPVAR-007 -- Obsolete in version 0.5.3; duplicate of CPVAR-005.
	- |LastReview|: 2026-06-29
* :wtrl_label:`Public_constants:`
	- [CPCON-001] -- The section |may| exist.
	- [CPCON-002] -- If it exists, it |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [CPCON-003] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Assignable>:`
		* [CPCON-004] -- :wtrl_label:`<Assignable>` |must| match the pattern of an Identifier.
		* [CPCON-007] -- The subsection content |must| be free-form text.
		* [CPCON-005] -- :wtrl_label:`<Assignable>` |must| be resolvable relative to the documented class.
		* [CPCON-009] -- :wtrl_label:`<Assignable>` |must| refer to a Named Value.
		* [CPCON-006] -- If the object referenced by :wtrl_label:`<Assignable>` is annotated, the annotation  |must| be :wtrl_type:`Final`.
	- |ObsoleteRules|
		* CPCON-008 -- Obsolete in version 0.5.3; duplicate of CPCON-005.
	- |LastReview|: 2026-02-24
* :wtrl_label:`Factory:`
	- [FAC-001] -- The section |may| exist.
	- [FAC-009] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [FAC-004] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Function>:`
		* [FAC-005] -- :wtrl_label:`<Function>` |must| match the pattern of a Qualified Identifier.
		* [FAC-008] -- Each :wtrl_label:`<Function>` |must| occur at most once within its enclosing :wtrl_label:`Factory` section.
		* [FAC-006] -- :wtrl_label:`<Function>` |must| resolve to an existing function.
		* [FAC-007] -- The content of :wtrl_label:`<Function>` |must| be interpreted as free-form text.
	- |ObsoleteRules|:
		* FAC-002 -- Obsolete since version 0.5.1; superseded by PRE-013.
		* FAC-003 -- Obsolete since version 0.5.0.
	- |LastReview|: 2026-02-23


.. _function_sections:

Sections for function/method docstrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the sections described in :ref:`common_sections`
a function or method docstring |must| have the following structure:

.. _section_function_pramble:

* :wtrl_label:`Preamble:`
	- :wtrl_label:`profile:`
		* [PRE-019] -- The profile |must| be :wtrl_value:`function` or :wtrl_value:`method`.
	- :wtrl_label:`status:`
		* [STA-001] -- The subsection |may| exist.
		* [STA-002] -- The subsection |must| contain exactly one entry.
		* [STA-003] -- The entry |must| be an Identifier.
		* [STA-004] -- The following trait identifiers are defined by this specification:
			- :wtrl_value:`experimental` -- The object is under active development and its behavior or signature may change without notice.
			- :wtrl_value:`stable` -- The object is intended for normal use and its behavior and signature are expected to remain compatible across releases.
			- :wtrl_value:`frozen` -- The object is considered feature-complete and should not receive behavioral changes except for critical bug fixes.
			- :wtrl_value:`deprecated` -- The object should no longer be used for new code and may be removed in a future version.
			- :wtrl_value:`draft` -- The object is incomplete and primarily intended for internal use or discussion; its contract is not yet finalized.
		* [STA-005] -- If subsection :wtrl_label:`Status` is absent, tools |should| treat the status as :wtrl_value:`stable`.

* [DOC-005] -- Function or method docstrings |must_not| contain sections other than { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`, :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract`, :wtrl_label:`Parameters`, :wtrl_label:`Returns`, :wtrl_label:`Raises` }.
* :wtrl_label:`Contract:`
	- [CON-027] -- |Must_not| have subsections other than { :wtrl_label:`general`, :wtrl_label:`invariants`, :wtrl_label:`requires`, :wtrl_label:`ensures` }.
	- For subsections { :wtrl_label:`general`, :wtrl_label:`invariants`, :wtrl_label:`requires`, :wtrl_label:`ensures` } the following rules apply:
		* [CON-051] -- Tools |must| treat the free-form content as an ordered sequence of logical lines.
		* [CON-052] -- Tools |must| store exactly one string item per logical line and |must| preserve the original order.
	- :wtrl_label:`general:`
		* [CON-024] -- The subsection |must| exist.
		* [CON-021] -- |Must| contain an explanation of the purpose of the function sufficient to decide
		  whether the function is applicable to a given use case.
	- :wtrl_label:`invariants:`
		* [CON-025] -- The subsection |may| exist.
		* [CON-026] -- The subsection content |must| be free-form text.
	- :wtrl_label:`requires:`
		* [CON-047] -- The subsection |may| exist.
		* [CON-048] -- The subsection content |must| be free-form text.
	- :wtrl_label:`ensures:`
		* [CON-049] -- The subsection |may| exist.
		* [CON-050] -- The subsection content |must| be free-form text.
	- |ObsoleteRules|
		* CON-019 -- Obsolete in version 0.5.5; Superseded by CON-001
		* CON-020 -- Obsolete in version 0.5.5; Superseded by CON-002
	- |LastReview|: 2026-03-03
* :wtrl_label:`Parameters:`
	- [PAR-001] -- The section |must| exist.
	- [PAR-002] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [PAR-003] -- The section |must| list all parameters and provide an explanation for each parameter.
	- [PAR-008] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Par>:`
		* [PAR-006] -- :wtrl_label:`<Par>` |must| be an Identifier.
		* [PAR-007] -- The subsection content |must| be free-form text.
		* [PAR-004] -- Each parameter in the function's signature |must| be documented by a corresponding :wtrl_label:`<Par>` entry.
		* [PAR-005] -- Each :wtrl_label:`<Par>` entry |must| correspond to a parameter in the function's signature.
	- |LastReview|: 2026-02-25
* :wtrl_label:`Returns:`
	- [RET-001] -- The section |must| exist.
	- [RET-002] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [RET-005] -- The section |must_not| contain subsections.
	- [RET-003] -- The section |must| explain the return value of the documented function or method.
	- [RET-004] -- If the documented function or method is annotated with return type :wtrl_type:`bool`,
	  section :wtrl_label:`Returns` |should| mention at least one of the tokens
	  :wtrl_value:`|True|` or :wtrl_value:`|False|`.
	- [RET-006] -- If the documented function or method is annotated to return :wtrl_value:`None`,
	  section :wtrl_label:`Returns` |should| mention the token :wtrl_value:`|None|`.
	- [RET-007] -- If the documented function or method is annotated to return :wtrl_type:`Self`,
	  section :wtrl_label:`Returns` |should| mention the token :wtrl_value:`|Self|`.
	- [RET-008] -- Validators |should| apply rule RET-006 only if the function or method
	  is annotated to return :wtrl_value:`None` and the section contains ``None`` in non-tokenised form.
	- [RET-009] -- Validators |should| apply rule RET-007 only if the function or method
	  is annotated to return :wtrl_type:`Self` and the section contains ``self`` or ``Self`` in non-tokenised form.
	- [RET-010] -- Violations of rules RET-004, RET-006, and RET-007
	  |must| be reported as warnings and |must_not| be reported as errors.
	- |LastReview|: 2026-02-25
* :wtrl_label:`Raises:`
	- [RAI-001] -- The section |must| exist.
	- [RAI-002] -- The section |must| be listed as normative in :wtrl_label:`Preamble.normative_sections`.
	- [RAI-003] -- The section |must| list all exception classes that may be raised under correct and contract-compliant usage.
	- [RAI-011] -- Each entry in the section |must| have the form of a subsection matching the following pattern:
	- :wtrl_label:`<Exception>:`
		* [RAI-008] -- :wtrl_label:`<Exception>` |must| be a Qualified Identifier.
		* [RAI-004] -- :wtrl_label:`<Exception>` |must| resolve to an existing (exception) class.
		* [RAI-005] -- The subsection content |must| be free-form text.
		* [RAI-006] -- The content |must| explain the circumstances which must or may lead to raising the exception addressed by :wtrl_label:`<Exception>`.
		* [RAI-007] -- Each entry listed |must| represent a subclass of :wtrl_type:`BaseException`.
	- |ObsoleteRules|
		* RAI-009 -- Obsolete since 0.5.2; superseded by RAI-004.
		* RAI-010 -- Obsolete since 0.5.3;

Sections for inherited method docstrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the sections described in :ref:`common_sections`
an inherited method docstring |must| have the following structure:

* [DOC-006] -- Inherited method docstrings |must_not| contain sections other than
  { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Description`,
  :wtrl_label:`Notes`, :wtrl_label:`See_also`, :wtrl_label:`Contract` }.

* :wtrl_label:`Preamble:`
	- :wtrl_label:`profile:`
		* [PRE-020] -- The profile |must| be :wtrl_value:`inherited_method`.
* :wtrl_label:`Contract:`
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
	- |ObsoleteRules|:
		* CON-033 -- Obsolete in version 0.5.5; Superseded by CON-001
		* CON-034 -- Obsolete in version 0.5.5; Superseded by CON-002
	- |LastReview|: 2026-02-23

Rules for exceptions not supposed to occur
------------------------------------------

This section is normative.

The rule declarations in this section describe error conditions that correspond
to logically unreachable branches in the implementation. Under correct
implementation of both the specification and the analyzed code, these cases
should never occur.

However, since the documentation is regularly validated against the codebase,
formal rule identifiers must exist so that such situations can be reported
consistently if they are encountered.

If any of the rules listed below is triggered during validation, this indicates
an internal inconsistency or an implementation defect.

* [DOC-999] -- |Should_not| occur.
* [MCLO-999] -- |Should_not| occur.
* [MPTYP-999] -- |Should_not| occur.
* [MPVAR-999] -- |Should_not| occur.

Coverage rules and intended workflow
------------------------------------

This section is informative.

The Waterloo specification contains a set of rules that connect docstring validity and public API listings
in sections such as :wtrl_label:`Public_classes`, :wtrl_label:`Public_functions`, and :wtrl_label:`Public_methods`.
Taken together, these rules define an intended workflow and an interpretation of documentation "coverage".

In short, Waterloo treats the :wtrl_label:`Public_*` sections as an explicit declaration of public API surface
(for a given scope). Listing an object in a :wtrl_label:`Public_*` section is a commitment:
the specification requires the object to exist, and requires the object to have a valid docstring.

Conversely, the existence of a valid docstring does not automatically make an object part of the public API.
The specification recommends listing documented objects in :wtrl_label:`Public_*` sections, but does not require it.
This supports incremental documentation work, experimentation, and internal documentation without forcing immediate API exposure.

Module-level coverage
^^^^^^^^^^^^^^^^^^^^^

At module level, the specification expresses the following principles:

	* The specification recommends that each class with a valid docstring is listed in :wtrl_label:`Public_classes`
	  (MPCL-006).

	* The specification recommends that each class listed in :wtrl_label:`Public_classes` has a valid docstring
	  (MPCL-007).

	* The specification recommends that each function with a valid docstring is listed in :wtrl_label:`Public_functions`
	  (MPFN-006).

	* The specification recommends that each function listed in :wtrl_label:`Public_functions` has a valid docstring
	  (MPFN-007).

	* The specification requires that each type listed in :wtrl_label:`Public_types` exists in the module
	  (MPTYP-005).

	* The specification requires that each variable listed in :wtrl_label:`Public_variables` exists in the module, either as a runtime attribute or as an annotated variable
	  (MPVAR-005).

	* The specification requires that each constant listed in :wtrl_label:`Public_constants` exists in the module
	  (MPCON-005).

Class-level coverage
^^^^^^^^^^^^^^^^^^^^

At class level, the specification expresses the following principles:

	* The specification requires that each class listed in :wtrl_label:`Public_classes` exists as an attribute on the documented class
	  (CPCL-004).

	* The specification recommends that each embedded class with a valid docstring is listed in section :wtrl_label:`Public_classes`
	  (CPCL-006).

	* The specification recommends that each method with a valid docstring is listed in section :wtrl_label:`Public_methods`
	  (CPMT-006).

	* The specification requires that each method listed in section :wtrl_label:`Public_methods` exists and is a method/function
	  (CPMT-005).

	* The specification requires that each variable listed in :wtrl_label:`Public_variables` exists on the documented class, either as a runtime attribute or as an annotated field
	  (CPVAR-005).

	* The specification requires that each constant listed in :wtrl_label:`Public_constants` exists on the documented class
	  (CPCON-005).

Practical consequence
^^^^^^^^^^^^^^^^^^^^^

These rules allow authors to write many valid docstrings without immediately declaring the documented objects as public.
Only objects explicitly listed in :wtrl_label:`Public_*` sections are treated as part of the public API surface
(for the given scope) and are therefore subject to strict coverage expectations.



.. _chapter_scopes_and_visibility:

Scopes and visibility
---------------------

This section is normative.

This section defines the semantics of the :wtrl_label:`scope` attribute and the
rules governing visibility, rendering, and validation across different scopes.

The purpose of scopes is to allow a single codebase and documentation set to be
rendered consistently for different audiences, such as public users, extension
developers, or core developers.

More formally, the purpose is to ensure that any rendered
documentation artifact forms a reference-closed subgraph of the
complete documentation graph.

Conceptual model
^^^^^^^^^^^^^^^^^^^^^

Each documented object (module, class, function, or method) is assigned one or
more scope values via the :wtrl_label:`Preamble.scope` subsection.

Scopes do not represent access control. Instead, they describe the intended
audience and contractual visibility of an object.
Scopes are interpreted uniformly by validators, renderers, and coverage tools.

.. _section_scope_values:

Scope values
^^^^^^^^^^^^

This section is normative.

Any tool |must| recognize and dispatch the following scope identifiers:

* :wtrl_value:`public`
* :wtrl_value:`extension`
* :wtrl_value:`core`

with the following semantics:

* :wtrl_value:`public` -- stable API intended for general external users.
* :wtrl_value:`extension` -- API intended for extension, plugin, or application developers.
* :wtrl_value:`core` -- internal API intended for core developers of the project.

The specification defines a partial order over scope values such that:

* :wtrl_func:`s` ( :wtrl_value:`public` ) <= :wtrl_func:`s` ( :wtrl_value:`extension` )
* :wtrl_func:`s` ( :wtrl_value:`extension` ) <= :wtrl_func:`s` ( :wtrl_value:`core` )

This order expresses increasing internality and decreasing audience size.

Scope sets
^^^^^^^^^^

This section is informative. Rules SCP-002 and SCP-010 describe the properties listed here in a normative way.

The :wtrl_label:`scope` subsection may list zero or more scope identifiers.
The scope of an object is therefore a set of scope values.
If the :wtrl_label:`scope` subsection is absent or empty, the default scope set is
{ :wtrl_value:`public` }.

Visibility
^^^^^^^^^^^^^^^^^^^^^

An object is considered visible for a given rendering or validation context if
at least one of its scope values is visible in that context.

Let S be a set of scope values selected by a tool (for example, for rendering or
coverage analysis). An object is :wtrl_dfn:`visible` under a scope set S if and only if there exists
a scope value s_obj assigned to the object and a scope value s_query in S
such that:

	s_obj <= s_query

In other words, an object is visible if at least one of its declared scopes is
less than or equal to at least one selected scope.

.. _section_scope_monotonicity_rule:

Scope Monotonicity Rule
^^^^^^^^^^^^^^^^^^^^^^^

Documented objects form a directed reference graph.

Reference edges arise exclusively from the constructs listed below.
For each reference edge, the source and target objects are defined
according to the semantics of the corresponding construct.
The following sections constitute the only means by which reference edges
are introduced into the documentation graph.

**Public classes, functions, and methods**

* Entries in :wtrl_label:`Public_classes` induce reference edges from the containing module/class to the listed classes.
* Entries in :wtrl_label:`Public_functions` induce reference edges from the containing module to the listed functions.
* Entries in :wtrl_label:`Public_methods` induce reference edges from the containing class to the listed methods.

.. rubric:: Rationale (informative)
	
This reflects the intuitive notion that the containing object "contains"
the listed objects as part of its public API surface. The reference edge represents a contractual
relationship: the containing object is **responsible** for providing access to the contained objects,
and users of the containing object are expected to interact with the contained objects as part
of their usage of the containing object. The containing object must be at least as public as
the contained objects, since otherwise it would block access to visible such objects.

**Inheritance**

* Subsection :wtrl_label:`Contract.base` in profile :wtrl_value:`inherited_method` induces a reference edge from the referenced(!) base method to the referencing(!) method.
* Entries in :wtrl_label:`Derived_from` induce reference edges from the base(!) class to the derived(!) class.

.. rubric:: Rationale (informative)

This reflects the intuitive notion that a derived class or method "refers to"
its base class or method as part of its contract. The reference edge represents a contractual relationship:
the derived object is **obliged** to uphold the contract of the base object, and users of the derived object
are expected to rely on the guarantees provided by the base object as part of their usage of the derived object.

**Cross-referencing**

* Entries in :wtrl_label:`See_also` induce reference edges from the referenced(!) objects to the referencing(!) object.

.. rubric:: Rationale (informative)

A section :wtrl_label:`See_also` represents an explicit warrant that the referenced objects
are accessible and relevant to users of the referencing object. Information flows from the referenced objects
to the referencing object, and users of the referencing object are expected to consult the referenced objects,
therefore the referenced objects must be at least as public as the referencing object.

If we define A as the source of information and B as the target of information,
in terms of the numeric scope order, this means:

* For containment-style references, there exist s_A in scopes(A) and s_B in scopes(B) such that s_A <= s_B,
  ("A is at least as public as B")
  where A represents the **containing** object and B represents the **contained** object.

* For :wtrl_label:`Derived_from` and :wtrl_label:`Contract.base`,
  there exist s_A in scopes(A) and s_B in scopes(B) such that s_A <= s_B,
  ("A is at least as public as B")
  where A represents the **referenced** object
  and B represents the **referencing** object containing the :wtrl_label:`Derived_from` or :wtrl_label:`Contract.base` section.

* For :wtrl_label:`See_also`, there exist s_A in scopes(A) and s_B in scopes(B) such that s_A <= s_B,
  ("A is at least as public as B")
  where A represents the **referenced** object
  and B represents the **referencing** object containing the :wtrl_label:`See_also` section.

This rule set is referred to as the :wtrl_term:`Scope Monotonicity Rule`.

Non-referential relationships
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Certain structural relationships do not introduce reference edges
for the purposes of scope validation.
In particular, entries in the :wtrl_label:`Factory` section do not
constitute reference edges.

The :wtrl_label:`Factory` section describes callable entry points
for object construction. The direction of instantiation does not
imply contractual visibility in either direction.

For example:

* A factory function may have scope :wtrl_value:`core` while the
  constructed class has scope :wtrl_value:`public`.
* Conversely, a class may have scope :wtrl_value:`core` while a
  factory function providing controlled access to instances is
  visible under :wtrl_value:`public`.

Both situations are valid and do not violate scope monotonicity.
Therefore, factory declarations do not participate in the reference graph.

Rendering and validation
^^^^^^^^^^^^^^^^^^^^^^^^^

When rendering documentation for a selected scope set S, tools |must|:

* render only objects that are visible under S, and
* emit only references to visible objects.

Validators |must| enforce the scope monotonicity rule and report violations as
errors.

This guarantees that documentation rendered for any scope set is internally
consistent and closed under references.


Rationale: SSoT for Normative Statements
----------------------------------------

This section is informative.

This rationale provides the motivation for rules MCLO-007, MFNO-007,
CCLO-007, and CMTO-007. Waterloo follows the principle of **Single Source of Truth (SSoT)** for
normative requirements. Every normative statement is defined exactly once
and at exactly one semantic location.

In particular, normative requirements describing the behavior, guarantees,
or obligations of an object are defined exclusively in the docstring of that
object itself, in accordance with the principles of Locality of Information
(LoII) and Single Source of Truth (SSoT).

Sections such as :wtrl_label:`Public_classes`, :wtrl_label:`Public_functions`,
and :wtrl_label:`Public_methods` declare which objects belong to the documented
public API surface. Sections such as :wtrl_label:`Class_overview`,
:wtrl_label:`Function_overview`, and :wtrl_label:`Method_overview` may provide
informative summaries for those objects. Neither kind of section is intended to
redefine or qualify the behavior of the objects they mention.

Allowing normativity keywords in API listing sections or overview sections would introduce
multiple independent locations for normative statements about the same
object. This would make it impossible to ensure consistency and would
undermine automated validation, tooling, and long-term maintainability.

Therefore, once an object is equipped with its own valid docstring, all
normative statements concerning that object are required to appear there
and nowhere else. API listing sections may declare membership in the public API
surface, and overview sections may provide descriptive or summarizing text, but
neither may introduce additional normative requirements.

This design ensures that tools, validators, and human readers can rely on
a single authoritative specification for each documented object, and that
normative changes are localized, explicit, and unambiguous.

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

Distinction :wtrl_label:`ensures` vs :wtrl_label:`invariants`
-------------------------------------------------------------

This section is informative.

The subsections :wtrl_label:`ensures` and :wtrl_label:`invariants` overlap thematically, but serve different purposes.
:wtrl_label:`ensures` describes postconditions that hold after a successful call of the documented function.
:wtrl_label:`invariants` describes properties that remain true across repeated calls and are typically suited
for automated testing, such as idempotence, non-mutation of inputs, or round-trip properties.
