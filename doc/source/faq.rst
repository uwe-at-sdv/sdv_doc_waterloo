Requests for Rationales
=======================

.. _rfr_0001:

.. rubric:: [RFR-0001] -- On section :wtrl_label:`Raises`

Why do we demand sections like :wtrl_label:`Raises` in functions but not
for instance :wtrl_label:`Public_functions` in modules? Both are normative.
In both cases, an empty list (= empty set) is a normative statement.

:wtrl_label:`Status`:
	active

:wtrl_label:`Created`:
	2026-07-24

:wtrl_label:`Related rules`:
	RAI-001,
	MPCL-001, MPFN-001, CPTYP-001, CPVAR-001, CPCON-001,
	CPCL-001, CPMT-001, CPTYP-001, CPVAR-001, CPCON-001

:wtrl_label:`Rationale`:
	While modules without :wtrl_label:`Public_classes` or
	:wtrl_label:`Public_functions` are perfectly common, callable objects almost
	always require explicit consideration of exceptional control flow.

	Waterloo intentionally places a stronger documentation burden on functions and
	methods than on modules. In practice, omitted exception documentation is far
	more likely to hide implementation risks than omitted lists of public module
	members.

	Requiring the :wtrl_label:`Raises` section encourages authors to make an
	explicit decision. An empty section documents that no exceptions are expected;
	a populated section documents which exceptional conditions form part of the
	object's contract.

	A recurring follow-up asks why emptiness itself carries this statement,
	rather than an explicit marker such as :wtrl_lit:`<none>` or
	:wtrl_lit:`<empty>`. The empty section is already an unambiguous value of a
	normative structure, so a marker would only add a redundant synonym in the
	textual layer -- one that invites typos and near-synonyms
	(:wtrl_lit:`<none>` vs. :wtrl_lit:`<empty>` vs. :wtrl_lit:`none`) which a
	structural representation cannot suffer. Waterloo therefore assigns the
	meaning to the empty section directly and defines no such token.

:wtrl_label:`Consequences`:
	Omitting the Raises section would make it impossible to distinguish between
	*"No exceptions were considered"*
	and 
	*"The author explicitly states that no exceptions belong to the public contract"*.

.. _rfr_0002:

.. rubric:: [RFR-0002] -- On sections :wtrl_label:`{Class|Method|Function}_overview`

Why are the :wtrl_label:`{Class|Method|Function}_overview` sections separated from the
:wtrl_label:`Public_{class|method|function}` sections? The information from the :wtrl_label:`Overview` section
would fit thematically within the :wtrl_label:`Public` sections, and the docstring would be more concise.

:wtrl_label:`Status`:
	active

:wtrl_label:`Created`:
	2026-07-24

:wtrl_label:`Related rules`:
	MCLO-001, MFNO-001,
	MPCL-001, MPFN-001,
	CCLO-001, CMTO-001,
	CPCL-001, CPMT-001

:wtrl_label:`Rationale`:
	Overview sections provide an informative summary of related objects and help
	readers understand the overall structure of an API. By contrast, the
	:wtrl_label:`Public_*` sections contain normative statements defining the
	public interface.

	Keeping both concepts separate allows informative and normative content to
	coexist without assigning normative meaning to descriptive summaries.

	In practice this separation rarely increases documentation effort, since the
	overview sections are optional. Authors who consider them unnecessary may omit
	them entirely without affecting the normative documentation.

:wtrl_label:`Consequences`:
	Mixing overview sections with :wtrl_label:`Public_*` sections would violate the
	principle |BinNorm|, which requires informative and normative content
	to remain clearly separated.

	Furthermore, declaring overview entries to be normative would violate
	|LoII| (*Locality of Information, Input*) and
	|SSoT| (*Single Source of Truth*). A documented object's own docstring
	is the only authoritative location for normative statements describing that
	object. Repeating or relocating such information into overview sections would
	introduce duplication and additional maintenance effort.

