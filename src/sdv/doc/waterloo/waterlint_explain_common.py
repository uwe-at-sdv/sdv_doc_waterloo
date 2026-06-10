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

LabelKind_t = Literal["IDENTIFIER", "QUALIFIED_IDENTIFIER", "ANY_STRING", "NOT_APPLICABLE"]


class SectionBodyCategoryExplanation_t(TypedDict):
	semantic_markup_allowed: bool
	explanation: list[str]


class LabelCategoryInfo_t(TypedDict):
	category: SectionBodyCategory_t
	normativity: Normativity_t
	label_kind: LabelKind_t
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

LABEL_TO_CATEGORY: Final[Dict[str, LabelCategoryInfo_t]] = {
	"Preamble": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Preamble.profile": {"category": "IDENTIFIER", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Preamble.normative_sections": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Preamble.status": {"category": "IDENTIFIER", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Preamble.scope": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Definitions": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Definitions.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "hint": ""},
	"Definitions._inherit": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Terminology": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Terminology.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "ANY_STRING", "hint": ""},
	"Contract": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Contract.general": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Contract.constructor": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Contract.base": {"category": "QUALIFIED_IDENTIFIER", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Contract.traits": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Contract.invariants": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Contract.requires": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Contract.ensures": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Description": {"category": "FREEFORM_TEXT", "normativity": "can_be_both", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Derived_from": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Factory": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Factory.<item>": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "QUALIFIED_IDENTIFIER", "hint": ""},
	"Public_classes": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Public_functions": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Public_methods": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Class_overview": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Class_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "hint": ""},
	"Method_overview": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Method_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "hint": ""},
	"Function_overview": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Function_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "hint": ""},
	"Public_types": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Public_types.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "hint": ""},
	"Public_variables": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Public_variables.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "hint": ""},
	"Public_constants": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Public_constants.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "hint": ""},
	"Parameters": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Parameters.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "hint": ""},
	"Returns": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Raises": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Raises.<item>": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "QUALIFIED_IDENTIFIER", "hint": ""},
	"Notes": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "NOT_APPLICABLE", "hint": ""},
	"Notes.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "ANY_STRING", "hint": ""},
	"See_also": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "can_be_both", "label_kind": "NOT_APPLICABLE", "hint": ""},
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
		"body_category": "STRUCTURE",
		"normativity": "normative",
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
		"body_category": "STRUCTURE",
		"normativity": "normative",
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
		"body_category": "STRUCTURE",
		"normativity": "normative for callables",
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
		"body_category": "FREEFORM_TEXT",
		"normativity": "normative for callables",
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
		"body_category": "STRUCTURE",
		"normativity": "normative for callables",
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
		"body_category": "STRUCTURE",
		"normativity": "informative by default",
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
	cat_info = LABEL_TO_CATEGORY.get(label, {"category": "STRUCTURE", "normativity": "informative", "label_kind": "NOT_APPLICABLE", "hint": ""})
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
		"normativity": base["normativity"],
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
