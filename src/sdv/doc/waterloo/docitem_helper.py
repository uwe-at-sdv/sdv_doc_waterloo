"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_constants, Public_classes, Public_functions, Public_types
Contract:
	general:
		|Must| provide shared helper functions, constants, and type aliases for Waterloo docstring validation and explanation.
Public_classes:
	Trait, Scope, Flavour, Format, Status, ConfigTraversal, tracer, ResolveObjectError
Public_functions:
	explain_try_self_for_section, explain_try_self_for_subsection,
	render_source_snippet, render_expected_snippet, render_allowed_identifier, render_expected_identifier, render_suggestion,
	render_allowed_identifiers, render_identifier_lines, render_deduplicated_identifiers, render_unique_identifiers,
	render_normativity_keyword_details, render_exception_reference_details, render_parameter_signature_details,
	render_overview_requires_section_details, render_profile_mismatch_details, render_name_object_consistency_details,
	render_listed_object_missing_details,
	render_base_method_docstring_details, render_base_method_reference_details, render_scope_relation_details,
	render_normative_section_details, render_missing_entry_details, render_exactly_one_identifier_details,
	render_definition_reference_details, render_inherited_definition_details, render_type_reference_details,
	render_constant_reference_details, render_named_value_reference_details, render_overview_missing_member_details,
	get_source_docstring, is_annotatable, is_attr_annotated, is_attr_final, is_list_of_str,
	is_obj_module, is_obj_class, is_obj_function, is_obj_method_like, is_obj_named_value,
	is_obj_documentable, get_obj_direct_module, get_obj_name, get_obj_fully_qualified_name,
	get_obj_path, build_anchor, get_func_obj_from_callable, get_obj_docstring, get_obj_annotations,
	get_obj_decorators, gen_documentable_objects, traced_section, rule_on_fail, raise_has_no_docstring,
	raise_parsing_error, raise_parsing_error_expected_but_got, raise_parsing_error_invalid_label,
	raise_validation_error, raise_validation_error_expected_but_got, warn_parsing, warn_validation
Public_types:
	Profile:
		Supported profile labels for the helper layer.
	DocstringSubtree:
		Recursive docstring tree node type.
	DocstringTree:
		A full docstring tree represented as a list of subtree values.
	AnnotatableObject:
		Objects that can be annotated by the helper layer.
	RuleId:
		Rule identifier type alias.
	Origin:
		Tracer origin labels.
	Details:
		Tracer details payload.
	Scopes:
		A set of scope values.
	Documentable:
		Objects that can be traversed by the helper functions.
	AstDocNode:
		An AST node type relevant for docstring extraction.
Public_constants:
	RE_RULE_ID:
		Regular expression for rule IDs. Undocumented: RE_RULE_ID_COMPILED, the precompiled version for performance.
	RE_IDENTIFIER:
		Regular expression for identifiers. Undocumented: RE_IDENTIFIER_COMPILED, the precompiled version for performance.
	RE_QUALIFIED_IDENTIFIER:
		Regular expression for qualified identifiers. Undocumented: RE_QUALIFIED_IDENTIFIER_COMPILED, the precompiled version for performance.
	RE_CSV_IDENTIFIERS:
		Regular expression for comma-separated identifiers. Undocumented: RE_CSV_IDENTIFIERS_COMPILED, the precompiled version for performance.
	WTRL_MARKUP_ROLES:
		Regular expression for Waterloo markup roles in backtick markup.
	RE_WTRL_MARKUP_BACKTICK:
		Regular expression for matching Waterloo backtick markup with roles. Undocumented: RE_WTRL_MARKUP_BACKTICK_COMPILED, the precompiled version for performance.
	RE_WTRL_ANGLE_HTTPS_REF:
		Regular expression for matching Waterloo angle bracket HTTPS references. Undocumented: RE_WTRL_ANGLE_HTTPS_REF_COMPILED, the precompiled version for performance.
		References consist of two parts: clear text and <link>, optionally separated by whitespace.
	RE_WTRL_ANGLE_WTRL_REF:
		Regular expression for matching Waterloo angle bracket wtrl references. Undocumented: RE_WTRL_ANGLE_WTRL_REF_COMPILED, the precompiled version for performance.
		References consist of two parts: clear text and <link>, optionally separated by whitespace.
	RULE_ID_WHITELIST:
		Whitelist reasons for legacy rule identifiers used by the helper layer.
	CANONICAL_ORDER_OF_SECTIONS:
		Canonical subsection ordering for section snippets and expected snippets.
	CANONICAL_ORDER_OF_PROFILES:
		Canonical profile ordering for CLI help and documentation.
	TRAIT_TAG_MAP:
		Trait tag mapping for trait labels.
	SCOPE_TAG_MAP:
		Scope tag mapping for visibility selection.
	FLAVOUR_TAG_MAP:
		Flavour tag mapping for normativity keyword rendering.
	FORMAT_TAG_MAP:
		Output format tag mapping for string-related output.
	STATUS_TAG_MAP:
		Status tag mapping for Preamble.status.
	SECTION_PROPERTIES:
		|Must| be a mapping from section and subsection labels to their properties relevant for explanation and validation,
		for example body category, normativity, and profile applicability.
		Informative: This is a carefully distilled machine-readable representation of the relevant rules
		from the documentation standard, but the documentation remains the Single Source of Truth for the standard.
Notes:
	Render functions:
		The render functions in this module are intended for building
		verbose diagnostic messages that include source and expected snippets
		along with suggestions on how to fix the docstring. 
"""
from __future__ import annotations
from enum import Enum,IntEnum
from types import FunctionType, MappingProxyType, ModuleType
from typing_extensions import Self, TypeIs
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, Literal, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypedDict, TypeGuard, Union, cast

import sys,re,os,copy
import pkgutil,inspect,importlib
import ast
import textwrap
import builtins
from datetime import datetime
from weakref import WeakKeyDictionary
from contextlib import contextmanager

try:
	from enum import StrEnum # type: ignore[attr-defined]
except:
	class StrEnum(str, Enum): # type: ignore[no-redef]
		pass

#===== Rule-ID Whitelist ======================================#
# Valid whitelist reasons in tokenized form:
class WHITELIST_REASON(IntEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
	Contract:
		general:
			|Must| enumerate the legacy rule-whitelist reasons used by this helper layer.
	Public_constants:
		UNSPECIFIED_RULE:
			No explicit reason was recorded.
		MAY_EXIST_RULE:
			The rule may exist in the corpus.
		STRUCTURE_RULE:
			The rule is a structural rule.
		SEMANTIC_RULE:
			The rule is a semantic rule.
		UNRELATED_RULE:
			The rule is unrelated to the current module.
		ANTICIPATED_RULE:
			The rule is expected to appear later.
		FALLBACK_RULE:
			The rule acts as a fallback.
		RELAY_RULE:
			The rule is relayed to another rule.
		BAD_IMPLEMENTATION_RULE:
			The rule is a placeholder for a bad implementation case.
		EXISTS_AS_COMMENT_RULE:
			The rule exists only as a comment-level trace.
	"""
# should be avoided:
	UNSPECIFIED_RULE	= 0
# will definitely appear:
	MAY_EXIST_RULE		= 1
	STRUCTURE_RULE		= 2
	SEMANTIC_RULE		= 3
	UNRELATED_RULE		= 4
	ANTICIPATED_RULE	= 5
	FALLBACK_RULE		= 6
	RELAY_RULE		= 7
	BAD_IMPLEMENTATION_RULE	= 8
	EXISTS_AS_COMMENT_RULE	= 9
# - structure-rule
# Rules:
RULE_ID_WHITELIST: Final[Dict[str, WHITELIST_REASON]] = {
	"DOC-002":	WHITELIST_REASON.STRUCTURE_RULE,
	"META-000":	WHITELIST_REASON.UNRELATED_RULE,
	"META-001":	WHITELIST_REASON.UNRELATED_RULE,
	"META-002":	WHITELIST_REASON.UNRELATED_RULE,
	"META-003":	WHITELIST_REASON.UNRELATED_RULE,
	"META-004":	WHITELIST_REASON.UNRELATED_RULE,
	"CCLO-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CCLO-004":	WHITELIST_REASON.STRUCTURE_RULE,
	"CCLO-010":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CMTO-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CMTO-004":	WHITELIST_REASON.STRUCTURE_RULE,
	"CMTO-010":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CON-003":	WHITELIST_REASON.SEMANTIC_RULE,
	"CON-012":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CON-021":	WHITELIST_REASON.SEMANTIC_RULE,
	"CON-025":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CON-037":	WHITELIST_REASON.SEMANTIC_RULE,
	"CON-038":	WHITELIST_REASON.SEMANTIC_RULE,
	"CON-047":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CON-049":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CON-051":	WHITELIST_REASON.UNRELATED_RULE,
	"CON-052":	WHITELIST_REASON.UNRELATED_RULE,
	"CON-053":	WHITELIST_REASON.STRUCTURE_RULE,
	"CPCL-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPCL-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"CPCL-008":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPCON-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPCON-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"CPMT-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPMT-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"CPMT-008":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPTYP-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPTYP-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"CPVAR-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPVAR-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"DEF-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"DEF-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"DEF-005":	WHITELIST_REASON.SEMANTIC_RULE,
	"DEF-012":	WHITELIST_REASON.MAY_EXIST_RULE,
	"DEF-016":	WHITELIST_REASON.STRUCTURE_RULE,
	"DEF-019":	WHITELIST_REASON.RELAY_RULE,		# relay to VLII-001
	"DEF-020":	WHITELIST_REASON.MAY_EXIST_RULE,
	"DER-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"DER-002":	WHITELIST_REASON.SEMANTIC_RULE,
	"DER-009":	WHITELIST_REASON.STRUCTURE_RULE,
	"DESC-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"DESC-002":	WHITELIST_REASON.MAY_EXIST_RULE,
	"FAC-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"FAC-004":	WHITELIST_REASON.STRUCTURE_RULE,
	"MCLO-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MCLO-004":	WHITELIST_REASON.STRUCTURE_RULE,
	"MCLO-010":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MFNO-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MFNO-004":	WHITELIST_REASON.STRUCTURE_RULE,
	"MFNO-010":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPCL-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPCL-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"MPCL-008":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPCON-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPCON-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"MPFN-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPFN-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"MPFN-008":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPTYP-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPTYP-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"MPVAR-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"MPVAR-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"NOTE-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"NOTE-004":	WHITELIST_REASON.SEMANTIC_RULE,
	"NOTE-005":	WHITELIST_REASON.STRUCTURE_RULE,
	"NOTE-008":	WHITELIST_REASON.MAY_EXIST_RULE,
	"PAR-003":	WHITELIST_REASON.SEMANTIC_RULE,
	"PAR-008":	WHITELIST_REASON.STRUCTURE_RULE,
	"PNB-001":	WHITELIST_REASON.SEMANTIC_RULE,
	"PRE-021":	WHITELIST_REASON.STRUCTURE_RULE,
	"RAI-003":	WHITELIST_REASON.SEMANTIC_RULE,
	"RAI-006":	WHITELIST_REASON.SEMANTIC_RULE,
	"RAI-011":	WHITELIST_REASON.STRUCTURE_RULE,
	"PRSR-001":	WHITELIST_REASON.SEMANTIC_RULE,
	"RET-003":	WHITELIST_REASON.SEMANTIC_RULE,
	"SCP-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"SCP-002":	WHITELIST_REASON.STRUCTURE_RULE,
	"SCP-004":	WHITELIST_REASON.STRUCTURE_RULE,
	"SCP-010":	WHITELIST_REASON.FALLBACK_RULE,
	"SEE-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"SEE-010":	WHITELIST_REASON.EXISTS_AS_COMMENT_RULE,
	"SEE-011":	WHITELIST_REASON.MAY_EXIST_RULE,
	"STA-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"STA-005":	WHITELIST_REASON.EXISTS_AS_COMMENT_RULE,
	"TERM-001":	WHITELIST_REASON.MAY_EXIST_RULE,
	"TERM-004":	WHITELIST_REASON.STRUCTURE_RULE,
	"TERM-006":	WHITELIST_REASON.SEMANTIC_RULE,
	"TERM-009":	WHITELIST_REASON.MAY_EXIST_RULE,
	"CPVAR-009":	WHITELIST_REASON.SEMANTIC_RULE,
	"DEF-010":	WHITELIST_REASON.STRUCTURE_RULE,
	"LQID-003":	WHITELIST_REASON.STRUCTURE_RULE,
	"LQID-006":	WHITELIST_REASON.STRUCTURE_RULE,
	"LQID-005":	WHITELIST_REASON.STRUCTURE_RULE,
	"MPVAR-009":	WHITELIST_REASON.SEMANTIC_RULE,
	"RET-008":	WHITELIST_REASON.SEMANTIC_RULE,
	"RET-009":	WHITELIST_REASON.SEMANTIC_RULE,
	"RET-010":	WHITELIST_REASON.SEMANTIC_RULE,
	"TKN-007":	WHITELIST_REASON.STRUCTURE_RULE,
	"JSCH-000":	WHITELIST_REASON.UNRELATED_RULE,
	"JSCH-002":	WHITELIST_REASON.UNRELATED_RULE,
	"JSCH-003":	WHITELIST_REASON.UNRELATED_RULE,
	"JSCH-004":	WHITELIST_REASON.UNRELATED_RULE,
	"JSCH-005":	WHITELIST_REASON.UNRELATED_RULE,
	"JSCH-700":	WHITELIST_REASON.UNRELATED_RULE,
	"JSCH-800":	WHITELIST_REASON.UNRELATED_RULE,
	"TKN-005":	WHITELIST_REASON.UNRELATED_RULE,
	"TKN-006":	WHITELIST_REASON.UNRELATED_RULE,
	"TKN-008":	WHITELIST_REASON.UNRELATED_RULE,
	"TOOL-001":	WHITELIST_REASON.UNRELATED_RULE,
	"TOOL-800":	WHITELIST_REASON.UNRELATED_RULE,
	}

