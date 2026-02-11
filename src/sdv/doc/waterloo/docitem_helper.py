from __future__ import annotations
from enum import IntEnum
from types import FunctionType, MappingProxyType, ModuleType
from typing_extensions import Self, TypeIs
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

import sys,re,os
import inspect
import importlib
import builtins
from contextlib import contextmanager

#===== Constants ==============================================#

RE_RULE_ID : Final[str] = r"[A-Z][A-Z][A-Z]+-[0-9][0-9][0-9]+"
RE_RULE_ID_COMPILED : Final[re.Pattern[str]] = re.compile(RE_RULE_ID)

RE_IDENTIFIER : Final[str] = r"[A-Za-z_][A-Za-z0-9_]*"
RE_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_IDENTIFIER)

RE_QUALIFIED_IDENTIFIER : Final[str] = r"[A-Za-z_.][A-Za-z0-9_.]*"
RE_QUALIFIED_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_QUALIFIED_IDENTIFIER)

RE_LABEL : Final[str] = RE_QUALIFIED_IDENTIFIER + ":"
RE_LABEL_COMPILED : Final[re.Pattern[str]] = re.compile(RE_LABEL)

# Markup tokens for Waterloo roles, e.g. |type|`int` -> :wtrl_type:`int`
WTRL_MARKUP_ROLES: Final[str] = r"(attr|cmd|dfn|file|func|label|lit|mod|norm|op|opt|tag|term|type|value|var|var_type)"
RE_WTRL_MARKUP_BACKTICK: Final[str] = rf"\|{WTRL_MARKUP_ROLES}\|`([^`]+)`"
RE_WTRL_MARKUP_BACKTICK_COMPILED: Final[re.Pattern[str]] = re.compile(RE_WTRL_MARKUP_BACKTICK)

#RE_SUSPICIOUS_MARKUP_BACKTICK: Final[str] = rf"\|[a-zA-Z0-9_]+\|`"
#RE_SUSPICIOUS_MARKUP_BACKTICK_COMPILED: Final[re.Pattern[str]] = re.compile(RE_SUSPICIOUS_MARKUP_BACKTICK)

CSV_SECTIONS = frozenset(["normative_sections", "scopes", "Public_classes", "Public_methods", "Public_functions", "See_also"])
SINGLE_STRING_SECTIONS = frozenset(["profile","status"])


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
	PUBLIC		= 0
	EXTENSION	= 1
	CORE		= 2

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
			Example: \|Must\|
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
			|Must| provide constant representing available output formats for string rendering.
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

#===== Typechecking ===========================================#

docstring_tree: TypeAlias = List[Union[str , "docstring_tree"]]
docstring_subtree: TypeAlias = Union[str, List["docstring_subtree"]]

AnnotatedObject_t = Union[type, ModuleType]
RuleSet = Sequence[str]

Scopes_t : TypeAlias = Set[int]

Documentable_t = ModuleType | type[object] | Callable[..., Any]

def is_attr_annotated(obj : AnnotatedObject_t, attr: str) -> bool:
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
		Drift:
			Last reviewed on 2026-02-04
	"""
	local_annotations = getattr(obj, "__annotations__", {})
	return attr in local_annotations

def is_attr_final(obj : AnnotatedObject_t, attr: str) -> bool:
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
		Drift:
			Last reviewed on 2026-02-04
	"""
# Get type annotations
	hints = get_type_hints(obj, include_extras=True)
	hint = hints.get(attr)
# Is final or not
	return get_origin(hint) is Final

def returns_bool(obj : object) -> bool:
	if obj is bool:
		return True
	origin = get_origin(obj)
	if origin is None:
		return False
	args = get_args(obj)
	return bool(args) and any(a is bool for a in args)

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


