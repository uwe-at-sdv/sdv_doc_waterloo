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
	semantic_markup_allowed: bool
	explanation: list[str]


class SectionPropertyInfo_t(TypedDict):
	category: SectionBodyCategory_t
	normativity: Normativity_t
	label_kind: LabelKind_t
	profile: list[Profile_t] | None
	must_exist: MustExist_t
	hint: str


class ExplainSection_t(TypedDict):
	profile: Profile_t
	label: str
	title: str
	body_category: SectionBodyCategory_t
	normativity: Normativity_t
	label_kind: LabelKind_t
	available_profiles: list[Profile_t]
	allowed_subsections: list[str]
	role_notes: list[str]
	body: list[str]
	template: list[str]
	hint: list[str]
	try_next: list[str]


WTRL_MARKUP_ROLE_LIST: Final[list[str]] = [role for role in WTRL_MARKUP_ROLES.strip("()").split("|") if role]

ExplainSectionBodyCategory: Final[Dict[str, SectionBodyCategoryExplanation_t]] = {
	"STRUCTURE": {
		"semantic_markup_allowed": False,
		"explanation": [
			"The section/subsection contains no freeform text but only defines a structure of subsections and roles.",
		],
	},
	"IDENTIFIER": {
		"semantic_markup_allowed": False,
		"explanation": [
			"The section/subsection body is expected to be a single identifier, for example a scope or status marker.",
		],
	},
	"QUALIFIED_IDENTIFIER": {
		"semantic_markup_allowed": False,
		"explanation": [
			"The section/subsection body is expected to be a single qualified identifier, for example a fully qualified type name or a reference to another documented object.",
		],
	},
	"LIST_OF_IDENTIFIERS": {
		"semantic_markup_allowed": False,
		"explanation": [
			"The section/subsection body is expected to be a list of identifiers, for example a list of definition items.",
		],
	},
	"LIST_OF_QUALIFIED_IDENTIFIERS": {
		"semantic_markup_allowed": False,
		"explanation": [
			"The section/subsection body is expected to be a list of qualified identifiers, for example a list of method or class names.",
		],
	},
	"ITEMIZED_TEXT": {
		"semantic_markup_allowed": True,
		"explanation": [
			"The section/subsection body is expected to be a list of freeform text entries.",
			"Itemization is expressed by bullets and lines, not by decorative spacing.",
		],
	},
	"FREEFORM_TEXT": {
		"semantic_markup_allowed": True,
		"explanation": [
			"The section/subsection body is expected to be freeform text, for example a general description or a note.",
			"As opposed to itemized text, the body is not expected to be structured into separate entries but can be a single freeform block.",
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

SECTION_TO_SUBSECTIONS_BY_PROFILE: Final[Dict[Profile_t, Dict[str, List[str]]]] = {
	"module": {
		"Preamble": ["profile", "normative_sections", "status", "scope"],
		"Definitions": ["<item>"],
		"Terminology": ["<item>"],
		"Description": [],
		"Notes": ["<item>"],
		"See_also": [],
		"Contract": ["general"],
		"Public_classes": [],
		"Class_overview": ["<item>"],
		"Public_functions": [],
		"Function_overview": ["<item>"],
		"Public_types": ["<item>"],
		"Public_variables": ["<item>"],
		"Public_constants": ["<item>"],
	},
	"class": {
		"Preamble": ["profile", "normative_sections", "status", "scope"],
		"Definitions": ["<item>", "_inherit"],
		"Terminology": ["<item>"],
		"Description": [],
		"Notes": ["<item>"],
		"See_also": [],
		"Contract": ["general", "constructor", "traits"],
		"Derived_from": [],
		"Public_classes": [],
		"Class_overview": ["<item>"],
		"Public_methods": [],
		"Method_overview": ["<item>"],
		"Public_types": ["<item>"],
		"Public_variables": ["<item>"],
		"Public_constants": ["<item>"],
		"Factory": ["<item>"],
	},
	"function": {
		"Preamble": ["profile", "normative_sections", "status", "scope"],
		"Definitions": ["<item>", "_inherit"],
		"Terminology": ["<item>"],
		"Description": [],
		"Notes": ["<item>"],
		"See_also": [],
		"Contract": ["general", "invariants", "requires", "ensures"],
		"Parameters": ["<item>"],
		"Returns": [],
		"Raises": ["<item>"],
	},
	"method": {
		"Preamble": ["profile", "normative_sections", "status", "scope"],
		"Definitions": ["<item>", "_inherit"],
		"Terminology": ["<item>"],
		"Description": [],
		"Notes": ["<item>"],
		"See_also": [],
		"Contract": ["general", "invariants", "requires", "ensures"],
		"Parameters": ["<item>"],
		"Returns": [],
		"Raises": ["<item>"],
	},
	"inherited_method": {
		"Preamble": ["profile", "normative_sections", "status", "scope"],
		"Definitions": ["<item>", "_inherit"],
		"Terminology": ["<item>"],
		"Description": [],
		"Notes": ["<item>"],
		"See_also": [],
		"Contract": ["general", "base"],
	},
}

SECTIONS_BY_PROFILE: Final[Dict[Profile_t, List[str]]] = {
	profile: list(section_map.keys())
	for profile, section_map in SECTION_TO_SUBSECTIONS_BY_PROFILE.items()
}

_COMMON_ROLE_NOTES = [
	"Semantic roles are the named sub-parts used inside a body, for example parameters, return values, notes, or references.",
	"Inline markup roles are: " + ", ".join(WTRL_MARKUP_ROLE_LIST) + ".",
	"Keep one indentation level per nesting level; structure is expressed by TAB-indented bullets and lines, not by decorative spacing.",
]

_BASE_SECTION_SPECS: Dict[str, Dict[str, Any]] = {
	"Contract": {
		"title": "Contract",
		"body": [
			"Contract contains the rules that the section enforces.",
			"It is the place where the validator expects the normative core of the object.",
		],
		"hint": [
			"try waterlint explain-section --label Contract",
			"Contract is the normative core of the docstring section.",
		],
		"try_next": ["waterlint explain-subsection --label constructor"],
	},
	"Preamble": {
		"title": "Preamble",
		"body": [
			"Preamble declares which profile the docstring follows and which sections are normative.",
			"It is the entry point for validating the rest of the document.",
		],
		"hint": [
			"try waterlint explain-section --label Preamble",
			"Preamble declares the profile and the normative section set.",
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
		],
		"hint": [
			"try waterlint explain-section --label Parameters",
			"Parameters list formal arguments in a callable docstring.",
		],
		"try_next": ["waterlint explain-subsection --label args"],
	},
	"Returns": {
		"title": "Returns",
		"body": [
			"Returns documents what the callable yields or returns.",
		],
		"hint": [
			"try waterlint explain-section --label Returns",
			"Returns describes the returned value or object.",
		],
		"try_next": ["waterlint explain-subsection --label return_value"],
	},
	"Raises": {
		"title": "Raises",
		"body": [
			"Raises documents documented exception conditions.",
		],
		"hint": [
			"try waterlint explain-section --label Raises",
			"Raises lists documented exceptions and their conditions.",
		],
		"try_next": ["waterlint explain-subsection --label ValueError"],
	},
	"Notes": {
		"title": "Notes",
		"body": [
			"Notes are used for additional guidance that is not part of the normative contract.",
		],
		"hint": [
			"try waterlint explain-section --label Notes",
			"Notes stays informative unless the surrounding profile explicitly makes it normative.",
		],
		"try_next": ["waterlint explain-section --label Notes"],
	},
}


def _available_profiles_for_label(label: str) -> list[Profile_t]:
	return [profile for profile, section_map in SECTION_TO_SUBSECTIONS_BY_PROFILE.items() if label in section_map]


def build_section_explanation(label: str, profile: Profile_t) -> ExplainSection_t | None:
	section_map = SECTION_TO_SUBSECTIONS_BY_PROFILE.get(profile)
	if section_map is None or label not in section_map:
		return None
	base = _BASE_SECTION_SPECS.get(label)
	if base is None:
		return None
	cat_info = SECTION_PROPERTIES.get(label, {"category": "STRUCTURE", "normativity": "informative", "label_kind": "NOT_APPLICABLE", "hint": ""})
	allowed_subsections = list(section_map.get(label, []))
	template: list[str] = [f"{label}:"]
	if cat_info["category"] == "STRUCTURE":
		for subsection in allowed_subsections:
			template.append(f"\t{subsection}:")
			template.append("\t\t...")
	elif cat_info["category"] == "FREEFORM_TEXT":
		template.append("\t...")
	elif cat_info["category"] == "LIST_OF_IDENTIFIERS":
		template.append("\titem_1")
		template.append("\titem_2")
	elif cat_info["category"] == "LIST_OF_QUALIFIED_IDENTIFIERS":
		template.append("\tpackage.module.Class")
		template.append("\tpackage.module.function")
	elif cat_info["category"] == "IDENTIFIER":
		template.append("\tidentifier")
	elif cat_info["category"] == "QUALIFIED_IDENTIFIER":
		template.append("\tpackage.module.Class")
	else:
		template.append("\t...")
	hint = list(base["hint"])
	hint.insert(0, f"Profile: {profile}")
	hint.append(f"Allowed subsections for {label}: {', '.join(allowed_subsections) if allowed_subsections else 'none'}")
	hint.append(f"try waterlint explain-section --label {label} --profile {profile}")
	return {
		"profile": profile,
		"label": label,
		"title": base["title"],
		"body_category": cat_info["category"],
		"normativity": cat_info["normativity"],
		"label_kind": cat_info["label_kind"],
		"available_profiles": _available_profiles_for_label(label),
		"allowed_subsections": allowed_subsections,
		"role_notes": list(_COMMON_ROLE_NOTES),
		"body": list(base["body"]),
		"template": template,
		"hint": hint,
		"try_next": list(base["try_next"]),
	}


def render_explanation_text(spec: ExplainSection_t) -> str:
	lines: list[str] = []
	lines.append(f"Profile: {spec['profile']}")
	lines.append(f"Label: {spec['label']}")
	lines.append(f"Title: {spec['title']}")
	lines.append(f"Body category: {spec['body_category']}")
	lines.append(f"Normativity: {spec['normativity']}")
	lines.append(f"Label kind: {spec['label_kind']}")
	lines.append("Available profiles:")
	for profile in spec["available_profiles"]:
		lines.append(f"\t- {profile}")
	lines.append("Allowed subsections:")
	for subsection in spec["allowed_subsections"]:
		lines.append(f"\t- {subsection}")
	lines.append("Role notes:")
	for note in spec["role_notes"]:
		lines.append(f"\t- {note}")
	lines.append("Body:")
	for line in spec["body"]:
		lines.append(f"\t{line}")
	lines.append("Template:")
	for line in spec["template"]:
		lines.append(f"\t{line}")
	lines.append("Hint:")
	for line in spec["hint"]:
		lines.append(f"\t{line}")
	if spec["try_next"]:
		lines.append("Try:")
		for line in spec["try_next"]:
			lines.append(f"\t{line}")
	return "\n".join(lines) + "\n"


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
		"allowed_subsections": list(spec["allowed_subsections"]),
		"role_notes": list(spec["role_notes"]),
		"body": list(spec["body"]),
		"template": list(spec["template"]),
		"hint": list(spec["hint"]),
		"try": list(spec["try_next"]),
	}
