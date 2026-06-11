#!/usr/bin/env python3
r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions, Public_types, Public_constants
	scope:
		extension
Contract:
	general:
		|Must| provide shared explanation data and renderers for waterlint explain commands.
Public_functions:
	build_section_explanation, build_subsection_explanation, render_explanation_text, render_explanation_json,
	render_subsection_explanation_text, render_subsection_explanation_json
Function_overview:
	build_section_explanation:
		Build a profile-specific section explanation for a label.
	build_subsection_explanation:
		Build a profile-specific subsection explanation for a fully qualified subsection label.
	render_explanation_text:
		Render a section explanation as raw text.
	render_explanation_json:
		Render a section explanation as JSON-ready data.
	render_subsection_explanation_text:
		Render a subsection explanation as raw text.
	render_subsection_explanation_json:
		Render a subsection explanation as JSON-ready data.
Public_types:
	SectionBodyCategory_t:
		|Must| be a literal type describing the structural form of a section body,\
		for example whether it is freeform text or a list of identifiers.
	LabelKind_t:
		|Must| be a literal type describing the kind of section label, for example whether it is fixed or an identifier.
		Informative: This is relevant for subsections with variable labels, for which the label kind determines the rules for the label text.
	Profile_t:
		|Must| be a literal type describing the documentation profile for which a section is relevant, for example "module" or "class".
	Normativity_t:
		|Must| be a literal type describing the normativity status of a section, for example "normative" or "informative".
		Any normative section or subsection |must| be mentioned in |label|`Preamble.normative_sections` to be considered normative.
	MustExist_t:
		|Must| be a literal type describing whether a section or subsection is required to exist in a document of the relevant profile.
Public_constants:
	SECTION_PROPERTIES:
		|Must| be a mapping from section and subsection labels to their properties relevant for explanation and validation,\
		for example body category, normativity, and profile applicability.
		Informative: This is a carefully distilled machine-readable representation of the relevant rules\
		from the documentation standard, but the documentation remains the Single Source of Truth for the standard.