def get_obj_name(obj: object) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
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
		Drift:
			Last reviewed on 2026-02-04
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
		Drift:
			Last reviewed on 2026-02-05
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
			|Must| return the docstring text for |var|`obj` if one is present.
			|Must| support modules, classes, functions/methods, descriptors (|type|`staticmethod`, |type|`classmethod`, |type|`property` / |type|`cached_property`), partial/partialmethod objects, and callable instances via |func|`__call__`.
			|Must| follow |type|`__wrapped__` chains created by |func|`functools.wraps`.
			|Must| return the empty string if no docstring is available.
	Parameters:
		obj:
			Any python object that might carry a docstring.
	Returns:
		|Must| return the docstring text, or empty string if none exists.
	Raises:
	Notes:
		Drift:
			Last reviewed on 2026-02-04
	"""
	checked: set[int] = set()

	def _walk(o: object) -> str:
		oid = id(o)
		if oid in checked:
			return ""
		checked.add(oid)
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
# This one delivers stuff like "Call self as a function", which we don't want.
# 6) callable instances: look at __call__
#		call = getattr(o, "__call__", None)
#		if call is not None and call is not o:
#			res = _walk(call)
#			if res:
#				return res

		return ""
	return _walk(obj)

#===== Tracing ================================================#
class tracer:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
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

		|Must| maintain a list of warnings, where each entry is a tuple consisting of list of Rule-IDs and a free-form message.
		|Must| provide a method for adding such a warning entry.
		|Must| allow to query if warnings have been added.
		|Must| provide a method for clearing the list of warnings.
		|Must| provide a method for rendering the list of warnings as a string.
		|Must| provide a generator which allows iterating over the list of warnings.

		|Must| maintain a list of errors, where each entry is a tuple consisting of list of Rule-IDs and a free-form message.
		|Must| provide a method for adding such a error entry.
		|Must| allow to query if errors have been added.
		|Must| provide a method for clearing the list of errors.
		|Must| provide a method for rendering the list of errors as a string.
		|Must| provide a generator which allows iterating over the list of errors.

		|Must| manage a set of ignore-rule instructions

		|Must| provide a stack containing the current set of |dfn|`rules on fail` being validated against.
		|Must| provide an api like |func|`push...`, |func|`pop...`, |func|`get...` for the |dfn|`rules on fail` stack.

		|Must| provide a stack containing the current set of |dfn|`scopes` being validated against.
		|Must| provide an api like |func|`push...`, |func|`pop...`, |func|`get...` for the |dfn|`scopes` stack.
	constructor:
		|Must| be default-constructible.
	"""
	def __init__(self) -> None:
		self._names : List[str] = []
# Infos are for debugging
		self._infos : List[str] = []
# This is a list of warnings, where each entry consists of a list of RuleIDs and a free-form text.
		self._warnings : List[Tuple[Sequence[str],str]] = []
		self._errors : List[Tuple[Sequence[str],str]] = []
# Rules to ignore
		self._ignrules : Set[str] = set()
# Rules in case a low-level function fails. We make sure there is always a set of rules
# so nothing will crash, but of course we don't want to see this one.
		self._rules_on_fail : List[RuleSet] = [["YYY-999"]]
# The scopes for validation. Successful validation requires that rules
# SCP-### are fulfilled. The default is a set with a single element CORE
		self._scopes : List[Scopes_t] = [set([Scope.CORE])]

	def __str__(self) -> str:
		t = ""
		t += "Infos:\n" + self.to_string_infos() + "\n"
		t += "Warnings:\n" + self.to_string_warnings() + "\n"
		t += "Error:\n" + self.to_string_errors() + "\n"
		return t
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
#----- Infos --------------------------------------------------#
	def clear_infos(self) -> None:
		self._infos = []
	def has_infos(self) -> bool:
		return len(self._infos) > 0
	def add_info(self,msg : str) -> None:
		self._infos.append(msg)
	def to_string_infos(self) -> str:
		return "\n".join([f"{msg}" for msg in self._infos])
# Implement your own pretty printing.
	def gen_infos(self) -> Generator[str,None,None]:
		for msg in self._infos:
			yield msg
#----- Warnings -----------------------------------------------#
	def clear_warnings(self) -> None:
		self._warnings = []
	def has_warnings(self) -> bool:
		return len(self._warnings) > 0
	def add_warning(self,rule_ids : Sequence[str], msg : str) -> None:
		self._warnings.append((rule_ids,msg))
	def to_string_warnings(self) -> str:
		return "\n".join([f"[Rule {','.join(rid)}] {msg}"  for rid,msg in self._warnings])
# Implement your own pretty printing.
	def gen_warnings(self) -> Generator[Tuple[Sequence[str],str],None,None]:
		for rids,msg in self._warnings:
			yield rids,msg
#----- Errors -------------------------------------------------#
	def clear_errors(self) -> None:
		self._errors = []
	def has_errors(self) -> bool:
		return len(self._errors) > 0
	def add_error(self,rule_ids : Sequence[str], msg : str) -> None:
		self._errors.append((rule_ids,msg))
	def to_string_errors(self) -> str:
		return "\n".join([f"[Rule {','.join(rid)}] {msg}"  for rid,msg in self._errors])
