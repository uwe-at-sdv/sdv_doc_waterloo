from __future__ import annotations
from typing import Any, Callable, Dict, Final, Mapping, TYPE_CHECKING, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, Literal, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypedDict, TypeGuard, Union, cast
from types import FunctionType, MappingProxyType, MethodType, ModuleType
from enum import Enum, IntEnum

import re

try:
	from enum import StrEnum # type: ignore[attr-defined]
except ImportError:
	class StrEnum(str, Enum): # type: ignore[no-redef]
		pass

# A single string can be a docstring subtree.
DocstringSubtree: TypeAlias = Union[str, List["DocstringSubtree"]]

# A docstring tree is always a list.
DocstringTree: TypeAlias = List[DocstringSubtree]

AnnotatableObject: TypeAlias = Union[type, ModuleType, FunctionType, MethodType]

RuleId: TypeAlias = str
Origin: TypeAlias = Literal["parsing", "validation", "tool", "extension"]
Details: TypeAlias = Dict[str,str | list[str]]

Documentable: TypeAlias = ModuleType | type[object] | Callable[..., Any]

# Scope values
class Scope(IntEnum):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants, Derived_from
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing available scopes.
			|Must| provide a time-stable partial order for the constants.
		constructor:
			Inherit from |type|`int`.
	Derived_from:
		IntEnum
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

Scopes: TypeAlias = Set[Scope]

# Documentation profiles and anchor infixes.
Profile: TypeAlias = Literal["module", "class", "function", "method", "inherited_method"]
Profile_t: TypeAlias = Profile
AnchorKind_t: TypeAlias = Literal["mod", "cls", "func", "obj"]


class Trait(StrEnum):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants, Derived_from
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing the traits of a class.
		constructor:
			Inherit from |type|`StrEnum`.
	Derived_from:
		StrEnum
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
	"final": Trait.FINAL,
	}
TRAIT_TAG_MAP: Final[Mapping[str, Trait]] = cast(Mapping[str, Trait], MappingProxyType(trait_tag_map))


class Flavour(IntEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants, Derived_from
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing available flavours for rendering Normativity Keywords.
		constructor:
			Inherit from |type|`int`.
	Derived_from:
		IntEnum
	Public_constants:
		RAW:
			Example: | + Must + |
		RFC_2119:
			Example: |lit|`MUST`
		MARKDOWN:
			Example: |lit|`**MUST**`
	"""
	RAW = 0
	RFC_2119 = 1
	MARKDOWN = 2


flavour_tag_map: Final[Mapping[str, Flavour]] = MappingProxyType({
	"raw": Flavour.RAW,
	"rfc-2119": Flavour.RFC_2119,
	"markdown": Flavour.MARKDOWN,
	})
FLAVOUR_TAG_MAP: Final[Mapping[str, Flavour]] = flavour_tag_map


class Format(IntEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants, Derived_from
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing available output formats for string rendering.
		constructor:
			Inherit from |type|`int`.
	Derived_from:
		IntEnum
	Public_constants:
		JSON:
			Javascript Object Notation
		MD:
			Markdown.
	"""
	JSON = 0
	MD = 1


format_tag_map: Final[Mapping[str, Format]] = MappingProxyType({
	"json": Format.JSON,
	"md": Format.MD,
	})
FORMAT_TAG_MAP: Final[Mapping[str, Format]] = format_tag_map


class Status(StrEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants, Derived_from
		scope:
			public
	Contract:
		general:
			|Must| provide constants representing the values of subsection |label|`Preamble.status`.
		constructor:
			Inherit from |type|`StrEnum`.
	Derived_from:
		StrEnum
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
	EXPERIMENTAL = "experimental"
	STABLE = "stable"
	FROZEN = "frozen"
	DEPRECATED = "deprecated"
	DRAFT = "draft"


status_tag_map = {
	"experimental": Status.EXPERIMENTAL,
	"stable": Status.STABLE,
	"frozen": Status.FROZEN,
	"deprecated": Status.DEPRECATED,
	"draft": Status.DRAFT,
	}
STATUS_TAG_MAP: Final[Mapping[str, Status]] = cast(Mapping[str, Status], MappingProxyType(status_tag_map))


# These axes describe semantic status and applicability in the documentation rules.
Normativity_t: TypeAlias = Literal["not_applicable", "normative", "informative", "can_be_both"]
MustExist_t: TypeAlias = Literal["yes", "no", "depends_on_context"]
LabelKind_t: TypeAlias = Literal["FIXED", "IDENTIFIER", "QUALIFIED_IDENTIFIER", "LIST_OF_IDENTIFIERS", "ANY_STRING"]
SectionBodyCategory_t: TypeAlias = Literal[
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

# Keep the canonical tokens in the helper layer: parsing, validation, and
# Authoring JSON all need the same definition of an explicit normative claim.
KEYWORDS_OF_NORMATIVITY: Final[tuple[str, ...]] = (
	"|must|",
	"|Must|",
	"|must_not|",
	"|Must_not|",
	"|should|",
	"|Should|",
	"|should_not|",
	"|Should_not|",
	"|may|",
	"|May|",
)

#CSV_SECTIONS = frozenset(["normative_sections", "scopes", "Public_classes", "Public_methods", "Public_functions", "See_also"])
SINGLE_STRING_SECTIONS = frozenset(["profile","status"])

# ANSI SGR escape sequences, e.g. "\x1b[31m"
RE_ANSI_SGR: Final[str] = r"\x1b\[[0-9;]*m"
RE_ANSI_SGR_COMPILED: Final[re.Pattern[str]] = re.compile(RE_ANSI_SGR)

# Markup tokens for Waterloo roles, e.g. |type|`int` -> :wtrl_type:`int`
# Single Source of Truth is the documentation standard.
WTRL_MARKUP_ROLES: Final[str] = r"(attr|cmd|class|dfn|file|func|key|label|lit|mod|norm|op|opt|pkg|ref|tag|term|type|url|value|var|var_type)"
RE_WTRL_MARKUP_BACKTICK: Final[str] = rf"\|{WTRL_MARKUP_ROLES}\|`([^`]+)`"
RE_WTRL_MARKUP_BACKTICK_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_MARKUP_BACKTICK)

# References consist of two parts: clear text and <link>.
RE_WTRL_ANGLE_HTTPS_REF: Final[str] = r"^\s*([^<>`]+?)\s*<\s*(https?://[^>\s]+)\s*>\s*$"
RE_WTRL_ANGLE_HTTPS_REF_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_ANGLE_HTTPS_REF)

RE_WTRL_ANGLE_WTRL_REF: Final[str] = r"^\s*([^<>`]+?)\s*<\s*(wtrl://[^>\s]+)\s*>\s*$"
RE_WTRL_ANGLE_WTRL_REF_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_ANGLE_WTRL_REF)

#RE_SUSPICIOUS_MARKUP_BACKTICK: Final[str] = rf"\|[a-zA-Z0-9_]+\|`"
#RE_SUSPICIOUS_MARKUP_BACKTICK_COMPILED: Final[re.Pattern[str]] = re.compile(RE_SUSPICIOUS_MARKUP_BACKTICK)

RE_WTRL_JSON_SCHEMA_NAME: Final[str] = r"^wtrl-[a-zA-Z\-_]*-[0-9+]\.[0-9+]\.[0-9+]\.schema\.json$"
RE_WTRL_JSON_SCHEMA_NAME_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_JSON_SCHEMA_NAME)