#===== Constants ==============================================#

WTRL_TRACER_JSON_SCHEMA_VERSION = "0.1.0"

RE_RULE_ID : Final[str] = r"[A-Z][A-Z][A-Z]+-[0-9][0-9][0-9]+"
RE_RULE_ID_COMPILED : Final[re.Pattern[str]] = re.compile(RE_RULE_ID)

RE_IDENTIFIER : Final[str] = r"[A-Za-z_][A-Za-z0-9_]*"
RE_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_IDENTIFIER)

RE_QUALIFIED_IDENTIFIER : Final[str] = r"[A-Za-z_][A-Za-z0-9_]*([.][A-Za-z_][A-Za-z0-9_]*)*"
RE_QUALIFIED_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_QUALIFIED_IDENTIFIER)

# Required for Definitions
RE_CSV_IDENTIFIERS = r"[A-Za-z_][A-Za-z0-9_]*(\s*[,]\s*[A-Za-z_][A-Za-z0-9_]*)*"
RE_CSV_IDENTIFIERS_COMPILED = re.compile(RE_CSV_IDENTIFIERS)

# ANSI SGR escape sequences, e.g. "\x1b[31m"
RE_ANSI_SGR: Final[str] = r"\x1b\[[0-9;]*m"
RE_ANSI_SGR_COMPILED: Final[re.Pattern[str]] = re.compile(RE_ANSI_SGR)

# Markup tokens for Waterloo roles, e.g. |type|`int` -> :wtrl_type:`int`
# Single Source of Truth is the documentation standard.
WTRL_MARKUP_ROLES: Final[str] = r"(attr|cmd|dfn|file|func|key|label|lit|mod|norm|op|opt|ref|tag|term|type|value|var|var_type)"
RE_WTRL_MARKUP_BACKTICK: Final[str] = rf"\|{WTRL_MARKUP_ROLES}\|`([^`]+)`"
RE_WTRL_MARKUP_BACKTICK_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_MARKUP_BACKTICK)

# References consist of two parts: clear text and <link>.
RE_WTRL_ANGLE_HTTPS_REF: Final[str] = r"^\s*([^<>`]+?)\s*<\s*(https?://[^>\s]+)\s*>\s*$"
RE_WTRL_ANGLE_HTTPS_REF_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_ANGLE_HTTPS_REF)

RE_WTRL_ANGLE_WTRL_REF: Final[str] = r"^\s*([^<>`]+?)\s*<\s*wtrl://([^>\s]+)\s*>\s*$"
RE_WTRL_ANGLE_WTRL_REF_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_ANGLE_WTRL_REF)

#RE_SUSPICIOUS_MARKUP_BACKTICK: Final[str] = rf"\|[a-zA-Z0-9_]+\|`"
#RE_SUSPICIOUS_MARKUP_BACKTICK_COMPILED: Final[re.Pattern[str]] = re.compile(RE_SUSPICIOUS_MARKUP_BACKTICK)

#CSV_SECTIONS = frozenset(["normative_sections", "scopes", "Public_classes", "Public_methods", "Public_functions", "See_also"])
SINGLE_STRING_SECTIONS = frozenset(["profile","status"])