.. _rfr_0003:

.. rubric:: [RFR-0003] -- On sections :wtrl_label:`Public_{variables|constants|types}`

Why does Waterloo not apply the separation introduced in RFR-0002 to
sections :wtrl_label:`Public_{variables|constants|types}` and (non-existing)
sections :wtrl_label:`{Variable|Constant|Type}_overview`}?

:wtrl_label:`Status`:
	active

:wtrl_label:`Created`:
	2026-07-25

:wtrl_label:`Related rules`:
	MPCON-001, MPVAR-001, MPTYP-001,
	CPCON-001, CPVAR-001, CPTYP-001

:wtrl_label:`Rationale`:
	While modules, classes, functions, and methods each have their own docstring,
	variables, constants, and types do not. Consequently, Waterloo had to choose
	between the following approaches:

	* introduce a synthetic docstring mechanism for these categories;
	* rely on an unofficial convention, for example interpreting a nearby string
	  literal as the object's docstring;
	* place the normative documentation into dedicated
	  :wtrl_label:`Public_{variables|constants|types}` sections of the parent
	  module or class.

	Waterloo deliberately adopts the latter approach. Introducing synthetic
	docstrings would make the language more intrusive, while relying on unofficial
	conventions is considered inappropriate for normative documentation.

:wtrl_label:`Consequences`:
	As explained above, the parent module or class already serves as the
	authoritative location for the normative documentation of variables,
	constants, and types.

	Introducing separate overview sections would place informative summaries
	immediately beside the corresponding normative documentation. Unlike the
	situation described in RFR-0002, this separation would provide little practical
	benefit while increasing the overall size and complexity of the documentation.

	This design preserves the principles |BinNorm|, |SSoT|, and |LoII|.

	The parent module or class becomes the authoritative documentation location
	for variables, constants, and types. Since the normative documentation already
	resides there, introducing additional overview sections would separate closely
	related information without providing the benefits described in RFR-0002.

.. _rfr_0004:

.. rubric:: [RFR-0004] -- On section :wtrl_label:`Raises`

Why was the content of a :wtrl_label:`Raises.<Exception>` subsection originally
restricted to a flat sequence of text lines, similarly to
:wtrl_label:`Contract.general`, and why are Waterloo table blocks now permitted?

:wtrl_label:`Status`:
	resolved

:wtrl_label:`Created`:
	2026-09-26

:wtrl_label:`Related rules`:
	RAI-005, RAI-006, TBL-001

:wtrl_label:`Rationale`:
	The label of a :wtrl_label:`Raises.<Exception>` entry denotes a resolvable
	exception class. A callable may raise one exception class for several distinct
	reasons. For example, :wtrl_class:`RuntimeError` can cover many failure modes
	when the implementation does not expose more specific derived exception
	classes.

	Waterloo therefore encourages authors to state the individual circumstances
	under which an exception may be raised. The original deliberately flat
	representation made these circumstances visible as separate logical lines and
	discouraged presentation-oriented structures that can obscure the exceptional
	control-flow contract.

:wtrl_label:`Consequences`:
	The original restriction proved unnecessarily strong. A table can make many
	related failure modes, such as error codes carried by one exception class,
	more compact and easier to scan without weakening the contract. Consequently,
	RAI-005 permits Waterloo table blocks as defined in TBL-001.

	Nested subsections and arbitrary nested itemisation remain disallowed. Authors
	must use text lines and, where useful, table rows to express the circumstances
	required by RAI-006 clearly and completely.

.. _rfr_0005:

.. rubric:: [RFR-0005] -- On the restricted structure of profile :wtrl_value:`inherited_method`

Why does profile :wtrl_value:`inherited_method` permit only a small, fixed set
of sections and only subsections :wtrl_label:`Contract.general` and
:wtrl_label:`Contract.base` in its normative contract?

:wtrl_label:`Status`:
	active

:wtrl_label:`Created`:
	2026-09-28

