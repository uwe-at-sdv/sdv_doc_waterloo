from __future__ import annotations
from enum import Enum,IntEnum
from types import FunctionType, MappingProxyType, ModuleType
from typing_extensions import Self, TypeIs
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, Literal, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

import sys,re,os,copy
import pkgutil,inspect,importlib
import ast
import textwrap
import builtins
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

WTRL_TRACER_JSON_SCHEMA_VERSION = "0.0.2"

RE_RULE_ID : Final[str] = r"[A-Z][A-Z][A-Z]+-[0-9][0-9][0-9]+"
RE_RULE_ID_COMPILED : Final[re.Pattern[str]] = re.compile(RE_RULE_ID)

RE_IDENTIFIER : Final[str] = r"[A-Za-z_][A-Za-z0-9_]*"
RE_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_IDENTIFIER)

RE_QUALIFIED_IDENTIFIER : Final[str] = r"[A-Za-z_][A-Za-z0-9_]*([.][A-Za-z_][A-Za-z0-9_]*)*"
RE_QUALIFIED_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_QUALIFIED_IDENTIFIER)

RE_LABEL : Final[str] = RE_QUALIFIED_IDENTIFIER + ":"
RE_LABEL_COMPILED : Final[re.Pattern[str]] = re.compile(RE_LABEL)

# Required for Definitions
RE_CSV_IDENTIFIERS = r"[A-Za-z_][A-Za-z0-9_]*(\s*[,]\s*[A-Za-z_][A-Za-z0-9_]*)*"
RE_CSV_IDENTIFIERS_COMPILED = re.compile(RE_CSV_IDENTIFIERS)

# ANSI SGR escape sequences, e.g. "\x1b[31m"
RE_ANSI_SGR: Final[str] = r"\x1b\[[0-9;]*m"
RE_ANSI_SGR_COMPILED: Final[re.Pattern[str]] = re.compile(RE_ANSI_SGR)

# Markup tokens for Waterloo roles, e.g. |type|`int` -> :wtrl_type:`int`
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

_SOURCE_DOCSTRING_CACHE: Dict[int, str] = {}
AstDocNode: TypeAlias = Union[ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef]
# Per-module AST cache used to preserve raw docstring indentation and tabs.
_MODULE_AST_CACHE: WeakKeyDictionary[ModuleType, Tuple[str, ast.Module, Dict[str, list[AstDocNode]]]] = WeakKeyDictionary()
# Final docstring results are cached as well, because the wrapper walk is repeated often.
_OBJ_DOCSTRING_CACHE: Dict[int, str] = {}


def get_source_docstring(o: object) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Notes
	Contract:
		general:
			|Must| return a raw source docstring for |var|`o` if the defining source text can be obtained.
			|Must| support modules, classes, functions, methods, and routine-like objects for which source text is available.
			|Must| prefer the source docstring over any runtime |value|`__doc__` representation.
			|Must| cache the extracted result globally by object identity to avoid repeated source parsing.
			|Must| cache one parsed AST per module and reuse it for subsequent lookups.
			|Must| preserve original indentation and tabs in order to remain compatible with Waterloo parsing under Python 3.13+.
			|Should| fall back to a direct source snippet parse when the object is a decorated or wrapper-like callable
			that cannot be resolved reliably through the module AST.
			The AST-based source lookup is intentionally slower than direct runtime docstring access and is therefore
			implemented with caching as a first-order mitigation, not as a full performance optimization.
			|Must| return the empty string if no source docstring can be determined.
	Parameters:
		o:
			Any documentable object whose defining source docstring should be extracted.
	Returns:
		|Must| return the raw source docstring text, or the empty string if none is available.
	Notes:
		The helper uses a source-first strategy to preserve original indentation and tab characters in Python 3.13+.
		Docstrings are cached by object identity, while parsed module ASTs are cached separately by module object.
		The AST path is slower than runtime __doc__ access, but caching keeps the repeated cost manageable.
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