# Implement your own pretty printing.
	def gen_errors(self) -> Generator[Tuple[Sequence[str],str],None,None]:
		for rids,msg in self._errors:
			yield rids,msg
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
	def clear_rules_on_fail(self) -> None:
		self._rules_on_fail = [["YYY-999"]]
	def push_rules_on_fail(self,rule_ids : RuleSet) -> None:
		self._rules_on_fail.append(rule_ids)
	def pop_rules_on_fail(self) -> None:
		del self._rules_on_fail[-1]
	def get_rules_on_fail(self) -> RuleSet:
		return self._rules_on_fail[-1]
#----- Scopes -------------------------------------------------#
	def clear_scopes(self) -> None:
		self._scopes = []
	def push_scopes(self,scopes : Scopes_t) -> None:
		self._scopes.append(scopes)
	def pop_scopes(self) -> None:
		del self._scopes[-1]
	def get_scopes(self) -> Scopes_t:
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
def rules_on_fail(tr: tracer, rule_ids: RuleSet) -> Generator[None, None, None]:
	tr.push_rules_on_fail(rule_ids)
	try:
		yield
	finally:
		tr.pop_rules_on_fail()

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

def raise_has_no_docstring(tr : tracer, rule_ids: Sequence[str], obj : object) -> NoReturn:
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
	msg = f"[Parsing] from '{tr.to_string()}': {categ} has no docstring"
	tr.add_error(rule_ids, msg)
	raise ParseError(msg)

def raise_parsing_error(tr : tracer, rule_ids: Sequence[str], msg : str) -> NoReturn:
	out = f"[Parsing] from '{tr.to_string()}': {msg}"
	tr.add_error(rule_ids, out)
	raise ParseError(out)

def raise_parsing_error_expected_but_got(tr : tracer, rule_ids: Sequence[str], expected : str, got : str) -> NoReturn:
	out = f"[Parsing] from '{tr.to_string()}': expected {expected}, but got {got}"
	tr.add_error(rule_ids, out)
	raise ParseError(out)

def raise_parsing_error_invalid_label(tr : tracer, rule_ids: Sequence[str],found : str,allowed : Iterable[str]) -> NoReturn:
	details : str = ""
	if found[-1] != ":":
		details = " (the colon seems to be missing)"
	out = f"[Parsing] from '{tr.to_string()}': '{found}' is not a valid label, allowed: {{{', '.join(allowed)}}}{details}"
	tr.add_error(rule_ids, out)
	raise ParseError(out)

def raise_validation_error(tr : tracer,obj: object, rule_ids: Sequence[str], msg : str) -> NoReturn:
	out = f"[Validation] from '{tr.to_string()}': {msg}"
	tr.add_error(rule_ids, out)
	raise ValidationError(out)

def raise_validation_error_expected_but_got(tr : tracer,obj: object, rule_ids: Sequence[str], expected : str, got : str) -> NoReturn:
	out = f"[Validation] from '{tr.to_string()}': expected {expected}, but got {got}"
	tr.add_error(rule_ids, out)
	raise ParseError(out)


def warn_parsing(tr : tracer, rule_ids: Sequence[str], msg : str) -> None:
	if rule_ids and all(tr.should_ignore_rule(rid) for rid in rule_ids):
		return
	rule_txt = ""
	if rule_ids:
		rule_txt = f"[Rules: {', '.join(rule_ids)}] "
	tr.add_warning(rule_ids, f"from '{tr.to_string()}': {msg}")

"""
Record a validation warning without raising.
"""
def warn_validation(tr: tracer, obj: object, rule_ids: Sequence[str], msg: str) -> None:
# If all rule_ids are ignored, skip recording the warning.
	if rule_ids and all(tr.should_ignore_rule(rid) for rid in rule_ids):
		return
	name = get_obj_name(obj)
	rule_txt = ""
	if rule_ids:
		rule_txt = f"[Rules: {', '.join(rule_ids)}] "
	tr.add_warning(rule_ids, f"from '{tr.to_string()}': In object '{name}': {msg}")

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
	"""
	def __init__(self) -> None:
		self._include_imported = False
		self._walk_packages = False
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
	def is_member_in_module(self,obj_parent: ModuleType | None,member: Documentable_t) -> bool:
		if obj_parent == None:
			return True
		return getattr(member, "__module__", None) == obj_parent.__name__
# False means: keep traversal within the module's own namespace
	def accept_imported_module(self,obj_parent: ModuleType,member: ModuleType) -> bool:
		return self.include_imported() or member.__name__.startswith(obj_parent.__name__ + ".")
	def accept_member_of_module(self,obj_parent: ModuleType,member: Documentable_t) -> bool:
		return self.include_imported() or self.is_member_in_module(obj_parent,member)

#===== Self-test ==============================================#

if __name__ == "__main__":
	print("No self-test currently.")
