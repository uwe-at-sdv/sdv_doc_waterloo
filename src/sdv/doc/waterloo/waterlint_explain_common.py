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
	get_section_explanation, render_explanation_text, render_explanation_json
Function_overview:
	get_section_explanation:
		Look up a section explanation by label.
	render_explanation_text:
		Render a section explanation as raw text.
	render_explanation_json:
		Render a section explanation as JSON-ready data.
"""

from __future__ import annotations

from typing import Any, Dict, Final, List, Literal, TypedDict

# The single source of truth for semantic markup roles.
# These are cited in each explanation of sections and subsections, where applicable.
from sdv.doc.waterloo.docitem_helper import WTRL_MARKUP_ROLES

# The normative documentation classifies each section and subsection role
# as one of these categories, which controls the expected content and formatting.
# Sections without textual content are considered as cateogry "STRUCTURE".
# We keep in mind that normativity is per section (BinNorm), so whenever
# a section is normative, all its subsections are normative as well.
#
# Example: Section "Contract" is a normative section of category "STRUCTURE" that contains no
# textual content itself but only defines subsections like "general", and depending on profile
# "constructor" or "requires"/"ensures"/"invariants".
#
# Example: Section "Returns" is a normative section of category "FREEFORM_TEXT"
# that contains a freeform textual description of the return value.
#
SectionBodyCategory_t = Literal["STRUCTURE","IDENTIFIER","QUALIFIED_IDENTIFIER","LIST_OF_IDENTIFIERS","LIST_OF_QUALIFIED_IDENTIFIERS","ITEMIZED_TEXT","FREEFORM_TEXT"]

class SectionBodyCategoryExplanation_t(TypedDict):
	semantic_markup_allowed: bool
	explanation: list[str]

Normativity_t = Literal["not_applicable", "normative", "informative", "can_be_both"]

class LabelCategoryInfo_t(TypedDict):
	category: SectionBodyCategory_t
	normativity: Normativity_t

ExplainSectionBodyCategory: Final[Dict[str, SectionBodyCategoryExplanation_t]] = {
	"STRUCTURE": {
		"semantic_markup_allowed": False,
		"explanation": [
			"The section/subsection contains no freeform text but only defines a structure of subsections and roles."
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
			"The section/subsection body is expected to be a list of freeform text entries,",
			"which are typically interpreted as an executable contract.",
			"Itemization is expressed by bullets and lines, not by decorative spacing, for example:",
			"* item 1",
			"* item 2",
			"+ item 2.1",
			"+ item 2.2",
			"- item 2.2.1",
			"- item 2.2.2",
			"* item 3",
			"Bullets only express level structure and have no semantic meaning or predefined graphical representation.",
		],
	},
	"FREEFORM_TEXT": {
		"semantic_markup_allowed": True,
		"explanation": [
			"The section/subsection body is expected to be freeform text, for example a general description or a note.",
			"As opposed to itemized text, the body is not expected to be structured into separate entries but can be a single freeform block.",
			"Itemization is expressed by bullets and lines, not by decorative spacing, for example:",
			"* item 1",
			"* item 2",
			"+ item 2.1",
			"+ item 2.2",
			"- item 2.2.1",
			"- item 2.2.2",
			"* item 3",
			"Bullets only express level structure and have no semantic meaning or predefined graphical representation.",
		],
	},
}

LABEL_TO_CATEGORY: Final[Dict[str, LabelCategoryInfo_t]] = {
	"Preamble": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Preamble.profile": {"category": "IDENTIFIER", "normativity": "not_applicable"},
	"Preamble.normative_sections": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable"},
	"Preamble.status": {"category": "IDENTIFIER", "normativity": "not_applicable"},
	"Preamble.scope": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable"},
	"Definitions": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Definitions.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative"},
	"Definitions._inherit": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative"},
	"Terminology": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Terminology.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative"},
	"Contract": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Contract.general": {"category": "ITEMIZED_TEXT", "normativity": "normative"},
	"Contract.constructor": {"category": "ITEMIZED_TEXT", "normativity": "normative"},
	"Contract.base": {"category": "QUALIFIED_IDENTIFIER", "normativity": "normative"},
	"Contract.traits": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative"},
	"Contract.invariants": {"category": "ITEMIZED_TEXT", "normativity": "normative"},
	"Contract.requires": {"category": "ITEMIZED_TEXT", "normativity": "normative"},
	"Contract.ensures": {"category": "ITEMIZED_TEXT", "normativity": "normative"},
	"Description": {"category": "FREEFORM_TEXT", "normativity": "can_be_both"},
	"Derived_from": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative"},
	"Factory": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Factory.<item>": {"category": "ITEMIZED_TEXT", "normativity": "normative"},
	"Public_classes": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative"},
	"Public_functions": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative"},
	"Public_methods": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative"},
	"Class_overview": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Class_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative"},
	"Method_overview": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Method_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative"},
	"Function_overview": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Function_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative"},
	"Public_types": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Public_types.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative"},
	"Public_variables": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Public_variables.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative"},
	"Public_constants": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Public_constants.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative"},
	"Parameters": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Parameters.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative"},
	"Returns": {"category": "FREEFORM_TEXT", "normativity": "normative"},
	"Raises": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Raises.<item>": {"category": "ITEMIZED_TEXT", "normativity": "normative"},
	"Notes": {"category": "STRUCTURE", "normativity": "not_applicable"},
	"Notes.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative"},
	"See_also": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "can_be_both"},
}

SECTION_TO_SUBSECTIONS_BY_PROFILE = {
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

# Main section names per profile, derived from the normative section/subsection map.
SECTIONS_BY_PROFILE: Final[Dict[str, List[str]]] = {
	profile: list(section_map.keys())
	for profile, section_map in SECTION_TO_SUBSECTIONS_BY_PROFILE.items()
}

class ExplainSection_t(TypedDict):
	label: str
	title: str
	category: str
	normativity: str
	role_notes: list[str]
	roles: list[str]
	body: list[str]
	template: list[str]
	hint: list[str]
	try_next: list[str]


_COMMON_ROLE_NOTES = [
	"Semantic roles are the named sub-parts used inside a body, for example parameters, return values, notes, or references.",
	"Keep one indentation level per nesting level; structure is expressed by TAB-indented bullets and lines, not by decorative spacing.",
]

_COMMON_HINTS = {
	"Contract": [
		"try waterlint explain-section --label Contract",
		"Contract is the normative core of the docstring section.",
	],
	"Preamble": [
		"try waterlint explain-section --label Preamble",
		"Preamble declares the profile and the normative section set.",
	],
	"Parameters": [
		"try waterlint explain-section --label Parameters",
		"Parameters list formal arguments in a callable docstring.",
	],
	"Returns": [
		"try waterlint explain-section --label Returns",
		"Returns describes the returned value or object.",
	],
	"Raises": [
		"try waterlint explain-section --label Raises",
		"Raises lists documented exceptions and their conditions.",
	],
	"Notes": [
		"try waterlint explain-section --label Notes",
		"Notes stays informative unless the surrounding profile explicitly makes it normative.",
	],
}

_SECTION_CATALOG: dict[str, ExplainSection_t] = {
	"Contract": {
		"label": "Contract",
		"title": "Contract",
		"category": "normative section",
		"normativity": "normative",
		"role_notes": _COMMON_ROLE_NOTES,
		"roles": [
			"general",
			"constructor",
			"requires",
			"ensures",
			"invariants",
		],
		"body": [
			"Contract contains the rules that the section enforces.",
			"It is the place where the validator expects the normative core of the object.",
		],
		"template": [
			"Contract:",
			"\tgeneral:",
			"\t\t...",
			"\tconstructor:",
			"\t\t...",
		],
		"hint": _COMMON_HINTS["Contract"],
		"try_next": [
			"waterlint explain-subsection --label constructor",
		],
	},
	"Preamble": {
		"label": "Preamble",
		"title": "Preamble",
		"category": "profile declaration section",
		"normativity": "normative",
		"role_notes": _COMMON_ROLE_NOTES,
		"roles": [
			"profile",
			"normative_sections",
			"status",
			"scope",
		],
		"body": [
			"Preamble declares which profile the docstring follows and which sections are normative.",
			"It is the entry point for validating the rest of the document.",
		],
		"template": [
			"Preamble:",
			"\tprofile:",
			"\t\tclass",
			"\tnormative_sections:",
			"\t\tContract",
		],
		"hint": _COMMON_HINTS["Preamble"],
		"try_next": [
			"waterlint explain-subsection --label profile",
			"waterlint explain-subsection --label normative_sections",
		],
	},
	"Parameters": {
		"label": "Parameters",
		"title": "Parameters",
		"category": "callable body section",
		"normativity": "normative for callables",
		"role_notes": _COMMON_ROLE_NOTES,
		"roles": [
			"parameter name",
			"parameter description",
		],
		"body": [
			"Parameters documents the callable signature in a structured way.",
			"Each parameter becomes a subsection entry with an explanatory body.",
		],
		"template": [
			"Parameters:",
			"\targs:",
			"\t\t...",
		],
		"hint": _COMMON_HINTS["Parameters"],
		"try_next": [
			"waterlint explain-subsection --label args",
		],
	},
	"Returns": {
		"label": "Returns",
		"title": "Returns",
		"category": "callable body section",
		"normativity": "normative for callables",
		"role_notes": _COMMON_ROLE_NOTES,
		"roles": [
			"return value",
			"return description",
		],
		"body": [
			"Returns documents what the callable yields or returns.",
		],
		"template": [
			"Returns:",
			"\t...",
		],
		"hint": _COMMON_HINTS["Returns"],
		"try_next": [
			"waterlint explain-subsection --label return_value",
		],
	},
	"Raises": {
		"label": "Raises",
		"title": "Raises",
		"category": "callable body section",
		"normativity": "normative for callables",
		"role_notes": _COMMON_ROLE_NOTES,
		"roles": [
			"exception name",
			"exception condition",
		],
		"body": [
			"Raises documents documented exception conditions.",
		],
		"template": [
			"Raises:",
			"\tValueError:",
			"\t\t...",
		],
		"hint": _COMMON_HINTS["Raises"],
		"try_next": [
			"waterlint explain-subsection --label ValueError",
		],
	},
	"Notes": {
		"label": "Notes",
		"title": "Notes",
		"category": "informational section",
		"normativity": "informative by default",
		"role_notes": _COMMON_ROLE_NOTES,
		"roles": [
			"note topic",
			"note body",
		],
		"body": [
			"Notes are used for additional guidance that is not part of the normative contract.",
		],
		"template": [
			"Notes:",
			"\tGeneral note:",
			"\t\t...",
		],
		"hint": _COMMON_HINTS["Notes"],
		"try_next": [
			"waterlint explain-section --label Notes",
		],
	},
}


def get_section_explanation(label: str) -> ExplainSection_t | None:
	return _SECTION_CATALOG.get(label)


def render_explanation_text(spec: ExplainSection_t) -> str:
	lines: list[str] = []
	lines.append(f"Label: {spec['label']}")
	lines.append(f"Title: {spec['title']}")
	lines.append(f"Category: {spec['category']}")
	lines.append(f"Normativity: {spec['normativity']}")
	lines.append("Role notes:")
	for role in spec["role_notes"]:
		lines.append(f"\t- {role}")
	lines.append("Roles:")
	for role in spec["roles"]:
		lines.append(f"\t- {role}")
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
		"label": spec["label"],
		"title": spec["title"],
		"category": spec["category"],
		"normativity": spec["normativity"],
		"role_notes": list(spec["role_notes"]),
		"roles": list(spec["roles"]),
		"body": list(spec["body"]),
		"template": list(spec["template"]),
		"hint": list(spec["hint"]),
		"try": list(spec["try_next"]),
	}