scope_tag_map = {
	"public": Scope.PUBLIC,
	"extension": Scope.EXTENSION,
	"core": Scope.CORE,
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

Scopes: TypeAlias = Set[int]

Documentable: TypeAlias = ModuleType | type[object] | Callable[..., Any]

def is_annotatable(obj: Any) -> TypeGuard[AnnotatableObject]:
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
	"""Return decorator lines for a callable object from its source text, if available."""
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
		Contract, Public_types
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

		|Must| maintain a list of infos, where each entry is a tuple consisting of list of Rule-IDs and a free-form message.
		|Must| provide a method for adding such a info entry.
		|Must| allow to query if infos have been added.
		|Must| provide a method for clearing the list of infos.
		|Must| provide a method for rendering the list of infos as a string.
		|Must| provide a generator which allows iterating over the list of infos.

		|Must| maintain a list of warnings, where each entry is a tuple consisting of one Rule-ID and a free-form message.
		|Must| provide a method for adding such a warning entry.
		|Must| allow to query if warnings have been added.
		|Must| provide a method for clearing the list of warnings.
		|Must| provide a method for rendering the list of warnings as a string.
		|Must| provide a generator which allows iterating over the list of warnings.

		|Must| maintain a list of errors, where each entry is a tuple consisting of one Rule-ID and a free-form message.
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
	"""
	Context: TypeAlias = List[str]
	class Severity(IntEnum):
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
		t = ""
		t += "Debug:\n" + self.to_string_debug_notes() + "\n"
		t += "Infos:\n" + self.to_string_infos() + "\n"
		t += "Warnings:\n" + self.to_string_warnings() + "\n"
		t += "Error:\n" + self.to_string_errors() + "\n"
		return t
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
	def build_json(self,severity: Severity) -> dict[str, Any]:
		doc: dict[str, Any] = {
			"$schema": f"https://sci-d-vis.com/schema/wtrl-tracer-json-{WTRL_TRACER_JSON_SCHEMA_VERSION}.schema.json",
#			"$id": f"urn:waterlint:{__version__}:diag:{datetime.now().strftime('%Y%m%d%H%M%S')}",
			"__WTRL_VERSION__": {
#				"waterloo": docitem.__version__,
				"schema": WTRL_TRACER_JSON_SCHEMA_VERSION,
			},
			"__WTRL_INFO__": [],
			"__WTRL_WARNING__": [],
			"__WTRL_ERROR__": [],
		}
		if severity <= self.Severity.DEBUG:
			doc["__WTRL_DEBUG__"] = []
#----- Debug notes --------------------------------------------#
		if severity <= self.Severity.DEBUG:
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
				entry["details"] = details
				cast(list[dict[str, Any]], doc["__WTRL_WARNING__"]).append(entry)
#----- Errors -------------------------------------------------#
		if severity <= self.Severity.ERROR:
			for context,rule_id,origin,msg,details in self.gen_errors():
				entry = {"kind": "error", "origin": origin, "rule-id": rule_id, "msg": msg}
				entry["context"] = context
				entry["details"] = details
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
		return "".join([f"- \x1b[35mDebug\x1b[0m [{origin}] - [{'->'.join(context)}] {msg}\n"  for context,origin,msg in self._debug])
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
		return "".join([f"- \x1b[32mInfo\x1b[0m [{origin}] - [{'->'.join(context)}] {msg}\n"  for context,origin,msg in self._infos])
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
		return "".join([f"- \x1b[33mWarning\x1b[0m [{origin}] - [{'->'.join(context)}] [Rule {rid}] {msg}\n"  for context,rid,origin,msg,details in self._warnings])
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
		return "".join([f"- \x1b[31mError\x1b[0m [{origin}] - [{'->'.join(context)}] [Rule {rid}] {msg}\n"  for context,rid,origin,msg,details in self._errors])
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

def raise_has_no_docstring(tr : tracer, rule_id: RuleId, obj : object) -> NoReturn:
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

def raise_parsing_error(tr : tracer, rule_id: RuleId, msg : str) -> NoReturn:
	out = msg
	tr.add_error(rule_id, "parsing", out)
	raise ParseError(out)

def raise_parsing_error_expected_but_got(tr : tracer, rule_id: RuleId, expected : str, got : str) -> NoReturn:
	out = f"expected {expected}, but got '{got}'"
	tr.add_error(rule_id, "parsing", out)
	raise ParseError(out)

def raise_parsing_error_invalid_label(tr : tracer, rule_id: RuleId,found : str,allowed : Iterable[str]) -> NoReturn:
	details : str = ""
	if found[-1] != ":":
		details = " (the colon seems to be missing)"
	out = f"'{found}' is not a valid label, allowed: {{{', '.join(allowed)}}}{details}"
	tr.add_error(rule_id, "parsing", out)
	raise ParseError(out)

def raise_validation_error(tr : tracer,obj: object, rule_id: RuleId, msg : str) -> NoReturn:
	out = msg
	tr.add_error(rule_id, "validation", out)
	raise ValidationError(out)

def raise_validation_error_expected_but_got(tr : tracer,obj: object, rule_id: RuleId, expected : str, got : str) -> NoReturn:
	out = f"expected {expected}, but got {got}"
	tr.add_error(rule_id, "validation", out)
	raise ParseError(out)


def warn_parsing(tr : tracer, rule_id: RuleId, msg : str) -> None:
	if tr.should_ignore_rule(rule_id):
		return
	tr.add_warning(rule_id,"parsing",msg)

"""
Record a validation warning without raising.
"""
def warn_validation(tr: tracer, obj: object, rule_id: RuleId, msg: str) -> None:
	if tr.should_ignore_rule(rule_id):
		return
	tr.add_warning(rule_id, "validation", msg)

#===== Self-test ==============================================#

if __name__ == "__main__":
	print("No self-test currently.")
