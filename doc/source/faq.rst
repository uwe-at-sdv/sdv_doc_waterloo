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

:wtrl_label:`Consequences`
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
	MPCON-001, MPVAR-001,MPTYP-001
	CPCON-001, CPVAR-001,CPTYP-001

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