"""

from __future__ import annotations

from typing import Any, Final, cast, Dict, List, Literal, TypedDict

import sdv.doc.waterloo.docitem as docitem
from sdv.doc.waterloo import waterlint_common as wl_common

from sdv.doc.waterloo.docitem_helper import SECTION_PROPERTIES as DOCITEM_SECTION_PROPERTIES
from sdv.doc.waterloo.docitem_helper import WTRL_MARKUP_ROLES

# These two type-like axes describe structural form: what kind of label, body, or render shape is involved.
# Source of Truth for all Section/Subsection properties is the informative section "Section property overview"
# in the documentation standard, which in turn is derived from the normative ruleset.

SectionBodyCategory_t = Literal[
	"STRUCTURE",
	"IDENTIFIER",
	"QUALIFIED_IDENTIFIER",
	"LIST_OF_IDENTIFIERS",
	"LIST_OF_QUALIFIED_IDENTIFIERS",
	"ITEMIZED_TEXT",
	"FREEFORM_TEXT",
]

LabelKind_t = Literal["FIXED", "IDENTIFIER", "QUALIFIED_IDENTIFIER", "LIST_OF_IDENTIFIERS", "ANY_STRING"]

# These axes describe semantic status and applicability in the documentation rules.

Profile_t = Literal["module", "class", "function", "method", "inherited_method"]
Normativity_t = Literal["not_applicable", "normative", "informative", "can_be_both"]
MustExist_t = Literal["yes", "no", "depends_on_context"]

class SectionBodyCategoryExplanation_t(TypedDict):
	markup_allowed: bool
	renders_outer_bullets: bool
	inner_lists_allowed: bool
	reason: str
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


class BodyExplain_t(TypedDict):
	category: SectionBodyCategory_t
	explanation: list[str]
	content: list[str]


class ExplainSection_t(TypedDict):
	profile: Profile_t
	label: str
	title: str
	body: BodyExplain_t
	normativity: Normativity_t
	label_kind: LabelKind_t
	must_exist: MustExist_t
	available_profiles: list[Profile_t]
	subsections: list[SubsectionExplainInfo_t]
	template: list[str]
	hint: list[str]
	try_self: str
	try_next: list[str]
	itemization: ItemizationExplain_t
	markup: FeatureExplain_t


class ExplainSubsection_t(TypedDict):
	profile: Profile_t
	section_label: str
	subsection_label: str
	label: str
	title: str
	section_title: str
	body: BodyExplain_t
	normativity: Normativity_t
	label_kind: LabelKind_t
	must_exist: MustExist_t
	available_profiles: list[Profile_t]
	template: list[str]
	hint: list[str]
	try_self: str
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
		"\t|",
		],
}

ExplainSectionBodyCategory: Final[Dict[SectionBodyCategory_t, SectionBodyCategoryExplanation_t]] = {
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
			"A line containing only `|` and optional whitespace denotes a paragraph boundary in the rendered output.",
			"As opposed to itemized text, the main body is not split into outer list items by the renderer.",
		],
	}
}


_PROFILE_ORDER: Final[list[Profile_t]] = ["module", "class", "function", "method", "inherited_method"]

SECTION_PROPERTIES: Final[Dict[str, SectionPropertyInfo_t]] = cast(Dict[str, SectionPropertyInfo_t], DOCITEM_SECTION_PROPERTIES)

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
		"module": ["<item>"],
		"class": ["<item>"]
	},
	"Public_functions": {
		"module": [],
	},
	"Function_overview": {
		"module": ["<item>"],
	},
	"Public_types": {
		"module": ["<item>"],
		"class": ["<item>"]
	},
	"Public_variables": {
		"module": ["<item>"],
		"class": ["<item>"]
	},
	"Public_constants": {
		"module": ["<item>"],
		"class": ["<item>"]
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
		"function": ["<item>"],
		"method": ["<item>"]
	},
	"Returns": {
		"function": [],
		"method": []
	},
	"Raises": {
		"function": ["<item>"],
		"method": ["<item>"]
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
			"Returns describes the returned value or object and its expected meaning.",
		],
		"try_next": ["waterlint explain-subsection --label return_value"],
	},
	"Raises": {
		"title": "Raises",
		"body": [
			"Raises documents documented exception conditions.",
			"Each subsection header names an exception type, and the subsection body explains the condition under which it is raised.",
			"If the callable is not supposed to raise any exceptions, the section still must be present, but left empty.",			
		],
		"hint": [
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
			"Factory is the creation-oriented companion to the class contract.",
		],
		"try_next": ["waterlint explain-subsection --label <item>"],
	},
}

_BASE_SUBSECTION_SPECS: Dict[str, Dict[str, Any]] = {
	"Preamble.profile": {
		"title": "Preamble.profile",
		"body": [
			"Preamble.profile names the documentation profile token for the current document.",
			"It must be one of the fixed profile identifiers such as module or class.",
		],
		"hint": [
			"Preamble.profile identifies which profile governs the rest of the docstring.",
		],
	},
	"Preamble.normative_sections": {
		"title": "Preamble.normative_sections",
		"body": [
			"Preamble.normative_sections lists the section labels that are normative in this document.",
			"It is a CSV list of fixed section labels.",
		],
		"hint": [
			"Preamble.normative_sections tells the validator which sections are normative.",
		],
	},
	"Preamble.status": {
		"title": "Preamble.status",
		"body": [
			"Preamble.status names the lifecycle status token for function or method profiles.",
			"It is only used when the surrounding profile requires a status marker.",
		],
		"hint": [
			"Preamble.status captures the status marker for callable docstrings.",
		],
	},
	"Preamble.scope": {
		"title": "Preamble.scope",
		"body": [
			"Preamble.scope lists the scope tags that constrain the visible object set.",
			"It is a CSV list of identifiers.",
		],
		"hint": [
			"Preamble.scope records the visible scope tags for the documented object.",
		],
	},
	"Definitions.<item>": {
		"title": "Definitions.<item>",
		"body": [
			"Each Definitions item introduces one normative term and its spelling variants.",
			"The subsection label itself is a CSV list of identifiers, with the first item naming the canonical term.",
		],
		"hint": [
			"Definitions.<item> explains one glossary entry and its variants.",
		],
	},
	"Definitions._inherit": {
		"title": "Definitions._inherit",
		"body": [
			"Definitions._inherit lists definition terms inherited from the surrounding scope.",
			"It is used when a child scope reuses the glossary of its parent scope.",
		],
		"hint": [
			"Definitions._inherit records inherited glossary terms.",
		],
	},
	"Terminology.<item>": {
		"title": "Terminology.<item>",
		"body": [
			"Terminology items give informative background for one term.",
			"They do not add new normative requirements.",
		],
		"hint": [
			"Terminology.<item> gives an informative term explanation.",
		],
	},
	"Notes.<item>": {
		"title": "Notes.<item>",
		"body": [
			"Notes items provide extra guidance, caveats, examples, or implementation notes.",
			"They stay informative unless the surrounding profile explicitly says otherwise.",
		],
		"hint": [
			"Notes.<item> captures a reader-oriented note or example.",
		],
	},
	"Contract.general": {
		"title": "Contract.general",
		"body": [
			"Contract.general describes the general normative contract for the documented object.",
			"It is the executable core of the contract section for the current profile.",
		],
		"hint": [
			"Contract.general is the general normative contract block.",
		],
	},
	"Contract.constructor": {
		"title": "Contract.constructor",
		"body": [
			"Contract.constructor describes the constructor contract for a class.",
			"It captures the normative creation behavior of the class constructor.",
		],
		"hint": [
			"Contract.constructor describes the constructor contract of the class.",
		],
	},
	"Contract.traits": {
		"title": "Contract.traits",
		"body": [
			"Contract.traits lists the traits, mixins, or related traits of the class.",
			"It is a flat list of identifiers.",
		],
		"hint": [
			"Contract.traits names the class traits or mixins.",
		],
	},
	"Contract.invariants": {
		"title": "Contract.invariants",
		"body": [
			"Contract.invariants lists invariants that must hold for the callable or class.",
			"Each logical item states one invariant clause.",
		],
		"hint": [
			"Contract.invariants lists invariant clauses for the object.",
		],
	},
	"Contract.requires": {
		"title": "Contract.requires",
		"body": [
			"Contract.requires lists the preconditions that must hold before the callable runs.",
			"Each logical item states one requirement.",
		],
		"hint": [
			"Contract.requires lists the preconditions of the callable.",
		],
	},
	"Contract.ensures": {
		"title": "Contract.ensures",
		"body": [
			"Contract.ensures lists the postconditions that hold after the callable returns.",
			"Each logical item states one guaranteed outcome.",
		],
		"hint": [
			"Contract.ensures lists the postconditions of the callable.",
		],
	},
	"Contract.base": {
		"title": "Contract.base",
		"body": [
			"Contract.base names the base object for an inherited method.",
			"It is a single qualified identifier.",
		],
		"hint": [
			"Contract.base names the inherited base object.",
		],
	},
	"Factory.<item>": {
		"title": "Factory.<item>",
		"body": [
			"Factory items name creation or retrieval entry points for the class.",
			"They are qualified identifiers that refer to the concrete factory-like callable or method.",
		],
		"hint": [
			"Factory.<item> names one factory-like entry point.",
		],
	},
	"Public_types.<item>": {
		"title": "Public_types.<item>",
		"body": [
			"Public_types items name one public type declaration or type alias.",
			"They are visible type-level declarations exported by the current scope.",
		],
		"hint": [
			"Public_types.<item> names one public type or alias.",
		],
	},
	"Public_variables.<item>": {
		"title": "Public_variables.<item>",
		"body": [
			"Public_variables items name one public variable exported by the current scope.",
			"They are identifiers that are part of the public API surface.",
		],
		"hint": [
			"Public_variables.<item> names one public variable.",
		],
	},
	"Public_constants.<item>": {
		"title": "Public_constants.<item>",
		"body": [
			"Public_constants items name one public constant exported by the current scope.",
			"They are identifiers that are part of the public API surface.",
		],
		"hint": [
			"Public_constants.<item> names one public constant.",
		],
	},
	"Class_overview.<item>": {
		"title": "Class_overview.<item>",
		"body": [
			"Class_overview items provide a short prose summary for one public class.",
			"They are reader-oriented narrative entries, not normative declarations.",
		],
		"hint": [
			"Class_overview.<item> summarizes one public class.",
		],
	},
	"Method_overview.<item>": {
		"title": "Method_overview.<item>",
		"body": [
			"Method_overview items provide a short prose summary for one public method.",
			"They are reader-oriented narrative entries, not normative declarations.",
		],
		"hint": [
			"Method_overview.<item> summarizes one public method.",
		],
	},
	"Function_overview.<item>": {
		"title": "Function_overview.<item>",
		"body": [
			"Function_overview items provide a short prose summary for one public function.",
			"They are reader-oriented narrative entries, not normative declarations.",
		],
		"hint": [
			"Function_overview.<item> summarizes one public function.",
		],
	},
	"Parameters.<item>": {
		"title": "Parameters.<item>",
		"body": [
			"Parameters items name one formal parameter and explain its role.",
			"They describe how the callable uses the parameter and what value shape is expected.",
		],
		"hint": [
			"Parameters.<item> explains one formal parameter.",
		],
	},
	"Raises.<item>": {
		"title": "Raises.<item>",
		"body": [
			"Raises items name one exception type and explain when it is raised.",
			"They document one exception condition at a time.",
		],
		"hint": [
			"Raises.<item> explains one exception type.",
		],
	},
}


def _available_profiles_for_label(label: str) -> list[Profile_t]:
	profile_map = SECTION_SUBSECTIONS.get(label, {})
	return [profile for profile in _PROFILE_ORDER if profile in profile_map]


def _available_profiles_for_subsection_label(label: str) -> list[Profile_t]:
	sub_info = SECTION_PROPERTIES.get(label)
	if sub_info is None:
		return []
	profiles = sub_info.get("profile")
	if profiles is None:
		return []
	return [profile for profile in _PROFILE_ORDER if profile in profiles]


def _build_template_lines(label: str, body_category: SectionBodyCategory_t, allowed_subsections: list[str]) -> list[str]:
	if body_category == "STRUCTURE":
		template = [EXPLAIN_TEMPLATES["STRUCTURE"][0].format(label=label)]
		for subsection in allowed_subsections:
			template.append(EXPLAIN_TEMPLATES["STRUCTURE"][1].format(subsection=subsection))
			template.append(EXPLAIN_TEMPLATES["STRUCTURE"][2])
		return template
	return [line.format(label=label) for line in EXPLAIN_TEMPLATES[body_category]]


def _render_explain_text(spec: dict[str, Any], include_section_context: bool = False) -> str:
	lines: list[str] = []
	lines.append(f"Label: {spec['label']}")
	lines.append(f"Profile: {spec['profile']}")
	if include_section_context:
		lines.append(f"Section: {spec['section_label']}")
		lines.append(f"Subsection: {spec['subsection_label']}")
	lines.append(f"Title: {spec['title']}")
	lines.append(f"Body category: {spec['body']['category']}")
	lines.append("Body explanation:")
	for line in spec["body"]["explanation"]:
		lines.append(f"  {line}")
	lines.append("Body content:")
	for line in spec["body"]["content"]:
		lines.append(f"  {line}")
	lines.append(f"Normativity: {spec['normativity']}")
	lines.append(f"Label kind: {spec['label_kind']}")
	lines.append(f"Must exist: {spec['must_exist']}")
	lines.append(f"Available profiles: {', '.join(spec['available_profiles']) if spec['available_profiles'] else 'none'}")
	lines.append("Template:")
	for line in spec["template"]:
		lines.append(f"  {line}")
	hint = spec.get("hint", [])
	if hint:
		lines.append("Hint:")
		for line in hint:
			lines.append(f"  {line}")
	lines.append(f"Try self: {spec['try_self']}")
	try_next = spec.get("try_next", [])
	if try_next:
		lines.append("Try next:")
		for line in try_next:
			lines.append(f"  {line}")
	itemization = spec["itemization"]
	lines.append("Itemization:")
	lines.append(f"  allowed: {itemization['allowed']}")
	lines.append(f"  renders_outer_bullets: {itemization['renders_outer_bullets']}")
	lines.append(f"  inner_lists_allowed: {itemization['inner_lists_allowed']}")
	lines.append(f"  reason: {itemization['reason']}")
	if "explanation" in itemization:
		lines.append("  explanation:")
		for line in itemization["explanation"]:
			lines.append(f"    {line}")
	markup = spec["markup"]
	lines.append("Markup:")
	lines.append(f"  allowed: {markup['allowed']}")
	lines.append(f"  reason: {markup['reason']}")
	if "explanation" in markup:
		lines.append("  explanation:")
		for line in markup["explanation"]:
			lines.append(f"    {line}")
	return "\n".join(lines) + "\n"


def _section_or_subsection_feature(category: SectionBodyCategory_t) -> tuple[ItemizationExplain_t, FeatureExplain_t]:
	feature_category = ExplainSectionBodyCategory[category]
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
	return itemization, markup


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
		# Existence is ensured by the construction of the mapping, so we can
		# directly access it without checking for existence and mypy is chilled.
		sub_info = SECTION_PROPERTIES[sub_label]
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
	try_self = f"waterlint explain-section --label {label} --profile PROFILE"

	itemization, markup = _section_or_subsection_feature(cat_info["category"])

	explanation: ExplainSection_t = {
		"profile": profile,
		"label": label,
		"title": base["title"],
		"body": {
			"category": cat_info["category"],
			"explanation": list(ExplainSectionBodyCategory[cat_info["category"]]["explanation"]),
			"content": list(base["body"]),
		},
		"normativity": cat_info["normativity"],
		"label_kind": cat_info["label_kind"],
		"must_exist": cat_info["must_exist"],
		"available_profiles": _available_profiles_for_label(label),
		"subsections": subsections,
		"template": template,
		"hint": hint,
		"try_self": try_self,
		"try_next": list(base["try_next"]),
		"itemization": itemization,
		"markup": markup,
	}
	return explanation


def build_subsection_explanation(label: str, profile: Profile_t) -> ExplainSubsection_t | None:
	if "." not in label:
		return None
	sub_info = SECTION_PROPERTIES.get(label)
	if sub_info is None or profile not in (sub_info["profile"] or []):
		return None
	section_label, subsection_label = label.split(".", 1)
	section_info = SECTION_PROPERTIES.get(section_label)
	if section_info is None:
		return None
	base = _BASE_SUBSECTION_SPECS.get(label)
	if base is None:
		return None
	itemization, markup = _section_or_subsection_feature(sub_info["category"])
	template = [line.format(label=label) for line in EXPLAIN_TEMPLATES[sub_info["category"]]]
	hint = [f"Profile: {profile}"]
	hint.extend(base["hint"])
	hint.append(f"Parent section: {section_label}")
	hint.append(f"Subsection: {subsection_label}")
	try_self = f"waterlint explain-subsection --label {label} --profile PROFILE"
	try_next = [f"waterlint explain-section --label {section_label} --profile PROFILE"]
	return {
		"profile": profile,
		"section_label": section_label,
		"subsection_label": subsection_label,
		"label": label,
		"title": base["title"],
		"section_title": _BASE_SECTION_SPECS.get(section_label, {"title": section_label})["title"],
		"body": {
			"category": sub_info["category"],
			"explanation": list(ExplainSectionBodyCategory[sub_info["category"]]["explanation"]),
			"content": list(base["body"]),
		},
		"normativity": sub_info["normativity"],
		"label_kind": sub_info["label_kind"],
		"must_exist": sub_info["must_exist"],
		"available_profiles": _available_profiles_for_subsection_label(label),
		"template": template,
		"hint": hint,
		"try_self": try_self,
		"try_next": try_next,
		"itemization": itemization,
		"markup": markup,
	}


def render_explanation_text(spec: ExplainSection_t) -> str:
	return _render_explain_text(cast(dict[str, Any], spec), include_section_context=False)


def render_explanation_json(spec: ExplainSection_t) -> dict[str, Any]:
	return {
		"kind": "section_explanation",
		"profile": spec["profile"],
		"label": spec["label"],
		"title": spec["title"],
		"normativity": spec["normativity"],
		"label_kind": spec["label_kind"],
		"must_exist": spec["must_exist"],
		"available_profiles": list(spec["available_profiles"]),
		"subsections": list(spec["subsections"]),
		"body": {
			"category": spec["body"]["category"],
			"explanation": list(spec["body"]["explanation"]),
			"content": list(spec["body"]["content"]),
		},
		"template": list(spec["template"]),
		"hint": list(spec["hint"]),
		"try_self": spec["try_self"],
		"try_next": list(spec["try_next"]),
		"itemization": dict(spec["itemization"]),
		"markup": dict(spec["markup"]),
	}


def render_subsection_explanation_text(spec: ExplainSubsection_t) -> str:
	return _render_explain_text(cast(dict[str, Any], spec), include_section_context=True)


def render_subsection_explanation_json(spec: ExplainSubsection_t) -> dict[str, Any]:
	return {
		"kind": "subsection_explanation",
		"profile": spec["profile"],
		"section_label": spec["section_label"],
		"subsection_label": spec["subsection_label"],
		"label": spec["label"],
		"title": spec["title"],
		"section_title": spec["section_title"],
		"normativity": spec["normativity"],
		"label_kind": spec["label_kind"],
		"must_exist": spec["must_exist"],
		"available_profiles": list(spec["available_profiles"]),
		"body": {
			"category": spec["body"]["category"],
			"explanation": list(spec["body"]["explanation"]),
			"content": list(spec["body"]["content"]),
		},
		"template": list(spec["template"]),
		"hint": list(spec["hint"]),
		"try_self": spec["try_self"],
		"try_next": list(spec["try_next"]),
		"itemization": dict(spec["itemization"]),
		"markup": dict(spec["markup"]),
	}


def _build_explain_tracer_json_doc(tr: Any, include_debug: bool = False) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=wl_common.WTRL_DOCITEM_VERSION,
		id_prefix="urn:waterlint:wtrl-tracer-json:explain",
		include_debug=include_debug,
	)


def _emit_explain_tracer(
	tr: Any,
	out_path: str | None,
	out_json_path: str | None,
	debug: bool = False,
) -> None:
	if not (tr.has_errors() or out_path or out_json_path):
		return
	wl_common.emit_tracer(
		tr,
		out_path,
		out_json_path,
		debug=debug,
		callback_build_json_doc=lambda tr_: _build_explain_tracer_json_doc(tr_, include_debug=debug),
	)