class Trait(StrEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing the traits of a class.
		constructor:
			Inherit from |type|`str` and |type|`Enum`.
	Public_constants:
		ABSTRACT:
			The class is abstract, i.e. it cannot be instantiated directly and is not a complete specification of the concept.
		FINAL:
			The class is final, i.e. it cannot be subclassed and is a complete specification of the concept.
	"""
	ABSTRACT = "abstract"
	FINAL = "final"

trait_tag_map = {
	"abstract": Trait.ABSTRACT,
	"final": Trait.FINAL
	}
TRAIT_TAG_MAP = MappingProxyType(trait_tag_map)

# Valid profiles
Profile = Literal["module", "class", "function", "method", "inherited_method"]

# Scope values
class Scope(IntEnum):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing available scopes.
			|Must| provide a time-stable partial order for the constants.
		constructor:
			Inherit from |type|`int`.
	Public_constants:
		PUBLIC:
			Selects the public API.
		EXTENSION:
			Selects the API for developers of plugin and extensions.
		CORE:
			Selects the API for core developers.
	Notes:
		Purpose:
			The scope is an optional parameter for rendering functions.\
			It allows to restrict the set of rendered objects to a\
			well-defined audience.
		Values:
			The class only ensures the partial order but does not\
			ensure particular values for the constants.
	"""
	PUBLIC		= 10
	EXTENSION	= 20
	CORE		= 30

# Keys |must| be lower-case.
scope_tag_map = {
	"public": Scope.PUBLIC,
	"extension": Scope.EXTENSION,
	"core": Scope.CORE,
	}
scope_to_string = {
	Scope.PUBLIC: "public",
	Scope.EXTENSION: "extension",
	Scope.CORE: "core"
}

SCOPE_TAG_MAP = MappingProxyType(scope_tag_map)	

# Flavour for string output
class Flavour(IntEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing available flavours for rendering Normativity Keywords.
		constructor:
			Inherit from |type|`int`.
	Public_constants:
		RAW:
			Example: | + Must + |
		RFC_2119:
			Example: |lit|`MUST`
		MARKDOWN:
			Example: |lit|`**MUST**`
	"""
	RAW		= 0
	RFC_2119	= 1
	MARKDOWN	= 2

flavour_tag_map = {
	"raw":		Flavour.RAW,
	"rfc-2119":	Flavour.RFC_2119,
	"markdown":	Flavour.MARKDOWN,
	}
FLAVOUR_TAG_MAP = MappingProxyType(flavour_tag_map)	

# Format for string-related output
class Format(IntEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing available output formats for string rendering.
		constructor:
			Inherit from |type|`int`.
	Public_constants:
		JSON:
			Javascript Object Notation
		YAML:
			YAML Ain't Markup Language
		MD:
			Markdown.
	"""
	JSON		= 0
	YAML		= 1
	MD		= 2

format_tag_map = {
	"json":		Format.JSON,
	"yaml":		Format.YAML,
	"md":		Format.MD
	}
FORMAT_TAG_MAP = MappingProxyType(format_tag_map)	

class Status(StrEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing the values of subsection |label|`Preamble.status`.
		constructor:
			Inherit from |type|`Enum`.
	Public_constants:
		EXPERIMENTAL:
			See rule |ref|`STA-004 <section_function_pramble>`.
		STABLE:
			See rule |ref|`STA-004 <section_function_pramble>`.
		FROZEN:
			See rule |ref|`STA-004 <section_function_pramble>`.
		DEPRECATED:
			See rule |ref|`STA-004 <section_function_pramble>`.
		DRAFT:
			See rule |ref|`STA-004 <section_function_pramble>`.
	Notes:
		LoII:
			This docstring violates LoII in order to preserve SSoT,
			see |label|`Public_constants`.
	"""
	EXPERIMENTAL	= "experimental"
	STABLE		= "stable"
	FROZEN		= "frozen"
	DEPRECATED	= "deprecated"
	DRAFT		= "draft"

status_tag_map = {
	"experimental":	Status.EXPERIMENTAL,
	"stable":	Status.STABLE,
	"frozen":	Status.FROZEN,
	"deprecated":	Status.DEPRECATED,
	"draft":	Status.DRAFT
	}
STATUS_TAG_MAP = MappingProxyType(status_tag_map)	

#===== begin section and subsection properties ===============#

# NOTE ABOUT SOURCE OF TRUTH:
# The tables in this block define the runtime-friendly structural metadata used by
# validators, explain output, and related tooling. They are an implementation view
# of the Waterloo section/subsection model, not the normative definition itself.
#
# Normative SSoT is the documentation in format.rst. If this block and format.rst
# ever diverge, format.rst is authoritative and this block must be updated.

# These axes describe semantic status and applicability in the documentation rules.

Profile_t = Literal["module", "class", "function", "method", "inherited_method"]
Normativity_t = Literal["not_applicable", "normative", "informative", "can_be_both"]
MustExist_t = Literal["yes", "no", "depends_on_context"]
LabelKind_t = Literal["FIXED", "IDENTIFIER", "QUALIFIED_IDENTIFIER", "LIST_OF_IDENTIFIERS", "ANY_STRING"]

CANONICAL_ORDER_OF_SECTIONS : Final[Dict[str,None | Sequence[str]]] = {
	"Preamble"		: ("profile","normative_sections","status","scope"),
	"Definitions"		: None,
	"Terminology"		: None,
	"Contract"		: ("general","constructor","base","traits","invariants","requires","ensures"),
	"Description"		: None,
	"Derived_from"		: None,
	"Factory"		: None,
	"Public_classes"	: None,
	"Class_overview"	: None,
	"Public_functions"	: None,
	"Function_overview"	: None,
	"Public_methods"	: None,
	"Method_overview"	: None,
	"Public_types"		: None,
	"Public_variables"	: None,
	"Public_constants"	: None,
	"Parameters"		: None,
	"Returns"		: None,
	"Raises"		: None,
	"Notes"			: None,
	"See_also"		: None,
	}

CANONICAL_ORDER_OF_PROFILES: Final[list[Profile_t]] = ["module", "class", "function", "method", "inherited_method"]

SectionBodyCategory_t = Literal[
	"STRUCTURE",
	"IDENTIFIER",
	"QUALIFIED_IDENTIFIER",
	"LIST_OF_IDENTIFIERS",
	"LIST_OF_QUALIFIED_IDENTIFIERS",
	"ITEMIZED_TEXT",
	"FREEFORM_TEXT",
]

class SectionProperty_t(TypedDict):
	category: SectionBodyCategory_t
	normativity: Normativity_t
	label_kind: LabelKind_t
	profile: list[Profile_t]
	must_exist: MustExist_t
	hint: str

# Shared section catalog consumed by validator and explain tooling.
# Keep this mapping synchronized with format.rst, which remains the normative SSoT.
SECTION_PROPERTIES: Final[dict[str, SectionProperty_t]] = {
	# Normativity does not apply to Preamble because normativity is declared therein, and normativity
	# does not apply to subsections because they are normative if and only if the surrounding section is normative (BinNorm).
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: not_applicable
	# "must_exist" rules: PRE-001
	"Preamble": {"category": "STRUCTURE", "normativity": "not_applicable", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, PRE-003
	# "normativity" rules: not_applicable
	# "must_exist" rules: PRE-003
	"Preamble.profile": {"category": "IDENTIFIER", "normativity": "not_applicable", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, PRE-006
	# "normativity" rules: not_applicable
	# "must_exist" rules: PRE-006
	"Preamble.normative_sections": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: PRE-016, PRE-019, STA-001
	# "normativity" rules: not_applicable
	# "must_exist" rules: STA-001
	"Preamble.status": {"category": "IDENTIFIER", "normativity": "not_applicable", "label_kind": "FIXED", "profile": ["function","method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, SCP-001
	# "normativity" rules: not_applicable
	# "must_exist" rules: SCP-001
	"Preamble.scope": {"category": "LIST_OF_IDENTIFIERS", "normativity": "not_applicable", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: DEF-002
	# "must_exist" rules: DEF-001
	"Definitions": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, DEF-003
	# "label_kind" rules: DEF-004, DEF-005
	# "normativity" rules: BinNorm, DEF-002
	# "must_exist" rules: DEF-020
	"Definitions.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "LIST_OF_IDENTIFIERS", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DEF-011, DEF-012
	# "normativity" rules: BinNorm, DEF-002
	# "must_exist" rules: DEF-012
	"Definitions._inherit": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative", "label_kind": "FIXED", "profile": ["class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# Terminology is the informative sister of Definitions. It is not allowed to contain normativity keywords but rather general explanations of terms.
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: TERM-002, TERM-003
	# "must_exist" rules: TERM-001
	"Terminology": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, TERM-004
	# "label_kind" rules: TERM-005, TERM-006
	# "normativity" rules: BinNorm, TERM-002
	# "must_exist" rules: TERM-009
	"Terminology.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "ANY_STRING", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: CON-002
	# "must_exist" rules: CON-001
	"Contract": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-022, CON-023, CON-024, CON-036
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-022, CON-023, CON-024, CON-036
	"Contract.general": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-007
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-007
	"Contract.constructor": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "FIXED", "profile": ["class"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-039
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-039
	"Contract.base": {"category": "QUALIFIED_IDENTIFIER", "normativity": "normative", "label_kind": "FIXED", "profile": ["inherited_method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: CON-012
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-012
	"Contract.traits": {"category": "LIST_OF_IDENTIFIERS", "normativity": "normative", "label_kind": "FIXED", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: CON-025
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-025
	"Contract.invariants": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "FIXED", "profile": ["function","method"], "must_exist": "no", "hint": ""},
	# "profile" rules: CON-047
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-047
	"Contract.requires": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "FIXED", "profile": ["function","method"], "must_exist": "no", "hint": ""},
	# "profile" rules: CON-049
	# "normativity" rules: BinNorm, CON-002
	# "must_exist" rules: CON-049
	"Contract.ensures": {"category": "ITEMIZED_TEXT", "normativity": "normative", "label_kind": "FIXED", "profile": ["function","method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: DESC-002
	# "must_exist" rules: DESC-001
	"Description": {"category": "FREEFORM_TEXT", "normativity": "can_be_both", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-004
	# "normativity" rules: DER-004
	# "must_exist" rules: DER-001
	"Derived_from": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "FIXED", "profile": ["class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-004
	# "normativity" rules: FAC-009
	# "must_exist" rules: FAC-001
	"Factory": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: FAC-004
	# "label_kind" rules: FAC-005
	# "normativity" rules: BinNorm, FAC-009
	# "must_exist" rules: FAC-004
	"Factory.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "QUALIFIED_IDENTIFIER", "profile": ["class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPCL-002, CPCL-002
	# "must_exist" rules: MPCL-001, CPCL-001
	"Public_classes": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "FIXED", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003
	# "normativity" rules: MPFN-002
	# "must_exist" rules: MPFN-001
	"Public_functions": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "FIXED", "profile": ["module"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-004
	# "normativity" rules: CPMT-002
	# "must_exist" rules: CPMT-001
	"Public_methods": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "normative", "label_kind": "FIXED", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPTYP-002, CPTYP-002
	# "must_exist" rules: MPTYP-001, CPTYP-001
	
	"Public_types": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MPTYP-003, CPTYP-003
	# "label_kind" rules: MPTYP-004, CPTYP-004
	# "normativity" rules: BinNorm, MPTYP-002, CPTYP-002
	# "must_exist" rules: MPTYP-003, CPTYP-003
	"Public_types.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPVAR-002, CPVAR-002
	# "must_exist" rules: MPVAR-001, CPVAR-001
	"Public_variables": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MPVAR-003, CPVAR-003
	# "label_kind" rules: MPVAR-004, CPVAR-004
	# "normativity" rules: BinNorm, MPVAR-002, CPVAR-002
	# "must_exist" rules: MPVAR-003, CPVAR-003
	"Public_variables.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MPCON-002, CPCON-002
	# "must_exist" rules: MPCON-001, CPCON-001
	"Public_constants": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MPCON-003, CPCON-003
	# "label_kind" rules: MPCON-004, CPCON-004
	# "normativity" rules: BinNorm, MPCON-002, CPCON-002
	# "must_exist" rules: MPCON-003, CPCON-003
	"Public_constants.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004
	# "normativity" rules: MCLO-002, CCLO-002
	# "must_exist" rules: MCLO-001, CCLO-001
	"Class_overview": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "FIXED", "profile": ["module","class"], "must_exist": "no", "hint": ""},
	# "profile" rules: MCLO-004, CCLO-004
	# "label_kind" rules: MCLO-005, CCLO-005
	# "normativity" rules: BinNorm, MCLO-002, CCLO-002
	# "must_exist" rules: MCLO-010, CCLO-010
	"Class_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "profile": ["module","class"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-004
	# "normativity" rules: CMTO-002
	# "must_exist" rules: CMTO-001
	"Method_overview": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "FIXED", "profile": ["class"], "must_exist": "no", "hint": ""},
	# "profile" rules: CMTO-004
	# "label_kind" rules: CMTO-005
	# "normativity" rules: BinNorm, CMTO-002
	# "must_exist" rules: CMTO-010
	"Method_overview.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "IDENTIFIER", "profile": ["class"], "must_exist": "no", "hint": ""},
	
	# "profile" rules: DOC-003
	# "normativity" rules: MFNO-002
	# "must_exist" rules: MFNO-001
	"Function_overview": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "FIXED", "profile": ["module"], "must_exist": "no", "hint": ""},
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
	"Parameters": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["function","method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: PAR-008
	# "label_kind" rules: PAR-006
	# "normativity" rules: BinNorm, PAR-002
	# "must_exist" rules: PAR-004, PAR-005
	"Parameters.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "IDENTIFIER", "profile": ["function","method"], "must_exist": "depends_on_context", "hint": ""},

	# "profile" rules: DOC-005
	# "normativity" rules: RET-002
	# "must_exist" rules: RET-001
	"Returns": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "FIXED", "profile": ["function","method"], "must_exist": "yes", "hint": ""},
	
	# "profile" rules: DOC-005
	# "normativity" rules: RAI-002
	# "must_exist" rules: RAI-001
	"Raises": {"category": "STRUCTURE", "normativity": "normative", "label_kind": "FIXED", "profile": ["function","method"], "must_exist": "yes", "hint": ""},
	# "profile" rules: RAI-011
	# "label_kind" rules: RAI-008
	# "normativity" rules: BinNorm, RAI-002
	# "must_exist" rules: RAI-011
	"Raises.<item>": {"category": "FREEFORM_TEXT", "normativity": "normative", "label_kind": "QUALIFIED_IDENTIFIER", "profile": ["function","method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: NOTE-002
	# "must_exist" rules: NOTE-001
	"Notes": {"category": "STRUCTURE", "normativity": "informative", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006, NOTE-005
	# "label_kind" rules: NOTE-006
	# "normativity" rules: BinNorm, NOTE-002
	# "must_exist" rules: NOTE-008
	"Notes.<item>": {"category": "FREEFORM_TEXT", "normativity": "informative", "label_kind": "ANY_STRING", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},

	# "profile" rules: DOC-003, DOC-004, DOC-005, DOC-006
	# "normativity" rules: SEE-011
	# "must_exist" rules: SEE-001
	"See_also": {"category": "LIST_OF_QUALIFIED_IDENTIFIERS", "normativity": "can_be_both", "label_kind": "FIXED", "profile": ["module","class","function","method","inherited_method"], "must_exist": "no", "hint": ""},
}

#===== end section and subsection properties =================#

_SOURCE_DOCSTRING_CACHE: Dict[int, str] = {}
AstDocNode: TypeAlias = Union[ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef]
# Per-module AST cache used to preserve raw docstring indentation and tabs.
_MODULE_AST_CACHE: WeakKeyDictionary[ModuleType, Tuple[str, ast.Module, Dict[str, list[AstDocNode]]]] = WeakKeyDictionary()
# Final docstring results are cached as well, because the wrapper walk is repeated often.
_OBJ_DOCSTRING_CACHE: Dict[int, str] = {}


def get_source_docstring(o: object) -> str:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| return a raw source docstring for |var|`o` if the defining source text can be obtained.
			|Must| support modules, classes, functions, methods, and routine-like objects for which source text is available.
			|Must| prefer the source docstring over any runtime |value|`__doc__` representation.
			|Must| cache the extracted result globally by object identity to avoid repeated source parsing.
			|Must| cache one parsed AST per module and reuse it for subsequent lookups.
			|Must| preserve original indentation and tabs in order to remain compatible with Waterloo parsing under Python 3.13+.
			|Should| fall back to a direct source snippet parse when the object is a decorated or wrapper-like callable\
			that cannot be resolved reliably through the module AST.\
			The AST-based source lookup is intentionally slower than direct runtime docstring access and is therefore\
			implemented with caching as a first-order mitigation, not as a full performance optimization.
			|Must| return the empty string if no source docstring can be determined.
	Parameters:
		o:
			Any documentable object whose defining source docstring should be extracted.
	Returns:
		|Must| return the raw source docstring text, or the empty string if none is available.
	Raises:
	Notes:
		Implementation:
			The helper uses a source-first strategy to preserve original indentation and tab characters in Python 3.13+.
			Docstrings are cached by object identity, while parsed module ASTs are cached separately by module object.
			The AST path is slower than runtime |var|`__doc__` access, but caching keeps the repeated cost manageable.
			Further performance improvements can be added later by caching validation results for repeated objects.
	"""
	key = id(o)
	if key in _SOURCE_DOCSTRING_CACHE:
		return _SOURCE_DOCSTRING_CACHE[key]
	doc = ""
	if isinstance(o, property):
		# Properties inherit their documentation from accessor methods.
		# Use the getter first because it is the canonical docstring source.
		for accessor in (o.fget, o.fset, o.fdel):
			if accessor is None:
				continue
			doc = get_source_docstring(accessor)
			if doc:
				break
	if inspect.ismodule(o) or inspect.isclass(o) or inspect.isroutine(o):
		mod = o if isinstance(o, ModuleType) else inspect.getmodule(o)
		try:
			if isinstance(mod, ModuleType):
				# The module source is the canonical raw text for module docstrings and
				# for building the AST index used to resolve nested classes/functions.
				src = inspect.getsource(mod)
				ast_index: Dict[str, list[AstDocNode]] = {}
				# Reuse the parsed module AST whenever we already have it in the cache.
				# This avoids reparsing the same file for every object from that module.
				if mod in _MODULE_AST_CACHE:
					_, tree, ast_index = _MODULE_AST_CACHE[mod]
				else:
					# Parse the full module once so nested definitions remain addressable by
					# their source-qualified names, preserving original indentation and tabs.
					tree = ast.parse(src)

					# Index nested class/function definitions by fully qualified name.
					def _index_node(node: ast.AST, prefix: str = "") -> None:
						body = getattr(node, "body", None)
						if not isinstance(body, list):
							return
						for child in body:
							if not isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
								continue
							name = child.name
							qual = f"{prefix}.{name}" if prefix else name
							ast_index.setdefault(qual, []).append(child)
							_index_node(child, qual)

					_index_node(tree)
					_MODULE_AST_CACHE[mod] = (src, tree, ast_index)
				qualname = getattr(o, "__qualname__", "") if not isinstance(o, ModuleType) else ""
				if isinstance(o, ModuleType):
					# Module docstrings live on the AST root.
					doc = ast.get_docstring(tree, clean=False) or ""
				elif qualname:
					# Normalize nested/locals-style qualnames to the AST index format.
					# This keeps wrappers and <locals> names usable for AST lookup.
					qualname = qualname.replace(".<locals>.", ".").replace(".<locals>", "")
					qualname = qualname.split("[", 1)[0]
					nodes = ast_index.get(qualname, [])
					node: AstDocNode | None = None
					if len(nodes) == 1:
						# Fast path: exactly one AST definition matches this qualified name.
						node = nodes[0]
					elif len(nodes) > 1:
						# Property accessors and similar wrappers can share a qualified name.
						# Use the source line to choose the definition that actually matches.
						try:
							_, lineno = inspect.getsourcelines(o)
						except Exception:
							lineno = None
						if lineno is not None:
							for cand in nodes:
								cand_lineno = getattr(cand, "lineno", None)
								decorators = getattr(cand, "decorator_list", None)
								if isinstance(decorators, list) and decorators:
									first_lineno = getattr(decorators[0], "lineno", cand_lineno)
								else:
									first_lineno = cand_lineno
								if first_lineno == lineno:
									node = cand
									break
						if node is None:
							# If source line selection fails, fall back to the first indexed node.
							node = nodes[0]
					if node is not None:
						doc = ast.get_docstring(node, clean=False) or ""
				if not doc and not isinstance(o, ModuleType):
					# Last-resort fallback for objects that have a source file but are not
					# directly resolvable through the module AST.
					try:
						src_obj = inspect.getsource(o)
						tree_obj = ast.parse(textwrap.dedent(src_obj))
						body = getattr(tree_obj, "body", [])
						if body:
							first = body[0]
							if isinstance(first, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
								doc = ast.get_docstring(first, clean=False) or ""
					except Exception:
						doc = ""
		except Exception:
			# Any source/AST failure means we cannot recover the raw docstring reliably.
			# Let the caller fall back to the runtime __doc__ or descriptor chain.
			doc = ""
	_SOURCE_DOCSTRING_CACHE[key] = doc
	return doc

#===== begin render functions for verbose diagnostics ========#

#----- explain command builders ------------------------------#

def explain_try_self_for_section(label: str, profile: str) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build the canonical self-explanation command for a section label and profile.
	Parameters:
		label:
			The section label to explain.
		profile:
			The docstring profile to use as the explain context.
	Returns:
		The canonical |cmd|`explain-section` command for the given label and profile.
	Raises:
	"""
	return f"waterlint explain-section --label {label} --profile {profile}"

def explain_try_self_for_subsection(label: str, profile: str) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build the canonical self-explanation command for a fully qualified subsection label and profile.
	Parameters:
		label:
			The fully qualified subsection label to explain.
		profile:
			The docstring profile to use as the explain context.
	Returns:
		The canonical |cmd|`explain-subsection` command for the given label and profile.
	Raises:
	"""
	return f"waterlint explain-subsection --label {label} --profile {profile}"

#----- source and expected snippet renderers -----------------#

def render_source_snippet(section_label: str, subsections: Iterable[str] | None = None) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact section snippet with canonical subsection ordering.
	Parameters:
		section_label:
			The section label to render.
		subsections:
			The subsection labels to render under the section label. If omitted, the canonical order for the
			section is used when available.
	Returns:
		A compact list of lines that renders the section label followed by subsection placeholders.
	Raises:
	"""
	canonical = CANONICAL_ORDER_OF_SECTIONS.get(section_label)
	if subsections is None:
		ordered = list(canonical) if canonical is not None else []
	else:
		ordered = list(subsections)
		if canonical is not None:
			order = {name: index for index, name in enumerate(canonical)}
			ordered.sort(key=lambda name: order.get(name, len(order)))
	lines = [f"{section_label}:"]
	for subsection in ordered:
		lines.append(f"\t{subsection}:")
		lines.append("\t\t...")
	return lines


def render_expected_snippet(section_label: str, subsections: Iterable[str] | None = None) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render the canonical expected snippet for a section.
	Parameters:
		section_label:
			The section label to render.
		subsections:
			The subsection labels to render under the section label.
	Returns:
		The canonical expected section snippet as a list of lines.
	Raises:
	"""
	return render_source_snippet(section_label, subsections)


def render_allowed_identifier(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection that expects exactly one identifier.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The allowed identifier values.
	Returns:
		A compact list of lines that states the allowed identifier values in one line.
	Raises:
	"""
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
	else:
		section_label, subsection_label = label, None
	items = list(dict.fromkeys(identifiers))
	if not items:
		items = ["..."]
	lines = [f"{section_label}:"]
	if subsection_label is not None:
		lines.append(f"\t{subsection_label}:")
		lines.append(f"\t\t<one of: {{ {', '.join(items)} }}>")
	else:
		lines.append(f"\t<one of: {{ {', '.join(items)} }}>")
	return lines


def render_expected_identifier(label: str, expected_kind: Literal["identifier", "qualified identifier"]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render the expected syntax for a single identifier-like value.
	Parameters:
		label:
			The subsection label to render.
		expected_kind:
			Use |token|`identifier` or |token|`qualified identifier` to describe the expected syntax class.
	Returns:
		A compact list of lines that states the expected syntax in the Waterloo snippet format.
	Raises:
	"""
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
	else:
		section_label, subsection_label = label, None
	lines = [f"{section_label}:"]
	if subsection_label is not None:
		lines.append(f"\t{subsection_label}:")
		lines.append(f"\t\t<{expected_kind}>")
	else:
		lines.append(f"\t<{expected_kind}>")
	return lines

def render_suggestion(label: str, suggestion: str) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a suggestion snippet either without or for a section or subsection in order to fix the docstring.
			|Must| add angle brackets around the suggestion to indicate that it is a placeholder for the actual content.
		requires:
			The suggestion |should| be a brief and concise plain single line text.
	Parameters:
		label:
			The section or subsection label (as qualified name) to render.
			An empty label means the suggestion is not bound to a specific section or subsection.
		suggestion:
			A brief suggestion of what the section or subsection could be or contain.
	Returns:
		A compact list of lines that states the suggested section or subsection in one line.
	Raises:
	"""
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
	else:
		section_label, subsection_label = label, None
	lines = []
	if subsection_label:
		lines.append(f"{section_label}:")
		lines.append(f"\t{subsection_label}:")
		lines.append(f"\t\t<{suggestion}>")
	elif section_label:
		lines.append(f"{section_label}:")
		lines.append(f"\t<{suggestion}>")
	else:
		lines.append(f"<{suggestion}>")
	return lines

def render_allowed_identifiers(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection that expects a list of identifiers.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The allowed identifier values.
	Returns:
		A compact list of lines that states the allowed identifier values in one line.
	Raises:
	"""
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
	else:
		section_label, subsection_label = label, None
	items = list(dict.fromkeys(identifiers))
	if not items:
		items = ["..."]
	lines = [f"{section_label}:"]
	if subsection_label is not None:
		lines.append(f"\t{subsection_label}:")
		lines.append(f"\t\t<some of: {{ {', '.join(items)} }}>")
	else:
		lines.append(f"\t<some of: {{ {', '.join(items)} }}>")
	return lines


def render_identifier_lines(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render the found identifiers of a list-valued subsection in a compact form.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The identifier values exactly as found.
	Returns:
		A compact list of lines that states the identifier values in one line without semantic normalization.
	Raises:
	"""
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
	else:
		section_label, subsection_label = label, None
	items = list(identifiers)
	if not items:
		items = ["..."]
	lines = [f"{section_label}:"]
	if subsection_label is not None:
		lines.append(f"\t{subsection_label}:")
		lines.append(f"\t\t{', '.join(items)}")
	else:
		lines.append(f"\t{', '.join(items)}")
	return lines


def render_deduplicated_identifiers(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection after removing duplicate identifiers.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The identifier values with duplicates removed while preserving the first occurrence order.
	Returns:
		A compact list of lines that states the deduplicated identifier values in one line.
	Raises:
	"""
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
	else:
		section_label, subsection_label = label, None
	items = list(dict.fromkeys(identifiers))
	if not items:
		items = ["..."]
	lines = [f"{section_label}:"]
	if subsection_label is not None:
		lines.append(f"\t{subsection_label}:")
		lines.append(f"\t\t{', '.join(items)}")
	else:
		lines.append(f"\t{', '.join(items)}")
	return lines


def render_unique_identifiers(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection that requires unique identifiers.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The canonical identifier values.
	Returns:
		A compact list of lines that states the canonical identifier values and mentions uniqueness.
	Raises:
	"""
	lines = render_deduplicated_identifiers(label, identifiers)
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
	else:
		section_label, subsection_label = label, None
	if subsection_label is not None:
		lines.append("\t\t(each identifier may occur at most once)")
	else:
		lines.append("\t(each identifier may occur at most once)")
	return lines

#----- diagnostics renderers for specific validation cases ---#

def render_normative_section_details(section_label: str, normative_sections: Iterable[str], profile: str, *, action: Literal["add", "remove"]) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for normative section membership checks.
	Parameters:
		section_label:
			The section label that should be added to or removed from the normative section set.
		normative_sections:
			The current normative section labels.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
		action:
			Either |token|`add` when the section should be present, or |token|`remove` when it should be absent.
	Returns:
		A details dictionary with |token|`found`, |token|`expected`, and |token|`hint`.
	Raises:
	"""
	current = list(normative_sections)
	if action == "add":
		expected = [*current, section_label]
	else:
		expected = [item for item in current if item != section_label]
	return {
		"found": render_identifier_lines("Preamble.normative_sections", current),
		"expected": render_deduplicated_identifiers("Preamble.normative_sections", expected),
		"hint": explain_try_self_for_section(section_label, profile),
	}


def render_missing_entry_details(container_label: str, current_entries: Iterable[str], missing_entry: str, profile: str, *, top_level: bool = False) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a missing entry in a section-like container.
	Parameters:
		container_label:
			The section label that contains the missing entry.
		current_entries:
			The currently present entry labels in the container.
		missing_entry:
			The entry label that should be added.
		profile:
			The docstring profile used for the |cmd|`explain-*` hint.
		top_level:
			Use a top-level list rendering when the container itself is the document root rather than a nested section.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(current_entries)
	found = [e for e in current for e in (e, "\t...")]
	expected = [e for e in [*current, missing_entry] for e in (e, "\t...")]
	if top_level:
		# This is a special marker case for the document root level, which is not rendered
		# with a section header and therefore needs a custom label in the snippets and hints.
		return {
			"found": found,
			"expected": expected,
			"hint": explain_try_self_for_section(missing_entry, profile),
		}
	return {
		"found": render_source_snippet(container_label, current),
		"expected": render_expected_snippet(container_label, expected),
		"hint": explain_try_self_for_subsection(f"{container_label}.{missing_entry}", profile),
	}


def render_overview_requires_section_details(overview_label: str, required_section: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for overview sections that require a normative companion section.
	Parameters:
		overview_label:
			The overview section label, such as |token|`Class_overview`.
		required_section:
			The normative section that must be added, such as |token|`Public_classes`.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |token|`found`, |token|`expected`, and |token|`hint`.
	Raises:
	"""
	return {
		"found": [f"{overview_label}", "\t..."],
		"expected": [f"<add normative section {required_section}>"],
		"hint": explain_try_self_for_section(required_section, profile),
	}


def render_name_object_consistency_details(label: str, current_entries: Iterable[str], profile: str, *, overview_item: str | None = None) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for name/object consistency checks.
	Parameters:
		label:
			The section label to render.
		current_entries:
			The current raw entries from the section.
		profile:
			The docstring profile used for the hint.
		overview_item:
			If provided, render an overview entry instead of a flat identifier list.
	Returns:
		A details dictionary with |token|`found`, |token|`expected`, and |token|`hint`.
	Raises:
	"""
	if overview_item is None:
		return {
			"found": render_identifier_lines(label, current_entries),
			"expected": ["<check name/object consistency>"],
			"hint": explain_try_self_for_section(label, profile),
		}
	return {
		"found": render_source_snippet(label, [overview_item]),
		"expected": ["<check name/object consistency>"],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_listed_object_missing_details(label: str, member_name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for a listed object that has no matching runtime object.
	Parameters:
		label:
			The section label to render.
		member_name:
			The listed entry name that has no matching object.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [member_name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_section(label, profile),
	}


def render_profile_mismatch_details(object_name: str, object_kind: str, current_profile: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for a profile mismatch.
	Parameters:
		object_name:
			The documented object name.
		object_kind:
			The detected object kind such as module, class, function or method-like.
		current_profile:
			The profile found in the docstring.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the hint.
	Returns:
		A details dictionary with |token|`found`, |token|`expected`, and |token|`hint`.
	Raises:
	"""
	expected_text = expected_text.strip()
	if expected_text.startswith("<") and expected_text.endswith(">") and len(expected_text) >= 2:
		expected_text = expected_text[1:-1].strip()
	return {
		"found": [
			"Preamble",
			"\tprofile:",
			f"\t\t{current_profile}",
		],
		"expected": render_suggestion("Preamble.profile", expected_text),
		"hint": explain_try_self_for_subsection("Preamble.profile", profile),
	}


def render_normativity_keyword_details(section_label: str, entry_name: str, current_lines: Iterable[str], suggestion: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for an entry that must not contain normativity keywords.
	Parameters:
		section_label:
			The overview section label, such as |token|`Class_overview`.
		entry_name:
			The entry label that violates the rule.
		current_lines:
			The raw lines found in the entry.
		suggestion:
			A brief informative replacement suggestion for the entry.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |token|`found`, |token|`expected`, and |token|`hint`.
	Raises:
	"""
	found_lines = list(current_lines)
	if not found_lines:
		found_lines = ["..."]
	return {
		"found": [f"{section_label}:", f"\t{entry_name}:"] + [f"\t\t{line}" for line in found_lines],
		"expected": [f"{section_label}:", f"\t{entry_name}:", f"\t\t<{suggestion}>"],
		"hint": explain_try_self_for_section(section_label, profile),
	}


def render_exception_reference_details(exception_name: str, profile: str, *, expected_kind: Literal["qualified identifier", "subclass of BaseException"]) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Raises entry that must resolve to an exception class.
	Parameters:
		exception_name:
			The exception entry name found in the Raises section.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
		expected_kind:
			Either |token|`qualified identifier` or |token|`subclass of BaseException`.
	Returns:
		A details dictionary with |token|`found`, |token|`expected`, and |token|`hint`.
	Raises:
	"""
	if expected_kind == "qualified identifier":
		expected = ["<check for typos or qualify properly>"]
	else:
		expected = ["<refer to an Exception class derived from BaseException>"]
	return {
		"found": render_source_snippet("Raises", [exception_name]),
		"expected": expected,
		"hint": explain_try_self_for_subsection("Raises.<item>", profile),
	}


def render_base_method_reference_details(current_entries: Iterable[str], expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Contract.base reference problem.
	Parameters:
		current_entries:
			The current raw entries found in Contract.base.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = [str(item) for item in current_entries]
	expected_text = expected_text.strip()
	if expected_text.startswith("<") and expected_text.endswith(">") and len(expected_text) >= 2:
		expected_text = expected_text[1:-1].strip()
	return {
		"found": render_source_snippet("Contract.base", current),
		"expected": render_suggestion("Contract.base", expected_text),
		"hint": [f"waterlint explain-subsection --label Contract.base --profile {profile}"],
	}


def render_exactly_one_identifier_details(label: str, current_entries: Iterable[str], profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a subsection that must contain exactly one identifier.
	Parameters:
		label:
			The qualified subsection label to render in the snippets and hint.
		current_entries:
			The current raw entries from the subsection.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(current_entries)
	return {
		"found": render_identifier_lines(label, current),
		"expected": render_expected_identifier(label, "identifier"),
		"hint": explain_try_self_for_subsection(label, profile),
	}


def render_parameter_signature_details(section_label: str, current_entries: Iterable[str], expected_entries: Iterable[str], profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a parameter/signature mismatch.
	Parameters:
		section_label:
			The label to render in the snippets.
		current_entries:
			The current raw parameter entries.
		expected_entries:
			The corrected parameter entries to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(current_entries)
	expected = list(expected_entries)
	return {
		"found": render_source_snippet(section_label, current),
		"expected": render_expected_snippet(section_label, expected),
		"hint": explain_try_self_for_section(section_label, profile),
	}


def render_see_also_reference_details(reference: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			module
		normative_sections:
			See_also
	Contract:
		general:
			|Must| build standardized validation details for a See_also reference mismatch.
	Parameters:
		reference:
			The raw reference text as found in the See_also section.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet("See_also", [reference]),
		"expected": [expected_text],
		"hint": [f"waterlint explain-section --label See_also --profile {profile}"],
	}


def render_scope_relation_details(
	containing_kind: str,
	containing_scopes: Scopes,
	is_containing_scope_explicit: bool,
	contained_kind: str,
	contained_scopes: Scopes,
	is_contained_scope_explicit: bool,
	section_label: str,
	reference: str,
	expected_text: str,
	profile: str,
) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a scope monotonicity violation.
	Parameters:
		containing_kind:
			The kind of the containing object, such as module or class.
		containing_scopes:
			The scopes of the containing object.
		is_containing_scope_explicit:
			Whether the containing object declared its scope explicitly.
		contained_kind:
			The kind of the contained object, such as function, class, or method.
		contained_scopes:
			The scopes of the contained object.
		is_contained_scope_explicit:
			Whether the contained object declared its scope explicitly.
		section_label:
			The section label to render.
		reference:
			The offending reference as found in the source section.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	def _render_scope_block(kind: str, scopes: Scopes, is_explicit: bool, *, name: str | None = None) -> list[str]:
		scope_values = ", ".join(scope_to_string[scope] for scope in sorted(scopes, key=lambda s: getattr(s, "value", 0)))
		scope_state = "<explicit>" if is_explicit else "<implicit>"
		label = f"<in docstring of {kind}>" if name is None else f"<in docstring of {kind} '{name}'>"
		return [label, "Preamble:", "\tscope:", f"\t\t{scope_values} {scope_state}"]

	return {
		"found": _render_scope_block(containing_kind, containing_scopes, is_containing_scope_explicit)
					+ render_source_snippet(section_label, [reference])
					+ _render_scope_block(contained_kind, contained_scopes, is_contained_scope_explicit, name=reference),
		"expected": [expected_text],
		"hint": [f"waterlint explain-subsection --label Preamble.scope --profile {profile}"],
	}


def render_base_method_docstring_details(base_name: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a base-method docstring problem.
	Parameters:
		base_name:
			The base method name found in Contract.base.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_identifier_lines("Contract.base", [base_name]),
		"expected": ["<implement a Waterloo docstring in base method>"],
		"hint": [f"waterlint explain-subsection --label Contract.base --profile {profile}"],
	}


def render_definition_reference_details(references: str | Iterable[str], profile: str, *, missing_definitions: bool) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a term reference problem in Definitions.
	Parameters:
		references:
			The term reference or term references found in the docstring body.
		profile:
			The docstring profile used for the |cmd|`explain-section` or |cmd|`explain-subsection` hint.
		missing_definitions:
			Whether the Definitions section itself is missing.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	if isinstance(references, str):
		current = [references]
	else:
		current = [str(reference) for reference in references]
	if missing_definitions:
		return {
			"found": render_identifier_lines("term refs", sorted(dict.fromkeys(current))),
			"expected": ["<add normative section Definitions>"],
			"hint": explain_try_self_for_section("Definitions", profile),
		}
	return {
		"found": render_identifier_lines("term", current[:1] if current else ["..."]),
		"expected": ["<define term in Definitions>"],
		"hint": explain_try_self_for_subsection("Definitions.<item>", profile),
	}


def render_inherited_definition_details(current_inherited_terms: Iterable[str], profile: str, *, expected_text: str, use_section_hint: bool = False) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for an inherited Definitions problem.
	Parameters:
		current_inherited_terms:
			The inherited definition terms found in the current object.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		use_section_hint:
			Whether the hint should point to the section-level |cmd|`explain-section` entry instead of the
			subsection-level inherited definition entry.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(dict.fromkeys(str(term) for term in current_inherited_terms))
	if use_section_hint:
		hint = explain_try_self_for_section("Definitions", profile)
	else:
		hint = explain_try_self_for_subsection("Definitions._inherit", profile)
	return {
		"found": render_identifier_lines("Definitions._inherit", current if current else ["..."]),
		"expected": [expected_text],
		"hint": hint,
	}


def render_type_reference_details(label: str, type_name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Public_types reference problem.
	Parameters:
		label:
			The subsection label to render.
		type_name:
			The type entry name found in the subsection.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [type_name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_constant_reference_details(label: str, const_name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Public_constants reference problem.
	Parameters:
		label:
			The subsection label to render.
		const_name:
			The constant entry name found in the subsection.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [const_name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_named_value_reference_details(label: str, name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Public_variables reference problem.
	Parameters:
		label:
			The subsection label to render.
		name:
			The variable entry name found in the subsection.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_overview_missing_member_details(overview_label: str, public_label: str, current_entries: Iterable[str], missing_name: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for an overview entry that is missing from its matching Public_* section.
	Parameters:
		overview_label:
			The overview section label, such as |token|`Class_overview`.
		public_label:
			The matching public section label, such as |token|`Public_classes`.
		current_entries:
			The current raw entries from the overview section.
		missing_name:
			The entry name that is missing from the public section.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(overview_label, [missing_name] + [str(item) for item in current_entries if str(item) != missing_name]),
		"expected": [f"<add {missing_name} to {public_label}>"],
		"hint": explain_try_self_for_subsection(f"'{public_label}.<item>'", profile),
	}

#===== end render functions for verbose diagnostics ==========#

#===== Config =================================================#

class ConfigTraversal:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
		scope:
			public
	Contract:
		general:
			|Must| provide public methods to configure object traversal for functions like |func|`gen_documentable_objects`.
			|Must| provide (internal) boolean methods which accept or refuse traversal at a given node in the object tree.
		constructor:
			|Must| be default-constructible
	Notes:
		Experimental:
			This class will likely be expanded in the future,\
			and we are postponing the normative documentation for now.
		Configure:
			Use |func|`enable_include_imported` to allow descending into imported modules.
		Future:
			Possible extensions include acceptance/refusal by regular expressions.
		Example:
			|ref|`gen_documentable_objects <example_gen_documentable_objects>`
	"""
	def __init__(self) -> None:
		self._include_imported = False
		self._walk_packages = False
	def __repr__(self) -> str:
		return "ConfigTraversal()"
	def enable_include_imported(self) -> Self:
		self._include_imported = True
		return self
	def include_imported(self) -> bool:
		return self._include_imported
	def enable_walk_packages(self) -> Self:
		self._walk_packages = True
		return self
	def disable_walk_packages(self) -> Self:
		self._walk_packages = False
		return self
	def walk_packages(self) -> bool:
		return self._walk_packages
	def is_member_in_module(self,obj_parent: ModuleType | None,member: Documentable) -> bool:
		if obj_parent == None:
			return True
		return getattr(member, "__module__", None) == obj_parent.__name__
# False means: keep traversal within the module's own namespace
	def accept_imported_module(self,obj_parent: ModuleType,member: ModuleType) -> bool:
		return self.include_imported() or member.__name__.startswith(obj_parent.__name__ + ".")
	def accept_member_of_module(self,obj_parent: ModuleType,member: Documentable) -> bool:
		return self.include_imported() or self.is_member_in_module(obj_parent,member)

#===== Typechecking ===========================================#

# A single string can be a docstring subtree.
DocstringSubtree: TypeAlias = Union[str, List["DocstringSubtree"]]

# A docstring tree is always a list.
DocstringTree: TypeAlias = List[DocstringSubtree]

AnnotatableObject: TypeAlias = Union[type, ModuleType, FunctionType]

RuleId: TypeAlias = str
Origin: TypeAlias = Literal["parsing", "validation", "tool", "extension"]
Details: TypeAlias = Dict[str,Any]

Scopes: TypeAlias = Set[Scope]

Documentable: TypeAlias = ModuleType | type[object] | Callable[..., Any]

def is_annotatable(obj: Any) -> TypeGuard[AnnotatableObject]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| decide whether |var|`obj` is one of the annotatable runtime object kinds supported by the helper layer.
	Parameters:
		obj:
			The object to test.
	Returns:
		|True| if |var|`obj` is annotatable, else |False|.
	Raises:
	"""
	return isinstance(obj, (type, ModuleType, FunctionType))

def is_attr_annotated(obj : AnnotatableObject, attr: str) -> bool:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| find out whether the attribute passed is annotated.
	Parameters:
		obj:
			The class or module containing the attribute.
		attr:
			The name of the attribute to be tested.
	Returns:
		|Must| return |True| if the attribute is annotated, else |False|.
	Raises:
		BaseException:
			|May| propagate exceptions from |func|`getattr`.
	Notes:
		Last review:
			2026-02-04
	"""
	return attr in get_obj_annotations(obj)

def is_attr_final(obj : AnnotatableObject, attr: str) -> bool:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| find out whether the attribute passed is annotated as |type|`Final`.
	Parameters:
		obj:
			The class or module containing the attribute.
		attr:
			The name of the attribute to be tested.
	Returns:
		|Must| return |True| if the attribute is annotated as |type|`Final`, else |False|.
	Raises:
		BaseException:
			|May| propagate exceptions from |func|`get_type_hints`.
	Notes:
		Last review:
			2026-02-04
	"""
# Get type annotations
	hints = get_type_hints(obj, include_extras=True)
	hint = hints.get(attr)
# Is final or not
	return get_origin(hint) is Final

def is_list_of_str(val: Any) -> TypeGuard[List[str]]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| decide whether |var|`val` is a list whose items are all strings.
	Parameters:
		val:
			The value to test.
	Returns:
		|True| if |var|`val` is a list of strings, else |False|.
	Raises:
	"""
	if not isinstance(val,list):
		return False
	for item in val:
		if not isinstance(item,str):
			return False
	return True

#===== Object properties ======================================#
def is_obj_module(obj: object) -> TypeIs[ModuleType]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| relay to |func|`inspect.ismodule`
	Parameters:
		obj:
			The object to inspect.
	Returns:
		|True| if |var|`obj` is a module.
	Raises:
		BaseException:
			|May| propagate exceptions from |mod|`inspect`.
	Notes:
		Purpose:
			Uniform wrapper, allows us to add debugging output or hooks in case of trouble.
	"""
	return inspect.ismodule(obj)
def is_obj_class(obj: object)  -> TypeIs[type[object]]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| relay to |func|`inspect.isclass`
	Parameters:
		obj:
			The object to inspect.
	Returns:
		|True| if |var|`obj` is a class.
	Raises:
		BaseException:
			|May| propagate exceptions from |mod|`inspect`.
	Notes:
		Purpose:
			Uniform wrapper, allows us to add debugging output or hooks in case of trouble.
	"""
	return inspect.isclass(obj) and hasattr(obj, "__dict__")
def is_obj_function(obj: object) -> TypeIs[Callable[...,Any]]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| relay to |func|`inspect.isroutine`
	Parameters:
		obj:
			The object to inspect.
	Returns:
		|True| if |var|`obj` is a routine, which is a pretty general concept for "something that can be called", but excludes callable classes.
	Raises:
		BaseException:
			|May| propagate exceptions from |mod|`inspect`.
	Notes:
		Purpose:
			Uniform wrapper, allows us to add debugging output or hooks in case of trouble.
	"""
	return inspect.isroutine(obj)

def is_obj_method_like(obj: object) -> TypeIs[Callable[...,Any]]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| detect callables which should be treated as "method-like" for Waterloo profile heuristics.
			|Must| return |False| for non-routines.
			|Must| treat callables with class-like |value|`__qualname__` (`A.f`) as method-like.
			|Should| additionally use decorators |lit|`@staticmethod`, |lit|`@classmethod`, |lit|`@abstractmethod`, |lit|`@abc.abstractmethod` as hints.
	Parameters:
		obj:
			Object to inspect.
	Returns:
		|True| if |var|`obj` is callable and method-like by heuristic.
	Raises:
	"""
	if not is_obj_function(obj):
		return False
	if inspect.ismethod(obj):
		return True
	qual = getattr(obj, "__qualname__", "")
	if isinstance(qual, str) and "." in qual and "<locals>" not in qual:
		return True
	try:
		decorator_lines = get_obj_decorators(obj)
		if any(
			line in ("@staticmethod", "@classmethod", "@abstractmethod", "@abc.abstractmethod")
			for line in decorator_lines
		):
			return True
	except Exception:
		pass
	return False

def is_obj_named_value(obj: object) -> TypeIs[Callable[...,Any]]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| be equivalent to not |func|`is_obj_module` and not |func|`is_obj_class` and not |func|`is_obj_function`.
		requires:
			The caller |must| ensure that the object exists.
	Parameters:
		obj:
			The object to inspect.
	Returns:
		|True| if |var|`obj` is a named value
	Raises:
		BaseException:
			|May| propagate exceptions from |mod|`inspect`.
	Notes:
		Purpose:
			Uniform wrapper, allows us to add debugging output or hooks in case of trouble.
	"""
	return not is_obj_module(obj) and not is_obj_class(obj) and not is_obj_function(obj)

def is_obj_documentable(obj: object) -> TypeIs[Documentable]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| find out if the object passed can have a docstring.
	Parameters:
		obj:
			The object to examine.
	Returns:
		|True| if |var|`obj` is a module, class or function, else |False|.
	Raises:
	"""
	return is_obj_module(obj) or is_obj_class(obj) or is_obj_function(obj)

def get_obj_direct_module(obj: object) -> ModuleType | None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| return the direct owner module of |var|`obj`.
			|Must| return |var|`obj` unchanged if |var|`obj` is a module.
			|Must| try to resolve the module named by |var|`obj.__module__` for classes and callables.
			|Must| return |None| if no direct module can be resolved.
			|Must| avoid deep traversal (e.g. not resolve enclosing module hierarchies recursively).
	Parameters:
		obj:
			The object to inspect.
	Returns:
		The direct module object, or |None| if unavailable.
	Raises:
		ImportError:
			|May| be raised by module import helpers if implementation chooses to import by name.
		ValueError:
			|May| be raised by import helpers for malformed module names.
		AttributeError:
			|May| be raised by low-level inspection for malformed objects.
	Notes:
		Boundary:
			"Direct module" is defined by immediate metadata (`__module__`) only.
			Nested ownership (class-inside-class, closures, descriptors) is out of scope.
	"""
# obj is a module? Nothing to do.
	if isinstance(obj, ModuleType):
		return obj
# Primary path: resolve immediate __module__ metadata.
	modname = getattr(obj, "__module__", None)
	if isinstance(modname, str) and modname:
# Try to find in sys.modules.
		mod = sys.modules.get(modname, None)
		if isinstance(mod, ModuleType):
			return mod
# Try to import.
		try:
			mod = importlib.import_module(modname)
		except Exception:
			mod = None
# Really a module? Then we're done.
		if isinstance(mod, ModuleType):
			return mod
# Fallback: inspect-based resolution for odd callables/descriptors/instances.
	try:
		mod = inspect.getmodule(obj)
	except Exception:
		mod = None
	if isinstance(mod, ModuleType):
		return mod
# Last fallback for instances/proxies lacking a useful __module__ on the object itself.
	cls = getattr(obj, "__class__", None)
	cls_modname = getattr(cls, "__module__", None)
	if isinstance(cls_modname, str) and cls_modname:
# Again, try to find in sys.modules.
		mod = sys.modules.get(cls_modname, None)
		if isinstance(mod, ModuleType):
			return mod
# Again, try to import.
		try:
			mod = importlib.import_module(cls_modname)
		except Exception:
			return None
# Really a module? Then we're done.
		if isinstance(mod, ModuleType):
			return mod
	return None
	

def get_obj_name(obj: object) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| employ reasonable heuristics to extract a representative name.
			|Must| return string objects as-is.
			|Must| prioritize `__qualname__` over `__name__` for types/functions.
			|Must| resolve to the name of the underlying class for object instances.
			|Must| provide the string representation as a terminal fallback.
	Parameters:
		obj:
			The object to inspect.
	Returns:
		The resolved name according to the defined hierarchy.
	Raises:
	Notes:
		Last review:
			2026-02-04
	"""
	if isinstance(obj, str):
		return obj
# Prioritize __qualname__ (more descriptive for nested scopes)
	for attr in ("__qualname__", "__name__"):
		val = getattr(obj, attr, None)
		if isinstance(val, str):
			return val
# Resolve instance to class name, or use global fallback
	return getattr(type(obj), "__name__", str(obj))

def get_obj_fully_qualified_name(obj: object) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| return a fully qualified object name where possible.
			|Must| return module objects as their module name.
			|Must| return callable/class/object names as |mod|`<module>` . |lit|`<qualname>` when both parts are available.
			|Must| fall back to |func|`get_obj_name` if no module prefix can be determined.
			|Must| return input strings unchanged.
	Parameters:
		obj:
			The object to inspect.
	Returns:
		Best-effort fully qualified object name.
	Raises:
	"""
	if isinstance(obj, str):
		return obj
	if is_obj_module(obj):
		mod_name = getattr(obj, "__name__", None)
		if isinstance(mod_name, str) and mod_name:
			return mod_name
	name = get_obj_name(obj)
	mod_name = getattr(obj, "__module__", None)
	if isinstance(mod_name, str) and mod_name:
		return f"{mod_name}.{name}"
	return name

def get_obj_path(obj: object) -> str | None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| return an absolute filesystem path to the module that defines |var|`obj`, if determinable.
			|Must| return |None| if the path cannot be determined (e.g. builtins, C-extensions, interactive objects).
	Parameters:
		obj:
			The object whose defining module path is requested.
	Returns:
		Absolute path string or |None|.
	Raises:
	Notes:
		Last review:
			2026-02-05
	"""
	try:
		mod = inspect.getmodule(obj)
		if mod is None:
			return None
		path_any: Any = inspect.getsourcefile(mod) or getattr(mod, "__file__", None)
		if path_any is None:
			return None
		return os.path.abspath(str(path_any))
	except Exception:
		return None

def build_anchor(obj: object, kind: str | None = None) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| build a deterministic anchor string from an object.
			|Must| use the fully qualified name as source.
			|Must| encode each qualified-name segment as ``<len>:<segment>``.
			|Must| prefix the anchor by |lit|`wtrl-<kind>-`.
			|Must| infer kind as one of ``mod``, ``cls``, ``func``, ``obj`` if not passed explicitly.
	Parameters:
		obj:
			Object for which the anchor shall be generated.
		kind:
			Optional explicit kind tag.
	Returns:
		Deterministic anchor string suitable for doc-internal links.
	Raises:
	"""
	if kind is None:
		if is_obj_module(obj):
			kind = "mod"
		elif is_obj_class(obj):
			kind = "cls"
		elif is_obj_function(obj):
			kind = "func"
		else:
			kind = "obj"
	fqn = get_obj_fully_qualified_name(obj)
	segs = [s for s in fqn.split(".") if s]
	if not segs:
		return f"wtrl-{kind}"
	enc = "-".join(f"{len(s)}:{s}" for s in segs)
	return f"wtrl-{kind}-{enc}"

def get_func_obj_from_callable(obj : object) -> Callable[..., Any] | None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
		status:
			stable
	Contract:
		general:
			|Must| return the function object assigned to the object for a wide class of cases.
			|Must| handle functions in classes without decorators.
			|Must| handle functions in classes with decorator |attr|`@staticmethod`.
			|Must| handle functions in classes with decorator |attr|`@classmethod`.
			|Must| handle callable classes.
			|Must| handle instances of callable classes.
			|Must| handle functions at module level.
			|Must| handle generators.
			|Should| be able to handle built-ins.
	Parameters:
		obj:
			The object to analyze.
	Returns:
		The function object (or built-in) assigned to |var|`obj`.
	Raises:
	Notes:
		API:
			The signature is stable, but we might add cases to the implementation.
	"""
	if inspect.isfunction(obj):
		return obj
	else:
# If we don't check this function will diverge for "print".
		if inspect.isbuiltin(obj):
			return obj
		func = getattr(obj,"__func__",None)
		if func:
			return cast(Callable[..., Any],func)
# Handle callable of callable classes, bound and unbound.
		if hasattr(obj, "__call__"):
			if inspect.ismethod(obj.__call__):
				return obj.__call__.__func__
			elif inspect.isfunction(obj.__call__):
				return obj.__call__
	return None

def get_obj_docstring(obj: object) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| return the best available docstring text for |var|`obj`.
			|Must| prefer the raw source docstring obtained by |func|`get_source_docstring`.
			|Must| support modules, classes, functions/methods, descriptors (|type|`staticmethod`, |type|`classmethod`, |type|`property` / |type|`cached_property`), partial/partialmethod objects, and callable instances via |func|`__call__`.
			|Must| follow |type|`__wrapped__` chains created by |func|`functools.wraps`.
			|Must| return the empty string if no docstring is available.
	Parameters:
		obj:
			Any python object that might carry a docstring.
	Returns:
		|Must| return the best available docstring text, or the empty string if none exists.
	Raises:
	Notes:
		Last review:
			2026-05-15
		General:
			The object-level cache avoids repeating the wrapper walk for the same object.
	"""
	oid = id(obj)
	if oid in _OBJ_DOCSTRING_CACHE:
		return _OBJ_DOCSTRING_CACHE[oid]

	checked: set[int] = set()

	def _walk(o: object) -> str:
		oid = id(o)
		if oid in checked:
			return ""
		checked.add(oid)
		# 0) Prefer source docstring to preserve raw indentation in Python 3.13+.
		doc_src = get_source_docstring(o)
		if doc_src:
			return doc_src
		# 1) direct __doc__
		doc_attr = getattr(o, "__doc__", None)
		if isinstance(doc_attr, str):
			return doc_attr
		# 2) functools.wraps chain via __wrapped__
		wrapped = getattr(o, "__wrapped__", None)
		if wrapped is not None:
			res = _walk(wrapped)
			if res:
				return res
		# 3) descriptors: classmethod / staticmethod expose underlying function via __func__
		func = getattr(o, "__func__", None)
		if func is not None:
			res = _walk(func)
			if res:
				return res
		# 4) property / cached_property: docstring on fget
		if isinstance(o, property):
			if o.fget:
				res = _walk(o.fget)
				if res:
					return res
		# 5) functools.partial / partialmethod: underlying function in .func
		func2 = getattr(o, "func", None)
		if func2 is not None:
			res = _walk(func2)
			if res:
				return res
		# 6) callable instances would resolve to their __call__ implementation,
		# which is usually not the docstring we want to expose here.

		return ""
	doc = _walk(obj)
	_OBJ_DOCSTRING_CACHE[oid] = doc
	return doc

import inspect
from typing import Any
from types import ModuleType

def get_obj_annotations(obj: object) -> dict[str, Any]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build a |type|`dict` (the |dfn|`result`) as follows:
			|Must| analyse the object's annotations by means of |mod|`inspect`.
			On success, |must| add the annotations to the result.
			|Must| check for an attribute |value|`__type_params__` in the object.
			If it exists (as of Python 3.12), |must| iterate over the\
			|type|`tuple` |var|`obj.__type_params__` and add pairs\
			consisting of |var|`param.__name__` and |value|`type(param)` to the result.
	Parameters:
		obj:
			The object to be inspected.
	Returns:
		A |type|`dict` representing the object's annotations.
	Raises:
		BaseException:
			|May| propagate exceptions other than |type|`TypeError` and |type|`ValueError` from module |mod|`inspect`.
	"""
# 1. Classic annotations (variables, methods, etc.)
	try:
		results = dict(inspect.get_annotations(obj, eval_str=False)) if is_annotatable(obj) else {}
	except (TypeError, ValueError):
		results = {}
# 2. Python 3.12+ Type Aliases (PEP 695)
	if hasattr(obj, "__type_params__"):
		for param in obj.__type_params__:
			results[param.__name__] = type(param)
	return results


def get_obj_decorators(obj: object) -> List[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| return the decorator lines from the source text of a callable object, if available.
	Parameters:
		obj:
			The callable object whose decorator lines should be extracted.
	Returns:
		A list of source lines that start with |token|`@`.
	Raises:
	"""
	try:
		code = inspect.getsource(cast(Callable[...,Any],obj))
		return [line.strip() for line in code.splitlines() if line.strip().startswith('@')]
	except:
		return []

def gen_documentable_objects(obj: Documentable,config: ConfigTraversal = ConfigTraversal()) -> Generator[Documentable,None,None]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		public
Contract:
	general:
		|Must| create a generator object which allows depth-first tree traversal of objects in |var|`obj`.
		|Must| first yield object |var|`obj` itself.
		|Must| yield all objects and only objects which can have a docstring.
Parameters:
	obj:
		The object (module, class, function, method) to examine.
	config:
		Controls acceptance or refusal of objects during traversal.
Returns:
	|Must| return a Generator which yields objects from tree traversal of |var|`obj`
Raises:
	"""
	_seen: Set[Documentable] = set()
	def _iter(o: Documentable,seen: Set[Documentable]) -> Generator[Documentable,None,None]:
		if o in seen:
			return
# With the seen-mechanisms each direct yield must be paired with updating `seen`.
		seen.add(o)
		yield o
		if isinstance(o, ModuleType):
			# We're in a module. There might be classes and functions:
			for name, member in list(o.__dict__.items()):
				if name == "__annotate__" or name.startswith("__annotate"):
					continue
				if isinstance(member, ModuleType):
					# descend into submodules
					if not config.accept_imported_module(o,member):
						continue
					yield from _iter(member, seen)
				elif isinstance(member, type):
					# class
					if not config.accept_member_of_module(o,member):
						continue
					yield from _iter(member, seen)
				elif isinstance(member, FunctionType):
					# function
					if not config.accept_member_of_module(o,member):
						continue
					yield from _iter(member, seen)
				else:
					continue
			# Optionally walk package submodules on disk
			if config.include_imported() and config.walk_packages() and hasattr(o, "__path__"):
				for finder, mod_name, is_pkg in pkgutil.iter_modules(o.__path__, o.__name__ + "."):
					try:
						submod = importlib.import_module(mod_name)
					except Exception:
						continue
					yield from _iter(submod, seen)
		elif isinstance(o, type):
			# We're in a class. There might be classes, static functions, class methods and "normal" methods:
			for name, member in list(o.__dict__.items()):
				if name == "__annotate__" or name.startswith("__annotate") or getattr(member, "__name__", "") == "__annotate__":
					continue
				if isinstance(member, type):
					yield from _iter(member, seen)
				else:
					func_obj = get_func_obj_from_callable(member)
					if func_obj is None:
						continue
					yield from _iter(func_obj, seen)
		elif callable(o):
# Functions/methods are leaves for our traversal
			return
	yield from _iter(obj,_seen)
  
#===== Tracing ================================================#
class tracer:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types, Public_classes, Public_methods
	Terminology:
		rules on fail:
			Low-level functions may find a parsing or validation warning or error,
			but have no clue which rule has been violated. The |dfn|`rules on fail`
			mechanism allows the caller to pass the set of rules in question.
			The tracer provides a stack and api for these rule sets.
	Contract:
		general:
			|Must| provide a string-valued stack API for storing context data, like "which object/section/subsection are we in?".
			|Must| provide a to-string method for rendering the context.

			|Must| maintain a list of infos, where each entry is a tuple consisting of context, origin, and a free-form message.
			|Must| provide a method for adding such a info entry.
			|Must| allow to query if infos have been added.
			|Must| provide a method for clearing the list of infos.
			|Must| provide a method for rendering the list of infos as a string.
			|Must| provide a generator which allows iterating over the list of infos.

			|Must| maintain a list of warnings, where each entry is a tuple consisting of context, one Rule-ID, origin, a free-form message, and optional details.
			|Must| provide a method for adding such a warning entry.
			|Must| allow to query if warnings have been added.
			|Must| provide a method for clearing the list of warnings.
			|Must| provide a method for rendering the list of warnings as a string.
			|Must| provide a generator which allows iterating over the list of warnings.

			|Must| maintain a list of errors, where each entry is a tuple consisting of context, one Rule-ID, origin, a free-form message, and optional details.
			|Must| provide a method for adding such a error entry.
			|Must| allow to query if errors have been added.
			|Must| provide a method for clearing the list of errors.
			|Must| provide a method for rendering the list of errors as a string.
			|Must| provide a generator which allows iterating over the list of errors.

			|Must| manage a set of ignore-rule instructions

			|Must| provide a stack containing the current |dfn|`rule on fail` being validated against.
			|Must| provide an api like |func|`push...`, |func|`pop...`, |func|`get...` for the |dfn|`rule on fail` stack.

			|Must| provide a stack containing the current set of |dfn|`scopes` being validated against.
			|Must| provide an api like |func|`push...`, |func|`pop...`, |func|`get...` for the |dfn|`scopes` stack.
		constructor:
			|Must| be default-constructible.
	Public_types:
		Context:
			A list of strings built per context manager during parsing and validation.\
			Entries can be module, class or function names, or labels.
	Public_classes:
		Severity
	Class_overview:
		Severity:
			An enum with values DEBUG, INFO, WARNING, ERROR for filtering the output of the tracer.
	Public_methods:
		build_json
	Method_overview:
		build_json:
			Build a JSON-serializable |type|`dict` containing the
			information in the tracer, filtered by severity and optionally enriched by metadata.
	Notes:
		Last review:
			2026-06-21
		Parameter details:
			This details payload is important for the MCP server, because it gives the LLM enough debugging context to interpret tracer output and decide how to react to it.
			It usually is a dict with keys "found", "expected", and "hint"; "hint" typically contains a waterlint call for retrieving more information about the affected section or subsection.
	"""
	Context: TypeAlias = List[str]
	class Severity(IntEnum):
		r"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract
		Contract:
			general:
				|Must| define the following severity levels for filtering the tracer's output:
				- |value|`DEBUG`: for debugging notes, not relevant for end-users.
				- |value|`INFO`: for informational messages that are relevant for end-users but do not indicate any problems.
				- |value|`WARNING`: for potential issues that should be looked at but do not necessarily indicate a failure.
				- |value|`ERROR`: for definite problems that indicate a failure to meet a requirement or rule.
				|Must| assign integer values to these levels in increasing order of severity, starting with 0 for DEBUG.
			constructor:
				|Must| inherit from |type|`IntEnum`.
		"""
		DEBUG		= 0,
		INFO		= 1,
		WARNING		= 2
		ERROR		= 3

	def __init__(self) -> None:
		self._names : List[str] = []
# Debugging notes
		self._debug : List[Tuple[tracer.Context,Origin,str]] = []
# Infos
		self._infos : List[Tuple[tracer.Context,Origin,str]] = []
# This is a list of warnings, where each entry consists of a RuleID and a free-form text.
		self._warnings : List[Tuple[tracer.Context,RuleId,Origin,str,Details]] = []
		self._errors : List[Tuple[tracer.Context,RuleId,Origin,str,Details]] = []
# Rules to ignore
		self._ignrules : Set[str] = set()
# Rule in case a low-level function fails. We make sure there is always a rule
# so nothing will crash, but of course we don't want to see this one.
		self._rule_on_fail : List[RuleId] = ["YYY-999"]
# The scopes for validation. Successful validation requires that rules
# SCP-### are fulfilled. The default is a set with a single element CORE
		self._scopes : List[Scopes] = [set([Scope.CORE])]

	def __str__(self) -> str:
		return self.str_by_severity(self.Severity.DEBUG)
	def _format_diagnostic_details(self, details: Details) -> str:
		lines: list[str] = []
		label_color = "\x1b[38;2;119;119;119m"
		label_reset = "\x1b[0m"
		for key in ("found", "expected"):
			value = details.get(key)
			if isinstance(value, list) and value:
				lines.append(f"\t{label_color}{key}:{label_reset}")
				for line in value:
					if isinstance(line, str):
						lines.append(f"\t\t{line}")
		hint = details.get("hint")
		if isinstance(hint, str) and hint:
			lines.append(f"\t{label_color}hint:{label_reset}")
			lines.append(f"\t\t{hint}")
		elif isinstance(hint, list) and hint:
			lines.append(f"\t{label_color}hint:{label_reset}")
			for line in hint:
				if isinstance(line, str) and line:
					lines.append(f"\t\t{line}")
		return "".join(f"{line}\n" for line in lines)
	def _format_diagnostic_line(self, kind: str, origin: Origin, context: tracer.Context, rule_id: RuleId | None, msg: str, details: Details | None = None) -> str:
		color_map = {
			"Debug": "\x1b[35m",
			"Info": "\x1b[32m",
			"Warning": "\x1b[33m",
			"Error": "\x1b[31m",
		}
		color = color_map.get(kind, "\x1b[0m")
		head = f"- {color}{kind}\x1b[0m [{origin}] - [{'->'.join(context)}]"
		if rule_id is not None:
			head += f" [Rule {rule_id}]"
		head += f" {msg}\n"
		if isinstance(details, dict) and details:
			head += self._format_diagnostic_details(details)
		return head
# Refcopy debug, infos, warnings from tr to self.
# Refcopy errors from tr to self as warnings.
# We use this e.g. in waterlint render-json.
	def append_and_defuse(self,tr: tracer) -> None:
		for msg_dbg in tr._debug:
			self._debug.append(msg_dbg)
		for msg_inf in tr._infos:
			self._infos.append(msg_inf)
		for msg_wrn in tr._warnings:
			self._warnings.append(msg_wrn)
# Defusing: errors in tr become warnings in self.
		for msg_err in tr._errors:
			self._warnings.append(msg_err)
# For humans
	def str_by_severity(self,severity: Severity) -> str:
		t = ""
		t += "----- Tracer-----8<---------------------------------------------\n"
		if severity <= self.Severity.DEBUG:
			t += self.to_string_debug_notes()
		if severity <= self.Severity.INFO:
			t += self.to_string_infos()
		if severity <= self.Severity.WARNING:
			t += self.to_string_warnings()
		if severity <= self.Severity.ERROR:
			t += self.to_string_errors()
		t += "----- Tracer----->8---------------------------------------------\n"
		return t
	def build_json(
		self,
		severity: Severity,
		*,
		schema_version: str | None = None,
		waterloo_version: str | None = None,
		id_prefix: str | None = None,
		include_debug: bool = True,
	) -> dict[str, Any]:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| build a JSON-serializable |type|`dict` containing the tracer's data, following the WTRL Tracer JSON Schema.
				|Must| include entries up to the specified severity level.
				|Must| allow including debug notes optionally, as they may contain sensitive or verbose information.
				|Must| include schema version and optionally Waterloo version in the metadata section.
		Parameters:
			severity:
				Only include entries with this severity level or higher.
				Levels are ordered as DEBUG < INFO < WARNING < ERROR.
			schema_version:
				Specify the WTRL Tracer JSON Schema version to declare in the output. Defaults to the current version if not provided.
				This does not affect the structure of the output, which always follows the current schema.
				Including the schema version allows consumers to validate against the correct schema and maintain compatibility as the schema evolves.
				* |Must| be a string in the format |lit|`X.Y.Z` where X, Y, and Z are non-negative integers.
				* |Must| default to the current schema version if not provided.
				* |Must| be included in the output under the `__WTRL_VERSION__` metadata section.
				* |Must_not| affect the actual structure of the output, which always follows the current schema.
			waterloo_version:
				Optionally include the version of the Waterloo tool that generated the tracer data.
				* |Must| be a string in the format |lit|`X.Y.Z` where X, Y, and Z are non-negative integers.
			id_prefix:
				Optionally include a prefix for the `$id` field in the output JSON.
				* |Must| be a string if provided.
				* |May| be omitted, in which case the `$id` field will not include a prefix.
			include_debug:
				Optionally include debug notes in the output JSON.
		Returns:
			A JSON-serializable |type|`dict` containing the tracer's data structured according to the WTRL Tracer JSON Schema,
			including entries up to the specified severity level and metadata about the schema and optionally the Waterloo version.
			The return value |must| conform to JSON Schema :file:`wtrl-tracer-json-X.Y.Z.schema.json` where X.Y.Z is the declared schema version.
		Raises:
		"""
		def _lift_diagnostic_fields(entry: dict[str, Any], details: Details | None = None) -> Details:
			if not isinstance(details, dict):
				return {}
			details_payload = dict(details)
			for key in ("expected", "found", "hint"):
				if key in details_payload:
					entry[key] = details_payload.pop(key)
			return details_payload
		schema_version = WTRL_TRACER_JSON_SCHEMA_VERSION if schema_version is None else schema_version
		doc: dict[str, Any] = {
			"$schema": f"https://sci-d-vis.com/schema/wtrl-tracer-json-{schema_version}.schema.json",
			"__WTRL_VERSION__": {
				"schema": schema_version,
			},
			"__WTRL_INFO__": [],
			"__WTRL_WARNING__": [],
			"__WTRL_ERROR__": [],
		}
		if waterloo_version is not None:
			cast(dict[str, Any], doc["__WTRL_VERSION__"])["waterloo"] = waterloo_version
		if id_prefix is not None:
			doc["$id"] = f"{id_prefix}:{datetime.now().strftime('%Y%m%d%H%M%S')}"
		if include_debug and severity <= self.Severity.DEBUG:
			doc["__WTRL_DEBUG__"] = []
#----- Debug notes --------------------------------------------#
		if include_debug and severity <= self.Severity.DEBUG:
			for context,origin,msg in self.gen_debug_notes():
				dentry: dict[str, Any] = {"kind": "debug", "origin": origin, "msg": msg}
				dentry["context"] = context
				cast(list[dict[str, Any]], doc["__WTRL_DEBUG__"]).append(dentry)
#----- Infos --------------------------------------------------#
		if severity <= self.Severity.INFO:
			for context,origin,msg in self.gen_infos():
				entry: dict[str, Any] = {"kind": "info", "origin": origin, "msg": msg}
				entry["context"] = context
				cast(list[dict[str, Any]], doc["__WTRL_INFO__"]).append(entry)
#----- Warnings -----------------------------------------------#
		if severity <= self.Severity.WARNING:
			for context,rule_id,origin,msg,details in self.gen_warnings():
				entry = {"kind": "warning", "origin": origin, "rule-id": rule_id, "msg": msg}
				entry["context"] = context
				entry["details"] = _lift_diagnostic_fields(entry, details)
				cast(list[dict[str, Any]], doc["__WTRL_WARNING__"]).append(entry)
#----- Errors -------------------------------------------------#
		if severity <= self.Severity.ERROR:
			for context,rule_id,origin,msg,details in self.gen_errors():
				entry = {"kind": "error", "origin": origin, "rule-id": rule_id, "msg": msg}
				entry["context"] = context
				entry["details"] = _lift_diagnostic_fields(entry, details)
				cast(list[dict[str, Any]], doc["__WTRL_ERROR__"]).append(entry)
		return doc

#----- Context ------------------------------------------------#
	def push(self,name : str) -> None:
		self._names.append(name)
	def pop(self) -> str:
		name = self._names[-1]
		del self._names[-1]
		return name
	def has_top(self,name : str) -> bool:
		return self._names[-1] == name if len(self._names) > 0 else False
	def to_string(self) -> str:
		return "->".join(self._names)
#----- Debug --------------------------------------------------#
	def clear_debug_notes(self) -> None:
		self._debug = []
	def has_debug_notes(self) -> bool:
		return len(self._debug) > 0
	def add_debug_note(self,msg : str,origin: Origin = "tool") -> None:
		self._debug.append((copy.copy(self._names),origin,msg))
	def to_string_debug_notes(self) -> str:
		return "".join([self._format_diagnostic_line("Debug", origin, context, None, msg) for context,origin,msg in self._debug])
# Implement your own pretty printing.
	def gen_debug_notes(self) -> Generator[Tuple[tracer.Context,Origin,str],None,None]:
		for context,origin,msg in self._debug:
			yield context,origin,msg
#----- Infos --------------------------------------------------#
	def clear_infos(self) -> None:
		self._infos = []
	def has_infos(self) -> bool:
		return len(self._infos) > 0
	def add_info(self,msg : str,origin: Origin = "tool") -> None:
		self._infos.append((copy.copy(self._names),origin,msg))
	def to_string_infos(self) -> str:
		return "".join([self._format_diagnostic_line("Info", origin, context, None, msg) for context,origin,msg in self._infos])
# Implement your own pretty printing.
	def gen_infos(self) -> Generator[Tuple[tracer.Context,Origin,str],None,None]:
		for context,origin,msg in self._infos:
			yield context,origin,msg
#----- Warnings -----------------------------------------------#
	def clear_warnings(self) -> None:
		self._warnings = []
	def has_warnings(self) -> bool:
		return len(self._warnings) > 0
	def add_warning(self,rule_id : RuleId, origin: Origin, msg : str,/,details: Details | None = None) -> None:
		self._warnings.append((copy.copy(self._names),rule_id,origin,msg,details or {}))
	def to_string_warnings(self) -> str:
		return "".join([self._format_diagnostic_line("Warning", origin, context, rid, msg, details) for context,rid,origin,msg,details in self._warnings])
# Implement your own pretty printing.
	def gen_warnings(self) -> Generator[Tuple[tracer.Context,RuleId,Origin,str,Details],None,None]:
		for context,rid,origin,msg,details in self._warnings:
			yield context,rid,origin,msg,details
#----- Errors -------------------------------------------------#
	def clear_errors(self) -> None:
		self._errors = []
	def has_errors(self) -> bool:
		return len(self._errors) > 0
	def add_error(self,rule_id : RuleId, origin: Origin, msg : str,/,details: Details | None = None) -> None:
		self._errors.append((copy.copy(self._names),rule_id,origin,msg,details or {}))
	def to_string_errors(self) -> str:
		return "".join([self._format_diagnostic_line("Error", origin, context, rid, msg, details) for context,rid,origin,msg,details in self._errors])
# Implement your own pretty printing.
	def gen_errors(self) -> Generator[Tuple[tracer.Context,RuleId,Origin,str,Details],None,None]:
		for context,rid,origin,msg,details in self._errors:
			yield context,rid,origin,msg,details
#----- Ignores ------------------------------------------------#
	def clear_ignored(self) -> None:
		self._ignrules = set()
	def add_ignore_rule(self,rule : str) -> None:
		if not RE_RULE_ID_COMPILED.fullmatch(rule):
			raise RuntimeError(f"Bad rule specifier: expected 'ABC[D...]-123[4..]', got '{rule}'.")
		self._ignrules.add(rule)
	def should_ignore_rule(self,rule : str) -> bool:
		return rule in self._ignrules
	def gen_ignore_rules(self) -> Generator[str,None,None]:
		for rule in self._ignrules:
			yield rule
#----- Rules on fail ------------------------------------------#
	def clear_rule_on_fail(self) -> None:
		self._rule_on_fail = ["YYY-999"]
	def push_rule_on_fail(self,rule_id : RuleId) -> None:
		self._rule_on_fail.append(rule_id)
	def pop_rule_on_fail(self) -> None:
		del self._rule_on_fail[-1]
	def get_rule_on_fail(self) -> RuleId:
		return self._rule_on_fail[-1]
#----- Scopes -------------------------------------------------#
	def clear_scopes(self) -> None:
		self._scopes = []
	def push_scopes(self,scopes : Scopes) -> None:
		self._scopes.append(scopes)
	def pop_scopes(self) -> None:
		del self._scopes[-1]
	def get_scopes(self) -> Scopes:
		return self._scopes[-1]

@contextmanager
def traced_section(tr: tracer, name: str) -> Generator[None, None, None]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| temporarily push |var|`name` onto the tracer context unless it is already on top.
	Parameters:
		tr:
			The tracer whose context stack should be managed.
		name:
			The context name to push.
	Returns:
		A context manager yielding nothing.
	Raises:
	"""
	something_pushed = False
	if not tr.has_top(name):
		tr.push(name)
		something_pushed = True
	try:
		yield
	finally:
		if something_pushed:
			tr.pop()
@contextmanager
def rule_on_fail(tr: tracer, rule_id: RuleId) -> Generator[None, None, None]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| temporarily push the given rule identifier onto the tracer's rule-on-fail stack.
	Parameters:
		tr:
			The tracer whose failure-rule stack should be managed.
		rule_id:
			The rule identifier to push for the duration of the context.
	Returns:
		A context manager yielding nothing.
	Raises:
	"""
	tr.push_rule_on_fail(rule_id)
	try:
		yield
	finally:
		tr.pop_rule_on_fail()

#===== Exceptions =============================================#

class ParseError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class ValidationError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class SectionNotFoundError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class SubsectionNotFoundError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)
class NoContentError(RuntimeError):
	def __init__(self,msg : str) -> None:
		super().__init__(msg)

class ResolveObjectError(RuntimeError):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| be an exception class for errors during reference resolution.
		constructor:
			|Must| accept the following positional parameters:
			* |var|`ref`: the reference string that was attempted to resolve.
			* |var|`current_obj`: the object from which the reference was being resolved.
			* |var|`candidates`: an optional list of candidate strings that were considered during resolution.
			* |var|`last_candidate`: an optional string representing the last candidate that was attempted before failure.
			* |var|`last_error`: an optional exception representing the last error encountered during resolution attempts.
			* |var|`msg`: an optional custom error message. If not provided, a default message should be constructed using |var|`ref` and |var|`current_obj`.
	Notes:
		Callsites:
			Various waterlint components.
	"""
	def __init__(
		self,
		ref: str,
		current_obj: object,
		candidates: Sequence[str] | None = None,
		last_candidate: str | None = None,
		last_error: Exception | None = None,
		msg: str | None = None,
	) -> None:
		self.ref = ref
		self.current_obj = current_obj
		self.current_obj_name = get_obj_fully_qualified_name(current_obj) if current_obj is not None else "None"
		self.candidates = list(candidates or [])
		self.last_candidate = last_candidate
		self.last_error = last_error
		if msg is None:
			msg = f"Could not resolve reference '{ref}' from context '{self.current_obj_name}'."
		super().__init__(msg)

	def to_details(self) -> dict[str, Any]:
		found = [
			"Resolve_object:",
			f"\tref: {self.ref}",
			f"\tcontext: {self.current_obj_name}",
		]
		if self.last_candidate is not None:
			found.append(f"\tlast_candidate: {self.last_candidate}")
		if self.last_error is not None:
			last_error_txt = str(self.last_error)
			if last_error_txt.startswith("Could not resolve reference ") and "Last import failure while trying " in last_error_txt:
				last_error_txt = last_error_txt.split("Last import failure while trying ", 1)[1]
				last_error_txt = last_error_txt.split("': ", 1)[-1]
			found.append(f"\tlast_error: {last_error_txt}")
		details: dict[str, Any] = {
			"found": found,
			"expected": ["<check spelling, installation, or qualification>"],
			"hint": [
				"Check for a typo.",
				"Make sure the package is installed or importable.",
				"Qualify the reference with the correct module path.",
			],
		}
		return details

def raise_has_no_docstring(tr : tracer, rule_id: RuleId, obj : object) -> NoReturn:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| raise a parsing error that states that the object has no docstring.
	Parameters:
		tr:
			The tracer that should receive the error.
		rule_id:
			The rule identifier to report.
		obj:
			The object whose missing docstring should be reported.
	Returns:
		No return value.
	Raises:
		ParseError:
			Always raised.
	"""
	if is_obj_module(obj):
		categ = "module"
#		name = obj.__name__
	elif is_obj_class(obj):
		categ = "class"
#		name = obj.__class__.__name__
	elif is_obj_function(obj):
		categ = "function"
#		name = obj.__name__
	else:
		categ = "object"
#		name = "unknown"
	msg = f"{categ} has no docstring"
	tr.add_error(rule_id, "parsing", msg)
	raise ParseError(msg)

def raise_parsing_error(tr : tracer, rule_id: RuleId, msg : str, details: dict[str, Any] | None = None) -> NoReturn:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| raise a parsing error with the given message and optional diagnostic details.
	Parameters:
		tr:
			The tracer that should receive the error.
		rule_id:
			The rule identifier to report.
		msg:
			The parsing error message.
		details:
			Additional diagnostic details.
	Returns:
		No return value.
	Raises:
		ParseError:
			Always raised.
	"""
	out = msg
	tr.add_error(rule_id, "parsing", out, details)
	raise ParseError(out)

def raise_parsing_error_expected_but_got(tr : tracer, rule_id: RuleId, expected : str, got : str, details: dict[str, Any] | None = None) -> NoReturn:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| raise a parsing error that compares the expected and actual values.
	Parameters:
		tr:
			The tracer that should receive the error.
		rule_id:
			The rule identifier to report.
		expected:
			The expected textual value.
		got:
			The actual textual value.
		details:
			Optional diagnostic details to attach to the tracer error.
	Returns:
		No return value.
	Raises:
		ParseError:
			Always raised.
	"""
	out = f"expected {expected}, but got '{got}'"
	tr.add_error(rule_id, "parsing", out, details)
	raise ParseError(out)

def raise_parsing_error_invalid_label(tr : tracer, rule_id: RuleId,found : str,allowed : Iterable[str]) -> NoReturn:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| raise a parsing error that reports an invalid label and the allowed labels.
	Parameters:
		tr:
			The tracer that should receive the error.
		rule_id:
			The rule identifier to report.
		found:
			The invalid label that was found.
		allowed:
			The allowed label values.
	Returns:
		No return value.
	Raises:
		ParseError:
			Always raised.
	"""
	details : str = ""
	if found[-1] != ":":
		details = " (the colon seems to be missing)"
	out = f"'{found}' is not a valid label, allowed: {{{', '.join(allowed)}}}{details}"
	tr.add_error(rule_id, "parsing", out)
	raise ParseError(out)

def raise_validation_error(tr : tracer,obj: object, rule_id: RuleId, msg : str, details: dict[str, Any] | None = None) -> NoReturn:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| raise a validation error with the given message and optional diagnostic details.
	Parameters:
		tr:
			The tracer that should receive the error.
		obj:
			The object being validated.
		rule_id:
			The rule identifier to report.
		msg:
			The validation error message.
		details:
			Additional diagnostic details.
	Returns:
		No return value.
	Raises:
		ValidationError:
			Always raised.
	"""
	out = msg
	tr.add_error(rule_id, "validation", out, details)
	raise ValidationError(out)

def raise_validation_error_expected_but_got(tr : tracer,obj: object, rule_id: RuleId, expected : str, got : str) -> NoReturn:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| raise a validation error that compares the expected and actual values.
	Parameters:
		tr:
			The tracer that should receive the error.
		obj:
			The object being validated.
		rule_id:
			The rule identifier to report.
		expected:
			The expected textual value.
		got:
			The actual textual value.
	Returns:
		No return value.
	Raises:
		ValidationError:
			Always raised.
	"""
	out = f"expected {expected}, but got {got}"
	tr.add_error(rule_id, "validation", out)
	raise ParseError(out)


def warn_parsing(tr : tracer, rule_id: RuleId, msg : str) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| record a parsing warning unless the rule is ignored.
	Parameters:
		tr:
			The tracer that should receive the warning.
		rule_id:
			The rule identifier to report.
		msg:
			The warning message.
	Returns:
		No return value.
	Raises:
	"""
	if tr.should_ignore_rule(rule_id):
		return
	tr.add_warning(rule_id,"parsing",msg)

def warn_validation(tr: tracer, obj: object, rule_id: RuleId, msg: str, details: dict[str, Any] | None = None) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| record a validation warning unless the rule is ignored.
	Parameters:
		tr:
			The tracer that should receive the warning.
		obj:
			The object being validated.
		rule_id:
			The rule identifier to report.
		msg:
			The warning message.
		details:
			Optional structured diagnostics payload for the warning.
	Returns:
		No return value.
	Raises:
	"""
	if tr.should_ignore_rule(rule_id):
		return
	tr.add_warning(rule_id, "validation", msg, details)

#===== Self-test ==============================================#

if __name__ == "__main__":
	print("No self-test currently.")
