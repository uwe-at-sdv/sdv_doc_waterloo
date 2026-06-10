#!/usr/bin/env python3
r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
	scope:
		extension
Contract:
	general:
		|Must| provide shared explanation data and renderers for waterlint explain commands.
Public_functions:
	build_section_explanation, render_explanation_text, render_explanation_json
Function_overview:
	build_section_explanation:
		Build a profile-specific section explanation for a label.
	render_explanation_text:
		Render a section explanation as raw text.
	render_explanation_json:
		Render a section explanation as JSON-ready data.
"""

from __future__ import annotations

from typing import Any, Final, Dict, List, Literal, TypedDict

from sdv.doc.waterloo.docitem_helper import WTRL_MARKUP_ROLES

SectionBodyCategory_t = Literal[
	"STRUCTURE",
	"IDENTIFIER",
	"QUALIFIED_IDENTIFIER",
	"LIST_OF_IDENTIFIERS",
	"LIST_OF_QUALIFIED_IDENTIFIERS",
	"ITEMIZED_TEXT",
	"FREEFORM_TEXT",
]


Profile_t = Literal["module", "class", "function", "method", "inherited_method"]

Normativity_t = Literal["not_applicable", "normative", "informative", "can_be_both"]

LabelKind_t = Literal["IDENTIFIER", "QUALIFIED_IDENTIFIER", "LIST_OF_IDENTIFIERS", "ANY_STRING", "NOT_APPLICABLE"]

MustExist_t = Literal["yes", "no", "depends_on_context"]

class SectionBodyCategoryExplanation_t(TypedDict):
	markup_allowed: bool
	renders_outer_bullets: bool
	inner_lists_allowed: bool
	explanation: list[str]


class SectionPropertyInfo_t(TypedDict):
	category: SectionBodyCategory_t
	normativity: Normativity_t
	label_kind: LabelKind_t
	profile: list[Profile_t] | None
	must_exist: MustExist_t
	hint: str


class SubsectionExplainInfo_t(TypedDict):
	label: str
	normativity: Normativity_t
	must_exist: MustExist_t
	label_kind: LabelKind_t


class ItemizationExplain_t(TypedDict, total=False):
	allowed: bool
	renders_outer_bullets: bool
	inner_lists_allowed: bool
	reason: str
	explanation: list[str]


class FeatureExplain_t(TypedDict, total=False):
	allowed: bool
	reason: str
	explanation: list[str]


class ExplainSection_t(TypedDict):
	profile: Profile_t
	label: str
	title: str
	body_category: SectionBodyCategory_t
	normativity: Normativity_t
	label_kind: LabelKind_t
	available_profiles: list[Profile_t]
	subsections: list[SubsectionExplainInfo_t]
	body: list[str]
	template: list[str]
	hint: list[str]
	try_next: list[str]
	itemization: ItemizationExplain_t
	markup: FeatureExplain_t


WTRL_MARKUP_ROLE_LIST: Final[list[str]] = [role for role in WTRL_MARKUP_ROLES.strip("()").split("|") if role]

EXPLAIN_TEMPLATES: Final[Dict[SectionBodyCategory_t, list[str]]] = {
	"STRUCTURE": [
		"{label}:",
		"\t{subsection}:",
		"\t\t...",
	],
	"IDENTIFIER": [
		"{label}:",
		"\tidentifier",
	],
	"QUALIFIED_IDENTIFIER": [
		"{label}:",
		"\tpackage.module.Class",
	],
	"LIST_OF_IDENTIFIERS": [
		"{label}:",
		"\titem_1, item_2, item_3, ...",
	],
	"LIST_OF_QUALIFIED_IDENTIFIERS": [
		"{label}:",
		"\tpkg.mod.Class1, pkg.mod.Class2, pkg.mod.Class3, ...",
	],
	"ITEMIZED_TEXT": [
		"{label}:",
		"\t|MUST| do this.",
		"\t|MUST| do that.",
		"\t|Must| do the following task consisting of these steps:",
		"\t+ |Must| do step1",
		"\t+ |Must| do step2",
	],
	"FREEFORM_TEXT": [
		"{label}:",
		"\t...",
	],
}

ExplainSectionBodyCategory: Final[Dict[str, SectionBodyCategoryExplanation_t]] = {
	"STRUCTURE": {
		"markup_allowed": False,
		"renders_outer_bullets": False,
		"inner_lists_allowed": False,
		"reason": "Structured section with subsection-only content.",
		"explanation": [
			"The section/subsection contains no freeform text but only defines a structure of subsections and roles.",
		],
	},
	"IDENTIFIER": {
		"markup_allowed": False,
		"renders_outer_bullets": False,
		"inner_lists_allowed": False,
		"reason": "Single identifier body.",
		"explanation": [
			"The section/subsection body is expected to be a single identifier, for example a scope or status marker.",
		],
	},
	"QUALIFIED_IDENTIFIER": {
		"markup_allowed": False,
		"renders_outer_bullets": False,
		"inner_lists_allowed": False,
		"reason": "Single qualified identifier body.",
		"explanation": [
			"The section/subsection body is expected to be a single qualified identifier, for example a fully qualified type name or a reference to another documented object.",
		],
	},
	"LIST_OF_IDENTIFIERS": {
		"markup_allowed": False,
		"renders_outer_bullets": False,
		"inner_lists_allowed": False,
		"reason": "Flat list of identifiers.",
		"explanation": [
			"The section/subsection body is expected to be a list of identifiers, for example a list of definition items.",
		],
	},
	"LIST_OF_QUALIFIED_IDENTIFIERS": {
		"markup_allowed": False,
		"renders_outer_bullets": False,
		"inner_lists_allowed": False,
		"reason": "Flat list of qualified identifiers.",
		"explanation": [
			"The section/subsection body is expected to be a list of qualified identifiers, for example a list of method or class names.",
		],
	},
	"ITEMIZED_TEXT": {
		"markup_allowed": True,
		"renders_outer_bullets": True,
		"inner_lists_allowed": True,
		"reason": "Rendered with outer bullets; inner lists allowed.",
		"explanation": [
			"The section/subsection body is rendered with outer bullets for each logical line.",
			"Waterloo itemization is flat in the source text: nesting is expressed by the choice of list marker, not by indentation.",
			"Inner lists may still be built inside a logical item.",
		],
	},
	"FREEFORM_TEXT": {
		"markup_allowed": True,
		"renders_outer_bullets": False,
		"inner_lists_allowed": True,
		"reason": "Rendered without outer bullets; inner lists allowed.",
		"explanation": [
			"The section/subsection body is rendered without outer bullets.",
			"The body may still contain inner lists when the content benefits from structured sub-points.",
			"As opposed to itemized text, the main body is not split into outer list items by the renderer.",
		],
	},
}

# * This mapping is a machine-readable representation of a subset of the rules defined in the documentation standard.
#   The documentation remains the Single Source of Truth for the standard, and this mapping is a distilled representation
#   of the relevant rules for the explain command.
# * For attributes "profile" and "must_exist" we assume orthogonality in the sense that there are no mixed cases
#   where a label is required in some profiles but not in others. If such cases arise, the structure
#   of this mapping would need to be changed to be profile-specific.
# * Whenever "label_kind" is not "NOT_APPLICABLE", we must specify the rules for the label kind
#   in the comment above the respective entry, for example "label_kind" rules: DEF-004, DEF-005.
SECTION_PROPERTIES: Final[Dict[str, SectionPropertyInfo_t]] = {
	# Normativity does not apply to Preamble because normativity is declared therein, and normativity
	# does not apply to subsections because they are normative if and only if the surrounding section is normative (BinNorm).
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: not_applicable
	# "must_exist" rules: PRE-001
	"Preamble": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, PRE-003
	# "normativity" rules: not_applicable
	# "must_exist" rules: PRE-003
	"Preamble.profile": {"category": "IDENTIFIER", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, PRE-006
	# "normativity" rules: not_applicable
	# "must_exist" rules: PRE-006
	"Preamble.normative_sections": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: PRE-016, PRE-019, STA-001
	# "normativity" rules: not_applicable
	# "must_exist" rules: STA-001
	"Preamble.status": {"category": "IDENTIFIER", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "profile": ["function","method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, SCP-001
	# "normativity" rules: not_applicable
	# "must_exist" rules: SCP-001
	"Preamble.scope": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: DEF-002
	# "must_exist" rules: DEF-001
	"Definitions": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, DEF-003
	# "label_kind" rules: DEF-004, DEF-005
	# "normativity" rules: BinNorm, DEF-002
	# "must_exist" rules: DEF-020
	"Definitions.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "LIST_OF_IDENTIFIERS", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DEF-011, DEF-012
	# "normativity" rules: BinNorm, DEF-002
	# "must_exist" rules: DEF-012
	"Definitions._inherit": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# Terminology is the informative sister of Definitions. It is not allowed to contain normativity keywords but rather general explanations of terms.
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: TERM-002, TERM-003
	# "must_exist" rules: TERM-001
	"Terminology": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, TERM-004
	# "label_kind" rules: TERM-005, TERM-006
	# "normativity" rules: BinNorm, TERM-002
	# "must_exist" rules: TERM-009
	"Terminology.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "ANY_STRING", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: CON-002
	# "must_exist" rules: CON-001
	"Contract": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-022, CON-023, CON-024, CON-036
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-022, CON-023, CON-024, CON-036
	"Contract.general": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-007
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-007
	"Contract.constructor": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["class"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-039
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-039
	"Contract.base": {"category": "QUALIFIED_IDENTIFIER", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-012
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-012
	"Contract.traits": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: CON-025
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-025
	"Contract.invariants": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["function","method"], "must_exist": "no", "hint": ""},
	# "profile" rules: CON-047
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-047
	"Contract.requires": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["function","method"], "must_exist": "no", "hint": ""},
	# "profile" rules: CON-049
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-049
	"Contract.ensures": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["function","method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: DESC-002
	# "must_exist" rules: DESC-001
	"Description": {"category": "FREEFORM_TEXT", "normativity": "can_be_both", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-004
	# "normativity" rules: DER-004
	# "must_exist" rules: DER-001
	"Derived_from": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-004
	# "normativity" rules: FAC-009
	# "must_exist" rules: FAC-001
	"Factory": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: FAC-004
	# "label_kind" rules: FAC-005
	# "normativity" rules: BinNorm, FAC-009
	# "must_exist" rules: FAC-004
	"Factory.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "QUALIFIED_IDENTIFIER", "profile": ["class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPCL-002, CPCL-002
	# "must_exist" rules: MPCL-001, CPCL-001
	"Public_classes": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003
	# "normativity" rules: MPFN-002
	# "must_exist" rules: MPFN-001
	"Public_functions": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-004
	# "normativity" rules: CPMT-002
	# "must_exist" rules: CPMT-001
	"Public_methods": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPTYP-002, CPTYP-002
	# "must_exist" rules: MPTYP-001, CPTYP-001
	"Public_types": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MPTYP-003, CPTYP-003
	# "label_kind" rules: MPTYP-004, CPTYP-004
	# "normativity" rules: BinNorm, MPTYP-002, CPTYP-002
	# "must_exist" rules: MPTYP-003, CPTYP-003
	"Public_types.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPVAR-002, CPVAR-002
	# "must_exist" rules: MPVAR-001, CPVAR-001
	"Public_variables": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MPVAR-003, CPVAR-003
	# "label_kind" rules: MPVAR-004, CPVAR-004
	# "normativity" rules: BinNorm, MPVAR-002, CPVAR-002
	# "must_exist" rules: MPVAR-003, CPVAR-003
	"Public_variables.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPCON-002, CPCON-002
	# "must_exist" rules: MPCON-001, CPCON-001
	"Public_constants": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MPCON-003, CPCON-003
	# "label_kind" rules: MPCON-004, CPCON-004
	# "normativity" rules: BinNorm, MPCON-002, CPCON-002
	# "must_exist" rules: MPCON-003, CPCON-003
	"Public_constants.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MCLO-002, CCLO-002
	# "must_exist" rules: MCLO-001, CCLO-001
	"Class_overview": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MCLO-004, CCLO-004
	# "label_kind" rules: MCLO-005, CCLO-005
	# "normativity" rules: BinNorm, MCLO-002, CCLO-002
	# "must_exist" rules: MCLO-010, CCLO-010
	"Class_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-004
	# "normativity" rules: CMTO-002
	# "must_exist" rules: CMTO-001
	"Method_overview": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "NOT_APPLICABLE", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: CMTO-004
	# "label_kind" rules: CMTO-005
	# "normativity" rules: BinNorm, CMTO-002
	# "must_exist" rules: CMTO-010
	"Method_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "profile": ["class"], "must_exist": "no", "hint": ""},
	
	# "profile" rules: DOC-003
	# "normativity" rules: MFNO-002
	# "must_exist" rules: MFNO-001
	"Function_overview": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "NOT_APPLICABLE", "profile": ["module"], "must_exist": "no", "hint": ""},
	# "profile" rules: MFNO-004
	# "label_kind" rules: MFNO-005
	# "normativity" rules: BinNorm, MFNO-002
	# "must_exist" rules: MFNO-010
	"Function_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "profile": ["module"], "must_exist": "no", "hint": ""},

	# We classify Parameters.<items>."must_exists" as "depends_on_context" because for any given value of <item>
	# it can be determined whether it must exist or not, but there is no general rule that applies to all items of the same label.
	# "profile" rules: DOC-005
	# "normativity" rules: PAR-002
	# "must_exist" rules: PAR-001
	"Parameters": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["function","method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: PAR-008
	# "label_kind" rules: PAR-006
	# "normativity" rules: BinNorm, PAR-002
	# "must_exist" rules: PAR-004, PAR-005
	"Parameters.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["function","method"], "must_exist": "depends_on_context", "hint": ""},

	# "profile" rules: DOC-005
	# "normativity" rules: RET-002
	# "must_exist" rules: RET-001
	"Returns": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["function","method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: DOC-005
	# "normativity" rules: RAI-002
	# "must_exist" rules: RAI-001
	"Raises": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "profile": ["function","method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: RAI-011
	# "label_kind" rules: RAI-008
	# "normativity" rules: BinNorm, RAI-002
	# "must_exist" rules: RAI-011
	"Raises.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "QUALIFIED_IDENTIFIER", "profile": ["function","method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: NOTE-002
	# "must_exist" rules: NOTE-001
	"Notes": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, NOTE-005
	# "label_kind" rules: NOTE-006
	# "normativity" rules: BinNorm, NOTE-002
	# "must_exist" rules: NOTE-008
	"Notes.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "ANY_STRING", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: SEE-011
	# "must_exist" rules: SEE-001
	"See_also": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "can_be_both", "label_kind": "NOT_APPLICABLE", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
}

_PROFILE_ORDER: Final[list[Profile_t]] = ["module", "class", "function", "method", "inherited_method"]

SECTION_SUBSECTIONS: Final[Dict[str, Dict[Profile_t, List[str]]]] = {
	"Preamble": {
		profile: ["profile", "normative_sections", "status", "scope"]
		for profile in _PROFILE_ORDER
	},
	"Definitions": {
		profile: ["<item>", "_inherit"] if profile in ("class", "function", "method", "inherited_method") else ["<item>"]
		for profile in _PROFILE_ORDER
	},
	"Terminology": {
		profile: ["<item>"]
		for profile in _PROFILE_ORDER
	},
	"Description": {
		profile: []
		for profile in _PROFILE_ORDER
	},
	"Notes": {
		profile: ["<item>"]
		for profile in _PROFILE_ORDER
	},
	"See_also": {
		profile: []
		for profile in _PROFILE_ORDER
	},
	"Contract": {
		"module": ["general"],
		"class": ["general", "constructor", "traits"],
		"function": ["general", "invariants", "requires", "ensures"],
		"method": ["general", "invariants", "requires", "ensures"],
		"inherited_method": ["general", "base"],
	},
	"Public_classes": {
		"module": [],
		"class": [],
	},
	"Class_overview": {
		profile: ["<item>"]
		for profile in ("module", "class")
	},
	"Public_functions": {
		"module": [],
	},
	"Function_overview": {
		"module": ["<item>"],
	},
	"Public_types": {
		profile: ["<item>"]
		for profile in ("module", "class")
	},
	"Public_variables": {
		profile: ["<item>"]
		for profile in ("module", "class")
	},
	"Public_constants": {
		profile: ["<item>"]
		for profile in ("module", "class")
	},
	"Derived_from": {
		"class": [],
	},
	"Public_methods": {
		"class": [],
	},
	"Method_overview": {
		"class": ["<item>"],
	},
	"Factory": {
		"class": ["<item>"],
	},
	"Parameters": {
		profile: ["<item>"]
		for profile in ("function", "method")
	},
	"Returns": {
		profile: []
		for profile in ("function", "method")
	},
	"Raises": {
		profile: ["<item>"]
		for profile in ("function", "method")
	},
}

SECTION_TO_SUBSECTIONS_BY_PROFILE: Final[Dict[Profile_t, Dict[str, List[str]]]] = {
	profile: {
		label: list(profile_map[profile])
		for label, profile_map in SECTION_SUBSECTIONS.items()
		if profile in profile_map
	}
	for profile in _PROFILE_ORDER
}

SECTIONS_BY_PROFILE: Final[Dict[Profile_t, List[str]]] = {
	profile: list(section_map.keys())
	for profile, section_map in SECTION_TO_SUBSECTIONS_BY_PROFILE.items()
}

_BASE_SECTION_SPECS: Dict[str, Dict[str, Any]] = {
	"Definitions": {
		"title": "Definitions",
		"body": [
			"Definitions introduces normative terms that are used later in the docstring.",
			"Each subsection label is a comma-separated list of identifiers.",
			"The first identifier names the canonical term; following identifiers name spelling or form variations of the same term.",
			"For example, the term sensitive may be introduced together with Sensitive and Sensitivity.",
		],
		"hint": [
			"try waterlint explain-section --label Definitions --profile class",
			"Definitions is the normative glossary of the docstring scope; each subsection header is a CSV list of Identifier tokens, with the first token naming the term and the remaining tokens naming variations.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Terminology": {
		"title": "Terminology",
		"body": [
			"Terminology collects informative term explanations and background notes.",
			"It helps readers understand the document without adding new normative requirements.",
		],
		"hint": [
			"try waterlint explain-section --label Terminology --profile class",
			"Terminology is informative and complements Definitions.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Description": {
		"title": "Description",
		"body": [
			"Description gives the general prose description of the object or scope.",
			"It may be normative or informative depending on the surrounding profile and context.",
		],
		"hint": [
			"try waterlint explain-section --label Description --profile module",
			"Description is the general prose block for a documented object.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Contract": {
		"title": "Contract",
		"body": [
			"Contract contains the normative rules that the section enforces.",
			"It is the place where the validator expects the executable core of the documented object.",
		],
		"hint": [
			"try waterlint explain-section --label Contract",
			"Contract is the normative core of the docstring section and the place where the tool checks the required structure.",
		],
		"try_next": ["waterlint explain-subsection --label constructor"],
	},
	"Preamble": {
		"title": "Preamble",
		"body": [
			"Preamble declares which profile the docstring follows and which sections are normative.",
			"It is the entry point for validating the rest of the document and for interpreting the remaining sections.",
		],
		"hint": [
			"try waterlint explain-section --label Preamble",
			"Preamble declares the profile, the normative section set, and the overall validation context.",
		],
		"try_next": [
			"waterlint explain-subsection --label profile",
			"waterlint explain-subsection --label normative_sections",
		],
	},
	"Parameters": {
		"title": "Parameters",
		"body": [
			"Parameters documents callable arguments in a structured way.",
			"Each subsection header names one formal parameter, and the subsection body explains its role, constraints, and expected value shape.",
		],
		"hint": [
			"try waterlint explain-section --label Parameters",
			"Parameters lists the formal arguments of a callable and explains each argument separately.",
		],
		"try_next": ["waterlint explain-subsection --label args"],
	},
	"Returns": {
		"title": "Returns",
		"body": [
			"Returns documents what the callable yields or returns.",
			"The block explains the value shape, the semantic meaning, and any important postconditions for the result.",
		],
		"hint": [
			"try waterlint explain-section --label Returns",
			"Returns describes the returned value or object and its expected meaning.",
		],
		"try_next": ["waterlint explain-subsection --label return_value"],
	},
	"Raises": {
		"title": "Raises",
		"body": [
			"Raises documents documented exception conditions.",
			"Each subsection header names an exception type, and the subsection body explains the condition under which it is raised.",
		],
		"hint": [
			"try waterlint explain-section --label Raises",
			"Raises lists the documented exception types and the conditions that trigger them.",
		],
		"try_next": ["waterlint explain-subsection --label ValueError"],
	},
	"Notes": {
		"title": "Notes",
		"body": [
			"Notes are used for additional guidance that is not part of the normative contract.",
			"They are the place for caveats, examples, implementation notes, and other reader-oriented information.",
		],
		"hint": [
			"try waterlint explain-section --label Notes",
			"Notes stays informative unless the surrounding profile explicitly makes it normative.",
		],
		"try_next": ["waterlint explain-section --label Notes"],
	},
	"See_also": {
		"title": "See_also",
		"body": [
			"See_also lists related documented objects or references.",
			"It is typically used to connect the current object to sibling sections, inherited material, or external targets.",
		],
		"hint": [
			"try waterlint explain-section --label See_also --profile module",
			"See_also is the cross-reference section for related documented objects and targets.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Public_classes": {
		"title": "Public_classes",
		"body": [
			"Public_classes lists the public class objects that belong to this module or class.",
			"Each entry is a fully qualified class name.",
		],
		"hint": [
			"try waterlint explain-section --label Public_classes --profile module",
			"Public_classes is the scope-local list of public classes.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Public_functions": {
		"title": "Public_functions",
		"body": [
			"Public_functions lists the public function objects that belong to this module.",
			"Each entry is a fully qualified function name.",
		],
		"hint": [
			"try waterlint explain-section --label Public_functions --profile module",
			"Public_functions is the module-local list of public functions.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Public_methods": {
		"title": "Public_methods",
		"body": [
			"Public_methods lists the public method objects that belong to this class.",
			"Each entry is a fully qualified method name.",
		],
		"hint": [
			"try waterlint explain-section --label Public_methods --profile class",
			"Public_methods is the class-local list of public methods.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Public_types": {
		"title": "Public_types",
		"body": [
			"Public_types lists the public type declarations exported by the current scope.",
			"Each entry names a public type, type alias, or other type-level declaration that is meant to be visible to readers and tools.",
		],
		"hint": [
			"try waterlint explain-section --label Public_types --profile module",
			"Public_types is the scope-local list of public type declarations and aliases.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Public_variables": {
		"title": "Public_variables",
		"body": [
			"Public_variables lists public variables that belong to this module or class.",
			"Each entry names a public variable exported by the scope.",
		],
		"hint": [
			"try waterlint explain-section --label Public_variables --profile module",
			"Public_variables is the scope-local list of public variables.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Public_constants": {
		"title": "Public_constants",
		"body": [
			"Public_constants lists public constants that belong to this module or class.",
			"Each entry names a public constant exported by the scope.",
		],
		"hint": [
			"try waterlint explain-section --label Public_constants --profile module",
			"Public_constants is the scope-local list of public constants.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Class_overview": {
		"title": "Class_overview",
		"body": [
			"Class_overview gives a short prose summary for each public class in the current scope.",
			"Each item is a reader-oriented narrative for one class, not a normative declaration.",
		],
		"hint": [
			"try waterlint explain-section --label Class_overview --profile module",
			"Class_overview is the informative companion to Public_classes.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Method_overview": {
		"title": "Method_overview",
		"body": [
			"Method_overview gives a short prose summary for each public method in the current class.",
			"Each item is a reader-oriented narrative for one method, not a normative declaration.",
		],
		"hint": [
			"try waterlint explain-section --label Method_overview --profile class",
			"Method_overview is the informative companion to Public_methods.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Function_overview": {
		"title": "Function_overview",
		"body": [
			"Function_overview gives a short prose summary for each public function in the current module.",
			"Each item is a reader-oriented narrative for one function, not a normative declaration.",
		],
		"hint": [
			"try waterlint explain-section --label Function_overview --profile module",
			"Function_overview is the informative companion to Public_functions.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Derived_from": {
		"title": "Derived_from",
		"body": [
			"Derived_from lists the qualified identifiers that this class is derived from.",
			"It records the immediate ancestry or derivation sources of the class.",
		],
		"hint": [
			"try waterlint explain-section --label Derived_from --profile class",
			"Derived_from names the class ancestry or derivation sources as qualified identifiers.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
	"Factory": {
		"title": "Factory",
		"body": [
			"Factory describes creation or retrieval entry points for the class.",
			"Use it for alternate constructors, class methods, or other qualified entry points that create, load, or return a related object.",
		],
		"hint": [
			"try waterlint explain-section --label Factory --profile class",
			"Factory is the creation-oriented companion to the class contract.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
}


def _available_profiles_for_label(label: str) -> list[Profile_t]:
	profile_map = SECTION_SUBSECTIONS.get(label, {})
	return [profile for profile in _PROFILE_ORDER if profile in profile_map]


def _build_template_lines(label: str, body_category: SectionBodyCategory_t, allowed_subsections: list[str]) -> list[str]:
	if body_category == "STRUCTURE":
		template = [EXPLAIN_TEMPLATES["STRUCTURE"][0].format(label=label)]
		for subsection in allowed_subsections:
			template.append(EXPLAIN_TEMPLATES["STRUCTURE"][1].format(subsection=subsection))
			template.append(EXPLAIN_TEMPLATES["STRUCTURE"][2])
		return template
	return [line.format(label=label) for line in EXPLAIN_TEMPLATES[body_category]]


def build_section_explanation(label: str, profile: Profile_t) -> ExplainSection_t | None:
	profile_map = SECTION_SUBSECTIONS.get(label)
	if profile_map is None or profile not in profile_map:
		return None
	base = _BASE_SECTION_SPECS.get(label)
	if base is None:
		return None
	# We assume that the label exists in the mapping, so we can directly access it without checking for existence.
	# The caller must ensure that the label exists in the mapping before calling this function.
	cat_info = SECTION_PROPERTIES.get(label)
	if cat_info is None:
		return None
	allowed_subsections = list(profile_map.get(profile, []))
	subsections: list[SubsectionExplainInfo_t] = []
	for subsection in allowed_subsections:
		sub_label = f"{label}.{subsection}"
		sub_info = SECTION_PROPERTIES.get(
			sub_label,
			{"normativity": "informative", "must_exist": "no", "label_kind": "NOT_APPLICABLE"},
		)
		subsections.append(
			{
				"label": subsection,
				"normativity": sub_info["normativity"],
				"must_exist": sub_info["must_exist"],
				"label_kind": sub_info["label_kind"],
			}
		)
	template = _build_template_lines(label, cat_info["category"], allowed_subsections)
	hint = list(base["hint"])
	hint.insert(0, f"Profile: {profile}")
	hint.append(f"Subsections for {label}: {', '.join(allowed_subsections) if allowed_subsections else 'none'}")
	hint.append(f"try waterlint explain-section --label {label} --profile {profile}")

	feature_category = ExplainSectionBodyCategory[cat_info["category"]]
	itemization: ItemizationExplain_t = {
		"allowed": feature_category["renders_outer_bullets"],
		"renders_outer_bullets": feature_category["renders_outer_bullets"],
		"inner_lists_allowed": feature_category["inner_lists_allowed"],
		"reason": feature_category["reason"],
	}
	if feature_category["inner_lists_allowed"]:
		itemization_lines = [
			"Waterloo itemization inside the body is flat in the source text.",
			"Inner lists are expressed by the choice of list marker, not by indentation.",
			"Inner lists may be nested inside a logical item when the content needs sub-points.",
			"Example:",
			"|Must| do this.",
			"|Must| do that.",
			"|Must| do the following task consisting of these steps:",
			"+ |Must| do step1",
			"+ |Must| do step2",
		]
		if feature_category["renders_outer_bullets"]:
			itemization_lines.append(
				"Renderers may also add outer bullets for each logical line in target formats such as Sphinx / reST."
			)
		else:
			itemization_lines.append(
				"Renderers do not add outer bullets for the body itself, but inner lists remain available."
			)
		itemization["explanation"] = itemization_lines
	if feature_category["markup_allowed"]:
		markup_token_lines = [
			"Waterloo docstrings use inline markup tokens only in free-form content lines.",
			"Inline markup tokens must not occur in section labels, subsection labels, or list entries in Identifier / Qualified Identifier sections.",
			"Tokens currently available: |Must|, |must|, |must_not|, |should|, |should_not|, |may|, |may_not|, |None|, |Self|, |True|, |False|.",
			"Semantic roles use the form |role|`content`, where role is one of: "
			+ ", ".join(WTRL_MARKUP_ROLE_LIST)
			+ ".",
			"Renderers should map the tokens to well-defined target-format constructs and preserve them when no translation is available.",
		]
		markup: FeatureExplain_t = {
			"allowed": True,
			"reason": "The body category permits semantic markup.",
			"explanation": markup_token_lines,
		}
	else:
		markup = {
			"allowed": False,
			"reason": "The body category does not permit semantic markup.",
		}

	explanation: ExplainSection_t = {
		"profile": profile,
		"label": label,
		"title": base["title"],
		"body_category": cat_info["category"],
		"normativity": cat_info["normativity"],
		"label_kind": cat_info["label_kind"],
		"available_profiles": _available_profiles_for_label(label),
		"subsections": subsections,
		"body": list(base["body"]),
		"template": template,
		"hint": hint,
		"try_next": list(base["try_next"]),
		"itemization": itemization,
		"markup": markup,
	}
	return explanation


def render_explanation_text(spec: ExplainSection_t) -> str:
	return "LATER - must implement JSON first"


def render_explanation_json(spec: ExplainSection_t) -> dict[str, Any]:
	return {
		"kind": "section_explanation",
		"profile": spec["profile"],
		"label": spec["label"],
		"title": spec["title"],
		"body_category": spec["body_category"],
		"normativity": spec["normativity"],
		"label_kind": spec["label_kind"],
		"available_profiles": list(spec["available_profiles"]),
		"subsections": list(spec["subsections"]),
		"body": list(spec["body"]),
		"template": list(spec["template"]),
		"hint": list(spec["hint"]),
		"try": list(spec["try_next"]),
		"itemization": dict(spec["itemization"]),
		"markup": dict(spec["markup"]),
	}
