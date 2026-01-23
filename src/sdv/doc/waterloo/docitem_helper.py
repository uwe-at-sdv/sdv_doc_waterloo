import sys,re
import inspect
import importlib
import builtins
from types import FunctionType, ModuleType
from contextlib import contextmanager
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union

#===== Constants ==============================================#

RE_RULE_ID : Final[str] = r"[A-Z][A-Z][A-Z]+-[0-9][0-9][0-9]+"
RE_RULE_ID_COMPILED : Final[re.Pattern[str]] = re.compile(RE_RULE_ID)

#===== Typechecking ===========================================#

docstring_tree: TypeAlias = List[Union[str , "docstring_tree"]]
docstring_subtree: TypeAlias = Union[str, List["docstring_subtree"]]

AnnotatedObject = Union[type, ModuleType]
RuleSet = Sequence[str]

def is_annotated(obj : AnnotatedObject, attr_name: str) -> bool:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| find out whether the attribute passed is annotated.
Parameters:
	obj:
		The class or module containing the attribute.
	attr_name:
		The name of the attribute to be tested.
Returns:
	|Must| return |True| if the attribute is annotated, else |False|.
Raises:
	BaseException:
		|May| propagate exceptions from :wtrl_func:`getattr`.
	"""
	local_annotations = getattr(obj, "__annotations__", {})
	return attr_name in local_annotations

def is_final(obj : AnnotatedObject, attr_name: str) -> bool:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| find out whether the attribute passed is annotated as :wtrl_type:`Final`.
Parameters:
	obj:
		The class or module containing the attribute.
	attr_name:
		The name of the attribute to be tested.
Returns:
	|Must| return |True| if the attribute is annotated as :wtrl_type:`Final`, else |False|.
Raises:
	BaseException:
		|May| propagate exceptions from :wtrl_func:`get_type_hints`.
	"""
# Get type annotations
	hints = get_type_hints(obj, include_extras=True)
	hint = hints.get(attr_name)
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

def get_obj_name(obj: object) -> str:
	if isinstance(obj, str):
		return obj
	if hasattr(obj, "__name__"):
		name_attr = getattr(obj, "__name__")
		return name_attr if isinstance(name_attr, str) else str(name_attr)
	return str(obj)

def get_func_obj_from_callable(member : object) -> Callable[..., Any] | None:
	if inspect.isfunction(member):
		return member
	elif isinstance(member, staticmethod):
		return member.__func__
	elif isinstance(member, classmethod):
		return member.__func__
	else:
		return None

def has_docstring(obj: ModuleType | type[object] | Callable[..., Any]) -> bool:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| check attribute ``__doc__`` of :wtrl_var:`obj`.
Parameters:
	obj:
		The object (module, class, function, method) to examine.
Returns:
	|Must| return |True| if :wtrl_var:`obj` has a docstring, else |must| return |False|.
Raises:
	"""
	return True if getattr(obj, "__doc__",None) else False

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
		but have no clue which rule has been violated. The :wtrl_dfn:`rules on fail`
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

		|Must| provide a stack containing the current set of :wtrl_dfn:`rules on fail` being validated against.
		|Must| provide an api like :wtrl_func:`push...`, :wtrl_func:`pop...`, :wtrl_func:`get...` for the :wtrl_dfn:`rules on fail` stack.
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
	if inspect.isclass(obj):
		categ = "class"
#		name = obj.__class__.__name__
	elif inspect.ismodule(obj):
		categ = "module"
#		name = obj.__name__
	elif inspect.isfunction(obj):
		categ = "function"
#		name = obj.__name__
	elif inspect.ismethod(obj):
		categ = "method"
#		name = obj.__name__
	else:
		categ = "object"
#		name = "unknown"
	msg = f"[Parsing] from '{tr.to_string()}': {categ} has no docstring"
	tr.add_error(rule_ids, msg)
	raise RuntimeError(msg)

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


if __name__ == "__main__":
	tr = tracer()
	tr.add_ignore_rule("RULE-123")
	tr.add_ignore_rule("RULE-456")
	for rule in tr.gen_ignore_rules():
		print("IGNORE_RULE:",rule)
	print(tr.should_ignore_rule("RULE-456"))
	print(tr.should_ignore_rule("RULE-789"))