:wtrl_label:`Related rules`:
	DOC-006, PRE-020, CON-035, CON-042, CON-045, SCP-008

:wtrl_label:`Rationale`:
	The :wtrl_value:`inherited_method` profile represents a narrow specialization
	of an already documented base method. Its purpose is to connect the derived
	method to that base method and to record only the information needed to
	concretize the inherited behavior. The base method remains the authoritative
	location for the complete callable contract.

	Typically, the derived method retains the same parameters and return contract,
	subject to ordinary Liskov-substitution compatibility. This is a common case,
	not a requirement of the profile. The essential condition is that the derived
	method does not introduce a sufficiently independent public contract to need
	its own full callable documentation.

	Allowing :wtrl_label:`Parameters`, :wtrl_label:`Returns`, or
	:wtrl_label:`Raises` here would invite duplicated contract statements and make
	it unclear whether the base-method contract or the derived-method docstring is
	authoritative. The restricted profile therefore preserves |SSoT| and |LoII|:
	the inherited-method docstring identifies and specializes the base contract
	without reproducing it.

:wtrl_label:`Consequences`:
	If an overriding method changes its public callable contract, for example by
	requiring different arguments, promising a materially different result, or
	introducing distinct exceptional behavior, authors |must| use profile
	:wtrl_value:`method` rather than :wtrl_value:`inherited_method`. This requires
	more documentation, but makes the changed contract explicit and local to the
	method that defines it.

	The profile also presupposes that the base method is itself documented: rule
	CON-045 requires the method referenced in :wtrl_label:`Contract.base` to have
	a valid docstring, once CON-042 to CON-044 have resolved it to the
	corresponding base-class method. A derived method cannot specialize a
	contract that does not exist. In a chain of overrides this makes
	documentation proceed from the base toward the leaves: each method is
	documented as :wtrl_value:`method` -- or itself inherits from an already
	documented one -- before an override of it may adopt
	:wtrl_value:`inherited_method`.

.. _rfr_0006:

.. rubric:: [RFR-0006] -- On section :wtrl_label:`Returns` for callables returning :wtrl_value:`None`

Why must a :wtrl_label:`Returns` section be present even for a callable annotated
to return :wtrl_value:`None`, when the :wtrl_label:`Raises` section of
:ref:`rfr_0001` may be empty? Both look like a "nothing to document" case.

:wtrl_label:`Status`:
	active

:wtrl_label:`Created`:
	2026-09-29

:wtrl_label:`Related rules`:
	RET-001, RET-003, RET-006,
	RAI-001

:wtrl_label:`Rationale`:
	The apparent asymmetry dissolves once each section is read for what it
	describes. :wtrl_label:`Raises` describes a *set* of exception classes, and
	the empty set is a meaningful value of that set: an empty section is the
	normative statement that no exception class belongs to the contract (see
	:ref:`rfr_0001`).

	:wtrl_label:`Returns` describes *the return value*. A callable annotated to
	return :wtrl_value:`None` does not return "nothing"; it returns the value
	:wtrl_value:`|None|`, the sole inhabitant of :wtrl_type:`NoneType`. That is a
	definite value, not an absent one, so the section always has something to
	state and is therefore never empty. Rule RET-003 accordingly requires the
	section to explain the return value, and RET-006 recommends naming the token
	:wtrl_value:`|None|`.

:wtrl_label:`Consequences`:
	Documenting :wtrl_value:`|None|` explicitly records a deliberate contract: the
	callable is used for its side effects, and callers |must_not| rely on a
	returned value. Omitting the section, which RET-001 forbids, would conflate
	*"returns None by design"* with *"the return value was not considered"* -- the
	same distinction :ref:`rfr_0001` preserves for :wtrl_label:`Raises`.

	Both sections thus follow one consistent principle: an empty section is
	admissible exactly when the empty set is itself the value being documented.
	This holds for :wtrl_label:`Raises` but not for :wtrl_label:`Returns`.
