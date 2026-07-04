"""
Preamble:
	profile:
		module
	normative_sections:
		Contract,
		Public_classes,
		Public_functions
Description:
	This module provides the Sphinx integration layer for the Waterloo documentation system.
	|
	The implementation operates directly on Docutils nodes and defines custom Docutils roles
	to generate structured documentation output from Waterloo-style docstrings.
	|
	Sphinx is used as the execution and rendering framework, but the internal data model is based
	on the Docutils abstract syntax tree (AST). All document structure, including sections,
	tables, lists, rubrics, and inline markup, is represented using Docutils node classes.
	|
	The module introduces a configurable |type|`context` object which encapsulates all
	project-specific presentation logic, including role expansion, symbol rendering, and
	HTML layout decisions. This context is configured by the target project via its
	|file|`conf.py` and is intentionally decoupled from the core implementation.
	|
	To support concise and unambiguous normative documentation, the module maintains explicit
	scope stacks with the semantics "current module" and "current class". These scopes define
	the implicit ownership of subsequently documented functions and methods and are modified
	using dedicated Docutils roles or directives.
	|
	The primary goal of this module is correctness, completeness, and reproducibility of
	normative documentation. Readability and visual presentation are considered secondary
	and are handled through configurable rendering layers.
Terminology:
	Docutils node:
		An element of the Docutils abstract syntax tree (AST),
		such as |type|`paragraph`, |type|`section`, or |type|`literal`.
	Docutils role:
		An inline markup construct of the form ``:role:`content``` implemented
		using the Docutils role API. Custom roles provided by this module are
		registered via Sphinx but conceptually belong to Docutils.
	Sphinx extension:
		A Python module loaded by Sphinx to extend its parsing, transformation,
		or rendering behavior. This module is implemented as a Sphinx extension
		but operates primarily on Docutils data structures.
Contract:
	general:
		|Must| provide classes and functions for buidling Docutils nodes from docstring trees.
		|Must| provide a default layout for HTML output from Sphinx.
		|Must| provide a class |type|`context` which provides abstract roles to be configured by the target project's |file|`conf.py`.
		|Must| provide a function for building Docutils nodes from a module docstring in waterloo format.
		|Must| provide a function for building Docutils nodes from a function docstring in waterloo format.
		|Must| provide a function for building Docutils nodes from a class docstring in waterloo format.
		|Must| provide a function for building Docutils nodes from a class docstring and the class' method docstrings in waterloo format.
		|Must| provide a Docutils role for rendering a function prototype.
		|Must| provide a Docutils role for rendering a method prototype.
		|Must| maintain a stack with semantics "current module" and |func|`push`-, |func|`pop`-, |func|`get`-methods.
		|Must| maintain a stack with semantics "current class" and |func|`push`-, |func|`pop`-, |func|`get`-methods.
		|Must| provide Docutils roles or directives for modifying these stacks.
Public_classes:
	context
Class_overview:
	context:
		Internal class, please ignore
Public_functions:
	build_sphinx_nodes,
	build_sphinx_nodes_full,
	resolve_qualified_name,
	wtrl_build_autodoc_module_nodes,
	wtrl_build_autodoc_function_nodes,
	wtrl_build_autodoc_class_nodes,
	wtrl_build_autodoc_class_full_nodes,
	wtrl_build_push_current_module_nodes,
	wtrl_build_push_current_class_nodes,
	wtrl_build_push_current_scope_nodes,
	wtrl_build_pop_current_module_nodes,
	wtrl_build_pop_current_class_nodes,
	wtrl_build_pop_current_scope_nodes,
	wtrl_build_method_signature_nodes,
	wtrl_build_function_signature_nodes,
	wtrl_build_method_signature_block_nodes,
	wtrl_build_function_signature_block_nodes
Function_overview:
	build_sphinx_nodes:
		Build a list of Docutils nodes from a docstring tree.
	build_sphinx_nodes_full:
		Build a list of Docutils nodes of a class object and its member functions from a docstring tree.
	resolve_qualified_name:
		Analyze a qualified name and return the object it refers to plus resolved name components.

	wtrl_build_autodoc_module_nodes:
		Implementation of role |attr|`.. wtrl_autodoc_module::`
	wtrl_build_autodoc_function_nodes:
		Implementation of role |attr|`.. wtrl_autodoc_function::`
	wtrl_build_autodoc_class_nodes:
		Implementation of role |attr|`.. wtrl_autodoc_class::`
	wtrl_build_autodoc_class_full_nodes:
		Implementation of role |attr|`.. wtrl_autodoc_class_full::`

	wtrl_build_push_current_module_nodes:
		Implementation of directive |attr|`.. wtrl_push_current_module::`
	wtrl_build_push_current_class_nodes:
		Implementation of directive |attr|`.. wtrl_push_current_class::`
	wtrl_build_push_current_scope_nodes:
		Implementation of directive |attr|`.. wtrl_push_current_scope::`
	wtrl_build_pop_current_module_nodes:
		Implementation of directive |attr|`.. wtrl_pop_current_module::`
	wtrl_build_pop_current_class_nodes:
		Implementation of directive |attr|`.. wtrl_pop_current_class::`
	wtrl_build_pop_current_scope_nodes:
		Implementation of directive |attr|`.. wtrl_pop_current_scope::`
"""

from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, Mapping, NewType, NoReturn, Protocol, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

import inspect
import re
import importlib
import sys,os,re
import warnings
import builtins
from docutils import nodes
from pathlib import Path

from docutils.parsers.rst import roles
from docutils.parsers.rst import languages
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.parsers.rst.states import Struct as RstStruct
from typing import Sequence, TypeAlias, cast, no_type_check
from sphinx.util.nodes import make_refnode

import sdv.doc.waterloo.docitem as mod_docitem

__version__ = "0.3.0"
# - 0.3.0 [2026-07-04]	New semantic roles
# - 0.2.1 [2026-05-08]	Bugfixes name resolution in link lists like "Public_methods"
# - 0.2.0 [2026-05-06]	Scope awareness
# - 0.1.1 [2026-04-25]	Parameters is now rendered as free-form text, not bullet list.
# - 0.1.0 [2026-04-17]	Public_types/constants/variables are now rendered as free-form text, not bullet list.

#===== Typechecking ===========================================#

Struct: TypeAlias = RstStruct


class InlinerDocumentSettings(Protocol):
	language_code: str
	env: Any


class InlinerDocument(Protocol):
	settings: InlinerDocumentSettings
	reporter: Any


class InlinerProtocol(Protocol):
	document: InlinerDocument
	reporter: Any

	def parse(self, text: str, lineno: int, memo: Struct, parent: nodes.Element) -> tuple[list[nodes.Node], list[nodes.Node]]: ...


class SphinxEnvProtocol(Protocol):
	docitem_context_configurator: Dict[str, Any] | None


class SphinxAppProtocol(Protocol):
	env: SphinxEnvProtocol
	docitem_context_configurator: Dict[str, Any] | None


class DirectiveStateProtocol(Protocol):
	inliner: InlinerProtocol
	document: InlinerDocument


class DirectiveLike(Protocol):
	state: DirectiveStateProtocol
	lineno: int

# Common role handler signature used by Docutils/Sphinx roles
RoleHandler: TypeAlias = Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]]

#===== Constants ==============================================#




class context:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
		|Must| be able to hold data from both the Sphinx environment and the user-defined configuration in |file|`conf.py`.
		|Must| provide a method which allows configuration by means of a simple, documented data structure.
		|Must| provide access to role decorator functions which map plain text to decorated text.
		|Must| provide setters to specify these role decorator functions.
	constructor:
		Internal class, TBD later, complicated sphinx stuff.
	"""
	def __init__(self,parse_inline : Callable[[nodes.Element, int, str], List[nodes.Node]],lineno: int) -> None:
		self.parse = parse_inline
		self.i_line = lineno
# See make_context. We extract env from the SphinxApp instance.
		self.env = None
		self.wtrl_validated_doc_cache: dict[int, mod_docitem.docitem_docstring_base | None] = {}
		self.add_role_attr = lambda t:f":wtrl_attr:`{t}`"
		self.add_role_cmd = lambda t:f":wtrl_cmd:`{t}`"
		self.add_role_dfn = lambda t:f":wtrl_dfn:`{t}`"
		self.add_role_file = lambda t:f":wtrl_file:`{t}`"
		self.add_role_func = lambda t:f":wtrl_func:`{t}`"
		self.add_role_label = lambda t:f":wtrl_label:`{t}`"
		self.add_role_lit = lambda t:f":wtrl_lit:`{t}`"
		self.add_role_mod = lambda t:f":wtrl_mod:`{t}`"
		self.add_role_norm = lambda t:f":wtrl_norm:`{t}`"
		self.add_role_op = lambda t:f":wtrl_op:`{t}`"
		self.add_role_opt = lambda t:f":wtrl_opt:`{t}`"
		self.add_role_tag = lambda t:f":wtrl_tag:`{t}`"
		self.add_role_type = lambda t:f":wtrl_type:`{t}`"
		self.add_role_value = lambda t:f":wtrl_value:`{t}`"
		self.add_role_var = lambda t:f":wtrl_var:`{t}`"
		self.add_role_var_type = lambda t:f":wtrl_var_type:`{t}`"
		self.build_prolog_method_overview : Callable[[context,str],List[nodes.Node]] = build_prolog_method_overview
		self.build_prolog_method_block : Callable[[context,nodes.Element | None,type[object],Callable[...,Any]],List[nodes.Node]] = build_prolog_method_block
		self.tr = mod_docitem.tracer()

	def set_add_role_attr(self,c : Callable[[str],str]) -> None:
		self.add_role_attr = c
	def set_add_role_cmd(self,c : Callable[[str],str]) -> None:
		self.add_role_cmd = c
	def set_add_role_dfn(self,c : Callable[[str],str]) -> None:
		self.add_role_dfn = c
	def set_add_role_file(self,c : Callable[[str],str]) -> None:
		self.add_role_file = c
	def set_add_role_func(self,c : Callable[[str],str]) -> None:
		self.add_role_func = c
	def set_add_role_label(self,c : Callable[[str],str]) -> None:
		self.add_role_label = c
	def set_add_role_lit(self,c : Callable[[str],str]) -> None:
		self.add_role_lit = c
	def set_add_role_mod(self,c : Callable[[str],str]) -> None:
		self.add_role_mod = c
	def set_add_role_norm(self,c : Callable[[str],str]) -> None:
		self.add_role_norm = c
	def set_add_role_op(self,c : Callable[[str],str]) -> None:
		self.add_role_op = c
	def set_add_role_opt(self,c : Callable[[str],str]) -> None:
		self.add_role_opt = c
	def set_add_role_tag(self,c : Callable[[str],str]) -> None:
		self.add_role_tag = c
	def set_add_role_type(self,c : Callable[[str],str]) -> None:
		self.add_role_type = c
	def set_add_role_var(self,c : Callable[[str],str]) -> None:
		self.add_role_var = c
	def set_add_role_value(self,c : Callable[[str],str]) -> None:
		self.add_role_value = c
	def set_add_role_var_type(self,c : Callable[[str],str]) -> None:
		self.add_role_var_type = c
	def set_build_prolog_method_overview(self,c : Callable[[context,str],List[nodes.Node]]) -> None:
		self.build_prolog_method_overview = c
	def set_build_prolog_method_block(self,c : Callable[[context,nodes.Element | None,object,object],List[nodes.Node]]) -> None:
		self.build_prolog_method_block = c
	def apply_config(self, cfg: dict[str,str]) -> None:
		def mk_role(role : str) -> Callable[[str],str]:
			return lambda t: f":{role}:`{t}`"
		role_map = [
			("role_attr", self.set_add_role_attr),
			("role_cmd", self.set_add_role_cmd),
			("role_dfn", self.set_add_role_dfn),
			("role_file", self.set_add_role_file),
			("role_func", self.set_add_role_func),
			("role_label", self.set_add_role_label),
			("role_lit", self.set_add_role_lit),
			("role_mod", self.set_add_role_mod),
			("role_norm", self.set_add_role_norm),
			("role_op", self.set_add_role_op),
			("role_opt", self.set_add_role_opt),
			("role_tag", self.set_add_role_tag),
			("role_type", self.set_add_role_type),
			("role_value", self.set_add_role_value),
			("role_var", self.set_add_role_var),
			("role_var_type", self.set_add_role_var_type),
		]
		for key, setter in role_map:
			if key in cfg:
				setter(mk_role(cfg[key]))
		if "prolog_method_overview" in cfg:
			self.set_build_prolog_method_overview(import_by_path(cfg["prolog_method_overview"]))
		if "prolog_method_block" in cfg:
			self.set_build_prolog_method_block(import_by_path(cfg["prolog_method_block"]))

def make_context(app: SphinxAppProtocol | Any, parse_inline: Callable[[nodes.Element, int, str], List[nodes.Node]], lineno: int) -> context:
	ctx = context(parse_inline, lineno)
	ctx.env = getattr(app, "env", None)
	configurator = getattr(app, "docitem_context_configurator", None)
	if configurator is None:
		configurator = getattr(app.env, "docitem_context_configurator", None)
	if configurator:
		assert isinstance(configurator, dict)
		ctx.apply_config(configurator)
	return ctx

# Inline-Parser, der *messages nicht wegwirft*
def parse_inline(inliner: InlinerProtocol, parent: nodes.Element, ln: int, txt: str) -> List[nodes.Node]:
	lang = languages.get_language(inliner.document.settings.language_code)

	memo = RstStruct(
	 document=inliner.document,
	 reporter=inliner.reporter,
	 language=lang,
	 title_styles=[],
	 section_level=0,
	 section_bubble_up_kludge=False,
	 inliner=inliner,
	)

	nodes_out, messages = inliner.parse(txt, ln, memo, parent)
	result: List[nodes.Node] = list(nodes_out)
	for msg in messages:
		parent += msg
	return result


def _register_anchor(ctx: context, obj: object, anchor: str) -> None:
	"""
	Register a local anchor for later cross-reference resolution.

	The registry lives on the Sphinx environment and maps fully qualified object
	names to tuples ``(docname, anchor_id)``.
	"""
	env = getattr(ctx, "env", None)
	if env is None:
		return
	docname = getattr(env, "docname", None)
	if not isinstance(docname, str) or not docname:
		return
	obj_fqn = mod_docitem.get_obj_fully_qualified_name(obj)
	if not isinstance(obj_fqn, str) or not obj_fqn:
		return
	index = getattr(env, "wtrl_anchor_index", None)
	if not isinstance(index, dict):
		index = {}
		setattr(env, "wtrl_anchor_index", index)
	index[obj_fqn] = (docname, anchor)


def _build_internal_ref(ctx: context, target_obj: object, link_text: str, css_class: str) -> nodes.reference:
	"""
	Create an internal reference node for a resolved target object.

	If Sphinx environment/builder context and anchor registry are available,
	use ``make_refnode`` (supports cross-document links). Otherwise fall back
	to a local ``refid`` reference.
	"""
	target_anchor = mod_docitem.build_anchor(target_obj)
	node_child = nodes.inline(link_text, link_text)
	env = getattr(ctx, "env", None)
	builder = getattr(getattr(env, "app", None), "builder", None)
	from_docname = getattr(env, "docname", None)
	index = getattr(env, "wtrl_anchor_index", None)
	target_fqn = mod_docitem.get_obj_fully_qualified_name(target_obj)

	if (
		builder is not None
		and isinstance(from_docname, str)
		and from_docname
		and isinstance(index, dict)
	):
		target_docname: str = from_docname
		target_id: str = target_anchor
		loc = index.get(target_fqn)
		if (
			isinstance(loc, tuple)
			and len(loc) == 2
			and isinstance(loc[0], str)
			and isinstance(loc[1], str)
		):
			target_docname, target_id = loc
		node_ref = make_refnode(
			builder,
			from_docname,
			target_docname,
			target_id,
			node_child,
			title=target_fqn,
		)
	else:
		node_ref = nodes.reference(link_text, link_text, refid=target_anchor)

	node_ref["classes"].append(css_class)
	return node_ref

def _signature_for(obj: object) -> inspect.Signature:
	return inspect.signature(cast(Callable[..., Any], obj))

def _maybe_drop_first_param(sig: inspect.Signature, *, drop: bool) -> inspect.Signature:
	if not drop:
		return sig
	params = list(sig.parameters.values())
	if not params:
		return sig
	first = params[0]
	if first.name in {"self", "cls", "mcls"}:
		return inspect.Signature(parameters=params[1:], return_annotation=sig.return_annotation)
	return sig

def format_type(tp: object) -> str:
	if tp is inspect._empty:
		return "Any"
	if isinstance(tp, type):
		return tp.__name__
	return str(tp)

def format_default(val: object) -> str:
	if val is inspect._empty:
		return ""
	return repr(val)

#===== State controlled by document input =====================#

#----- Globale variables --------------------------------------#
# These are fallback variables in case of testing from outside
# the Sphinx context. In normal usage the stacks are located
# in some appropriate place within Sphinx.
_global_current_module: List[str] = []
_global_current_class: List[str] = []
_global_current_scope: List[mod_docitem.Scope] = [mod_docitem.Scope.PUBLIC]

#----- Helpers ------------------------------------------------#
def _get_module_stack(env: Any | None) -> List[str]:
	attr = "_docitem_module_stack"
	if env is not None and hasattr(env, attr):
		return cast(List[str], getattr(env, attr))
	if env is not None and not hasattr(env, attr):
		setattr(env, attr, [])
		return cast(List[str], getattr(env, attr))
	return _global_current_module

def _get_class_stack(env: Any | None) -> List[str]:
	attr = "_docitem_class_stack"
	if env is not None and hasattr(env, attr):
		return cast(List[str], getattr(env, attr))
	if env is not None and not hasattr(env, attr):
		setattr(env, attr, [])
		return cast(List[str], getattr(env, attr))
	return _global_current_class

def _get_scope_stack(env: Any | None) -> List[mod_docitem.Scope]:
	attr = "_docitem_scope_stack"
	if env is not None and hasattr(env, attr):
		return cast(List[mod_docitem.Scope], getattr(env, attr))
	if env is not None and not hasattr(env, attr):
		setattr(env, attr, [mod_docitem.Scope.PUBLIC])
		return cast(List[mod_docitem.Scope], getattr(env, attr))
	return _global_current_scope

#----- API ----------------------------------------------------@

# Stack ops for current module
def push_current_module(qualified_module_name : str, env: Any | None = None) -> None:
	stack = _get_module_stack(env)
	stack.append(qualified_module_name)
	print(f"push_current_module: {stack[-1]}")
def pop_current_module(env: Any | None = None) -> None:
	stack = _get_module_stack(env)
	print(f"pop_current_module: {stack[-1]}")
	del stack[-1]
def get_current_module(env: Any | None = None) -> str:
	return _get_module_stack(env)[-1]
def has_current_module(env: Any | None = None) -> bool:
	return len(_get_module_stack(env)) > 0

# Stack ops for current class
def push_current_class(qualified_class_name : str, env: Any | None = None) -> None:
	stack = _get_class_stack(env)
	stack.append(qualified_class_name)
	print(f"push_current_class: {stack[-1]}")
def pop_current_class(env: Any | None = None) -> None:
	stack = _get_class_stack(env)
	print(f"pop_current_class: {stack[-1]}")
	del stack[-1]
def get_current_class(env: Any | None = None) -> str:
	return _get_class_stack(env)[-1]
def has_current_class(env: Any | None = None) -> bool:
	return len(_get_class_stack(env)) > 0

# Stack ops for current scope.
def push_current_scope(scope_tag : str, env: Any | None = None) -> None:
	if scope_tag not in mod_docitem.SCOPE_TAG_MAP:
		raise RuntimeError(f"Unknown scope '{scope_tag}'. Expected one of {list(mod_docitem.SCOPE_TAG_MAP.keys())}.")
	scope = mod_docitem.SCOPE_TAG_MAP[scope_tag]
	stack = _get_scope_stack(env)
	stack.append(scope)

def pop_current_scope(env: Any | None = None) -> None:
	stack = _get_scope_stack(env)
	if not stack:
		raise RuntimeError("Cannot pop current scope: stack is empty.")
	del stack[-1]

def get_current_scope(env: Any | None = None) -> mod_docitem.Scope:
	return _get_scope_stack(env)[-1]

def has_current_scope(env: Any | None = None) -> bool:
	return len(_get_scope_stack(env)) > 0

def _get_current_scope_set(env: Any | None = None) -> mod_docitem.Scopes:
	"""
	Convert the current Sphinx rendering scope into a Waterloo scope set.

	The Sphinx layer currently maintains a single active scope on a stack,
	while the core visibility API expects a set of scopes. This helper
	provides the bridge for scope-aware rendering decisions.
	"""
	if not has_current_scope(env):
		return set([mod_docitem.Scope.PUBLIC])
	return set([get_current_scope(env)])

def _is_doc_visible_in_current_scope(ctx: context, doc: mod_docitem.docitem_docstring_base) -> bool:
	"""
	Return whether the documented object is visible under the current
	Sphinx rendering scope.
	"""
	return doc.is_visible(_get_current_scope_set(ctx.env))

def _get_validated_doc_for_object(
	ctx: context,
	obj: object,
) -> mod_docitem.docitem_docstring_base | None:
	"""
	Best-effort lookup of a validated Waterloo docstring tree for an object.

	Link rendering uses this to decide whether a resolved Waterloo object is
	visible under the current Sphinx scope. Failures are treated as
	non-linkable targets and handled by the caller via plain text fallback.
	"""
	cache = ctx.wtrl_validated_doc_cache
	key = id(obj)
	if key in cache:
		cached = cache[key]
		return cached if isinstance(cached, mod_docitem.docitem_docstring_base) else None
	obj_doc = mod_docitem.get_obj_docstring(obj)
	if not isinstance(obj_doc, str) or not obj_doc.strip():
# Objects without a Waterloo docstring cannot contribute scope metadata.
# We treat them as scope-agnostic, so that documented constants and
# similar values remain linkable without spurious warnings.
		cache[key] = None
		return None
	try:
		doc = mod_docitem.validate_docstring(ctx.tr, obj,top=None, session=mod_docitem.DocSession())
	except Exception:
		cache[key] = None
		return None
	cache[key] = doc
	return doc

def _is_target_obj_visible_in_current_scope(ctx: context, obj: object) -> bool:
	doc = _get_validated_doc_for_object(ctx, obj)
	if doc is None:
#		return False
# We must return True here. A target should not be greyed out
# just because of a missing docstring. It may remain unlinked
# but it is not out of scope.
		return True
	return doc.is_visible(_get_current_scope_set(ctx.env))

#==============================================================#

# Official markup resolver: converts |role|`text` into :wtrl_role:`text`
def resolve_markup(text : str, ctx: context) -> str:
	def _resolve_wtrl_ref_uri(qname: str) -> str | None:
# Resolve object
		try:
			target_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		except Exception as exc:
			warnings.warn(f"WTRL ref target '{qname}' cannot be resolved: {exc}", RuntimeWarning)
			return None
		if not _is_target_obj_visible_in_current_scope(ctx, target_obj):
			return None
# Build anchor of object.
		target_anchor = mod_docitem.build_anchor(target_obj)
# Build fallback that works at least page internally,
# if we cannot access the current document name.
		env = getattr(ctx, "env", None)
		if env is None:
			return "#" + target_anchor
		from_docname = getattr(env, "docname", None)
		if not isinstance(from_docname, str) or not from_docname:
			return "#" + target_anchor
# Part of the best effort fallback strategy: If we fail to build the
# inter-page URI we can still hope the target is on the same page.
		target_docname: str = from_docname
		target_id: str = target_anchor
# At this point we already know that the enviroment is well-defined.
# Now extract the wtrl-specific index we accumulate in build_sphinx_nodes.
# Note that the first call to this function via parse_text happens deep inside
# build_sphinx_node, at a point where we already have wtrl_anchor_index.
# Yet, referencing objects rendered later than the current one fails
# if the target is in a different document (works intra-page, fails inter-page).
		index = getattr(env, "wtrl_anchor_index", None)
		target_fqn = mod_docitem.get_obj_fully_qualified_name(target_obj)
# But nonetheless we make sure the index exists and is a dict as expected.
		if isinstance(index, dict):
# Our helper _register_anchor adds anchor as tuple made of two components,
# the document name and the object anchor. If we find this structure
# we can extract the full inter-page URI. This conservative tests makes
# our code immune with respect to "creative" use of wtrl_anchor_index.
			loc = index.get(target_fqn)
			if (
				isinstance(loc, tuple)
				and len(loc) == 2
				and isinstance(loc[0], str)
				and isinstance(loc[1], str)
			):
				target_docname, target_id = loc
# Sphinx provides a mechanism for building the URI from source and target
# document name, provided we can get access to the Sphinx builder.
		builder = getattr(getattr(env, "app", None), "builder", None)
		if builder is not None:
			try:
# No need for inter-page URI if source and target document are the same.
				if from_docname == target_docname:
					return f"#{target_id}"
# Chill mypy. Use Sphinx builder and return URI,
				uri: str = cast(str,builder.get_relative_uri(from_docname, target_docname) + "#" + target_id)
				return uri
			except Exception as exc:
				warnings.warn(
					f"WTRL ref target '{qname}' resolved, but URI construction failed: {exc}",
					RuntimeWarning,
				)
				return None
# Fallback: Intra-page link.
		return "#" + target_id

	def _parse_ref_body(body: str) -> tuple[str, str]:
		"""Return the visible label and target from a Waterloo ref body."""
		m_ext = mod_docitem.RE_WTRL_ANGLE_HTTPS_REF_COMPILED.match(body)
		if m_ext:
			return m_ext.group(1).strip(), m_ext.group(2).strip()
		m_wtrl = mod_docitem.RE_WTRL_ANGLE_WTRL_REF_COMPILED.match(body)
		if m_wtrl:
			return m_wtrl.group(1).strip(), m_wtrl.group(2).strip()
		return body, ""

	def _repl(m: re.Match[str]) -> str:
		role = m.group(1)
		body = m.group(2)
		if role == "ref":
			label, target = _parse_ref_body(body)
			if target.startswith(("http://", "https://")):
				return f"`{label} <{target}>`_"
			if target.startswith("wtrl://"):
				qname = target[len("wtrl://"):]
# Resolve qualified name and build URI in Sphinx/reST style.
				uri = _resolve_wtrl_ref_uri(qname)
				if uri:
					return f"`{label} <{uri}>`_"
				return label
# Sphinx internal reference.
			return f":ref:`{body}`"
		return f":wtrl_{role}:`{body}`"
	s =  mod_docitem.RE_WTRL_MARKUP_BACKTICK_COMPILED.sub(_repl, text)
	return s

def build_sphinx_nodes(ctx : context,obj: object,doc: mod_docitem.docitem_docstring_base) -> List[nodes.Node]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| convert a parsed |type|`docitem_docstring_module`, |type|`docitem_docstring_class` or |type|`docitem_docstring_method` into a list of docutils nodes.
			|Must| render section/key/value content into a two-column table with section labels on the left and content on the right.
			|Must| apply role-formatters provided by |type|`context` (labels, types, vars, funcs, methods).
			|Must| assign a deterministic anchor id to the rendered table.
			|Must| render selected reference-like entries as internal links where targets can be resolved.
			|Must| keep unresolved reference entries visible as plain text fallback.
			|Must| emit runtime warnings for unresolved entries in sections where linkability is expected.
			|Must_not| raise hard validation errors for unresolved references; semantic enforcement belongs to the validator.
	Parameters:
		ctx:
			Rendering context providing inline parser and role-formatters.
		obj:
			The documented object (module, class or method).
		doc:
			Parsed docstring tree (representing one of the defined profiles).
	Returns:
		List of |type|`docutils.nodes.Node` representing the rendered documentation table.
	Raises:
		RuntimeError:
			|May| raise if unexpected section structure is encountered.
		RuntimeWarning:
			|May| emit warnings for unresolved link targets (for example in |label|`Public_*`, |label|`Derived_from`, or normative |label|`See_also`).
	Notes:
		Usage:
			This function is typically not called directly. It is called
			by the various |func|`autodoc` functions.
		Linking:
			Internal links are created using anchor ids from |func|`build_anchor`.
			Built-in exceptions in section |label|`Raises` are intentionally rendered as plain text without internal links.
		Last review:
			2026-02-15
		"""
	if not _is_doc_visible_in_current_scope(ctx, doc):
# Scope-aware rendering omits invisible objects entirely. If later
# we need author-facing placeholders, this is the early return to adapt.
		return []
	node_root: List[nodes.Node] = []
	def parse_text(parent: nodes.Element, text: str) -> List[nodes.Node]:
		return ctx.parse(parent, 0, resolve_markup(text, ctx))

	def is_normative_section(section_label: str) -> bool:
		try:
			node_preamble = cast(Any, doc_items["Preamble"])
			if not node_preamble.has_item("normative_sections"):
				return False
			node_norm = node_preamble.item("normative_sections")
			return section_label in {str(x) for x in node_norm.items()}
		except Exception:
			return False

	def render_linked_factory_entry(parent: nodes.paragraph,entry: str,objname: str,css_class: str,role_fn: Callable[[str], str]) -> None:
		try:
			target_obj, _, _, _ = resolve_qualified_name(ctx, entry)
		except Exception as exc:
			try:
				target_obj, _, _, _ = resolve_qualified_name(ctx, objname + "." + entry)
			except Exception as exc:
				warnings.warn(f"Factory entry '{entry}' cannot be resolved for linking: {exc}",RuntimeWarning)
				parent.extend(ctx.parse(parent,0,role_fn(entry)))
				return
		if not _is_target_obj_visible_in_current_scope(ctx, target_obj):
			render_out_of_scope_entry(parent, entry, role_fn)
			return
		parent += _build_internal_ref(ctx, target_obj, entry, css_class)

	def render_linked_base_entry(parent: nodes.paragraph,entry: str,objname: str,css_class: str,role_fn: Callable[[str], str]) -> None:
		return render_linked_factory_entry(parent,entry,objname,css_class,role_fn)

# Not all parameters are used but we leave them in for future compatibility.
	def render_plain_entry(
		parent: nodes.paragraph,
		entry: str,
		css_class: str,
		role_fn: Callable[[str], str],
		warn_label: str,
	) -> None:
		parent.extend(ctx.parse(parent,0,role_fn(entry)))

	def render_out_of_scope_entry(
		parent: nodes.Element,
		entry: str,
		role_fn: Callable[[str], str],
	) -> None:
		def _mark(node: nodes.Node) -> None:
			if isinstance(node, nodes.literal):
				classes = node.get("classes", [])
				if "wtrl_out_of_scope" not in classes:
					classes.append("wtrl_out_of_scope")
					node["classes"] = classes
			if isinstance(node, nodes.Element):
				for child in node.children:
					_mark(child)

		nodes_out = ctx.parse(parent, 0, role_fn(entry))
		for node_any in nodes_out:
			_mark(node_any)
			parent += node_any

	def render_linked_public_entry(
		parent: nodes.paragraph,
		entry: str,
		resolver_prefix: str,
		css_class: str,
		role_fn: Callable[[str], str],
		warn_label: str,
	) -> None:
		try:
			target_obj, _, _, _ = resolve_qualified_name(ctx, resolver_prefix + "." + entry)
			if not _is_target_obj_visible_in_current_scope(ctx, target_obj):
				render_out_of_scope_entry(parent, entry, role_fn)
				return
			parent += _build_internal_ref(ctx, target_obj, entry, css_class)
		except Exception as exc:
			warnings.warn(f"{warn_label} resolver_prefix '{resolver_prefix}': entry '{entry}' cannot be resolved for linking: {exc}",RuntimeWarning)
			parent.extend(ctx.parse(parent,0,role_fn(entry)))

	def render_linked_public_entries(
		parent: nodes.paragraph,
		entries: Sequence[str],
		resolver_prefix: str,
		css_class: str,
		role_fn: Callable[[str], str],
		warn_label: str,
	) -> None:
		for i_item, content in enumerate(entries):
			content_s = str(content)
			if i_item > 0:
				parent += nodes.Text(", ")
			render_linked_public_entry(parent,content_s,resolver_prefix,css_class,role_fn,warn_label)

	def render_linked_derived_from_entries(
		parent: nodes.paragraph,
		entries: Sequence[str],
		css_class: str,
		role_fn: Callable[[str], str],
	) -> None:
		base_by_name: Dict[str, object] = {}
		if mod_docitem.is_obj_class(obj):
			for b in cast(tuple[type[Any], ...], getattr(obj, "__bases__", ())):
				base_by_name[mod_docitem.get_obj_name(b)] = b
				base_by_name[mod_docitem.get_obj_fully_qualified_name(b)] = b
				nm = getattr(b, "__name__", None)
				if isinstance(nm, str):
					base_by_name[nm] = b
				qn = getattr(b, "__qualname__", None)
				if isinstance(qn, str):
					base_by_name[qn] = b
		for i_item, content in enumerate(entries):
			content_s = str(content)
			if i_item > 0:
				parent += nodes.Text(", ")
			base_obj = base_by_name.get(content_s)
			if base_obj is not None:
				if _is_target_obj_visible_in_current_scope(ctx, base_obj):
					parent += _build_internal_ref(ctx, base_obj, content_s, css_class)
				else:
					render_out_of_scope_entry(parent, content_s, role_fn)
			else:
				warnings.warn(f"Derived_from entry '{content_s}' is not a direct base class of '{objname}'.",RuntimeWarning)
				parent.extend(ctx.parse(parent,0,role_fn(content_s)))

	def render_linked_see_also_entries(
		parent: nodes.paragraph,
		entries: Sequence[str],
		is_normative: bool,
		resolver_prefix: str | None,
	) -> None:
		obj_module_prefix = resolver_prefix
		obj_qualname = getattr(obj, "__qualname__", "")
		obj_class_prefix = None
		if isinstance(obj_qualname, str) and "." in obj_qualname and not mod_docitem.is_obj_module(obj):
			obj_class_prefix = f"{obj_module_prefix}.{obj_qualname.rsplit('.', 1)[0]}" if obj_module_prefix else None
		for i_item, content in enumerate(entries):
			content_s = str(content)
			if i_item > 0:
				parent += nodes.Text(", ")
			target_obj: object | None = None
			last_exc: Exception | None = None
			for cand in (
				content_s,
				f"{obj_module_prefix}.{content_s}" if obj_module_prefix else None,
				f"{obj_class_prefix}.{content_s}" if obj_class_prefix else None,
			):
				if cand is None:
					continue
				try:
					target_obj, _, _, _ = resolve_qualified_name(ctx, cand)
					last_exc = None
					break
				except Exception as exc:
					last_exc = exc
					target_obj = None
			if target_obj is not None and _is_target_obj_visible_in_current_scope(ctx, target_obj):
				parent += _build_internal_ref(ctx, target_obj, content_s, "wtrl_var")
			elif target_obj is not None:
				render_out_of_scope_entry(parent, content_s, ctx.add_role_var)
			else:
				warn_exc: Exception = last_exc if last_exc is not None else ImportError(f"Could not resolve qualified name '{content_s}' with module/class context None/None.")
				if is_normative:
					warnings.warn(f"See_also entry '{content_s}' cannot be resolved for linking: {warn_exc}",RuntimeWarning)
				parent.extend(ctx.parse(parent,0,ctx.add_role_var(content_s)))

	def render_linked_raises_entry_label(parent: nodes.paragraph, exc_name: str) -> None:
		exc_obj: object | None = None
		last_exc: Exception | None = None
		for cand in (exc_name, objname + "." + exc_name):
			try:
				exc_obj, _, _, _ = resolve_qualified_name(ctx, cand)
				break
			except Exception as exc:
				last_exc = exc
				continue
		if exc_obj is None:
			# Built-in exceptions are valid and expected, but typically not part of local anchors.
			bi = getattr(builtins, exc_name, None)
			if isinstance(bi, type) and issubclass(bi, BaseException):
				parent.extend(ctx.parse(parent,0,ctx.add_role_type(exc_name)))
				return
			warnings.warn(f"Raises entry '{exc_name}' cannot be resolved: {last_exc}",RuntimeWarning)
			parent.extend(ctx.parse(parent,0,ctx.add_role_type(exc_name)))
			return
		if not isinstance(exc_obj, type) or not issubclass(exc_obj, BaseException):
			warnings.warn(f"Raises entry '{exc_name}' resolves to non-exception object.",RuntimeWarning)
			parent.extend(ctx.parse(parent,0,ctx.add_role_type(exc_name)))
			return
		# For builtins we keep plain styled text (usually no local anchor target).
		if getattr(exc_obj, "__module__", "") == "builtins":
			parent.extend(ctx.parse(parent,0,ctx.add_role_type(exc_name)))
			return
		if not _is_target_obj_visible_in_current_scope(ctx, exc_obj):
			render_out_of_scope_entry(parent, exc_name, ctx.add_role_type)
			return
		parent += _build_internal_ref(ctx, exc_obj, exc_name, "wtrl_type")

# Contract.*
	RE_DOC_BULLET_LIST = re.compile(r"^[-+*#]\s")
	def build_bullet_list_from_subsection_items(items: Iterable[str]) -> nodes.bullet_list:
		node_bullet_list = nodes.bullet_list()
		for content in items:
			node_list_item = nodes.list_item()
			node_paragraph = nodes.paragraph()
			node_paragraph.extend(parse_text(node_paragraph, content))
			node_list_item += node_paragraph
			node_bullet_list += node_list_item
		return node_bullet_list

# Factory, Method_overview, Function_overview, Class_overview, Public_types, Public_constants, Public_variables, Parameters, Raises,
	def build_bullet_list_from_section_items(section_items: Mapping[str, Any],render_label: Callable[[nodes.paragraph, str], None]) -> nodes.bullet_list:
		node_bullet_list = nodes.bullet_list()
		for label1, item_subsection in section_items.items():
			node_list_item = nodes.list_item()
			node_paragraph = nodes.paragraph()
			render_label(node_paragraph, str(label1))
			node_paragraph += build_bullet_list_from_subsection_items(item_subsection.items())
			node_list_item += node_paragraph
			node_bullet_list += node_list_item
		return node_bullet_list

# Definitions, Terminology, Description, Returns, Notes,
	def build_paragraphs_from_items(items: Sequence[str]) -> List[nodes.paragraph]:
		def gen_list(symbol: str) -> nodes.Element:
			node_any_list: nodes.Element
			if symbol == "#":
				node_any_list = nodes.enumerated_list()
				node_any_list['enumtype'] = 'arabic'
				node_any_list['prefix'] = ''
				node_any_list['suffix'] = '.'
				node_any_list['start'] = 1
			else:
				node_any_list = nodes.bullet_list()
			return node_any_list

		restart = True
# Here we collect the paragraph nodes to be returned.
		out: List[nodes.paragraph] = []
# This is the current object we append content to. Whenever we
# find a paragraph token "|" we push this to `out` and create
# a new one. After the loop the current paragraph is appended
# to `out`.
		node_paragraph = nodes.paragraph()

		i_item = 0
		while i_item < len(items):
			content = items[i_item]
			if content == "|":
				out.append(node_paragraph)
				node_paragraph = nodes.paragraph()
				restart = True
			else:
# We experimentally allow bullet lists triggered by a sequence of leading "* ", "+ ", or "- ".
# in the content lines. If we find such a pattern, we build a bullet list from
# all consecutive lines matching the pattern.
				n_lines = 0
				while i_item + n_lines < len(items) and RE_DOC_BULLET_LIST.match(items[i_item + n_lines]):
					n_lines += 1
					if i_item + n_lines >= len(items):
						break
# Originally at least two items are required for safe pattern recognition,
# but the normative rules are getting too complex in that case, so let's
# simplify this:
				if n_lines >= 1:
# For nested itemizations we need a stack.
					node_stack: List[nodes.Element] = []
					symb_stack: List[str] = []
					last_item_stack: List[nodes.list_item | None] = []

					for content in items[i_item:i_item + n_lines]:
						symbol = content[0]
# Drop bullet marker and space.
						text = content[2:]

						if not symb_stack:
							node_stack.append(gen_list(symbol))
							symb_stack.append(symbol)
							last_item_stack.append(None)
# Is this symbol different and new? -> Increase itemization level
						elif symbol != symb_stack[-1]:
							if symbol not in symb_stack:
# The new nested list must be attached to the previous item
								parent_item = last_item_stack[-1]
								if parent_item is None:
									raise ValueError(
									f"Cannot start nested list with symbol {symbol!r} "
									"without a previous list item."
									)
								symb_stack.append(symbol)
# Create (nested) bullet list and make it the current one.
								node_any_list = gen_list(symbol)
								parent_item += node_any_list
# Make nested list the current one
								node_stack.append(node_any_list)
								last_item_stack.append(None)
# Is this symbol different but old? -> Decrease itemization level
							else:
								while symb_stack[-1] != symbol:
									symb_stack.pop()
									node_stack.pop()
									last_item_stack.pop()
# Same symbol as before? -> Keep itemization level
						else:
							pass
# Always: create a new item on the current level
						node_list_item = nodes.list_item()
# Create paragraph for content.
						node_item_paragraph = nodes.paragraph()
						node_item_paragraph.extend(parse_text(node_list_item, text))
						node_list_item += node_item_paragraph
# Append item to current bullet list
						node_stack[-1] += node_list_item
# Remember last item on this level
						last_item_stack[-1] = node_list_item

					node_paragraph += node_stack[0]
					i_item += n_lines
					continue
# The normal stuff
				node_paragraph.extend(parse_text(node_paragraph, ("" if restart else " ") + content))
				restart = False
			i_item += 1
		out.append(node_paragraph)
		return out

	objname = mod_docitem.get_obj_name(obj)
	objname_q = mod_docitem.get_obj_fully_qualified_name(obj)
	anchor = mod_docitem.build_anchor(obj)
# Required for inter-page references.
	_register_anchor(ctx, obj, anchor)

# Build table
	node_table = nodes.table(classes=["wtrl-box"])
	node_table["ids"] = [anchor]
	node_tgroup = nodes.tgroup(cols=2)
	node_tgroup += nodes.colspec(colwidth=18)
	node_tgroup += nodes.colspec(colwidth=82)
	node_tbody = nodes.tbody()
	node_tgroup += node_tbody

	doc_items = cast(dict[str, Any], doc.items())
	profile = cast(str, cast(Any, doc_items["Preamble"]).items()["profile"].items()[0])
	node_thead = nodes.thead(classes=["wtrl-box-head-" + profile])
	node_hrow = nodes.row()
	node1_entry = nodes.entry()
	node1_entry += ctx.parse(node1_entry,0,ctx.add_role_label(profile.capitalize()))
	node2_entry = nodes.entry()
	node2_entry += nodes.paragraph(text=objname)
	node_hrow += node1_entry
	node_hrow += node2_entry
	node_thead += node_hrow
	node_tgroup += node_thead

	node_table += node_tgroup

# The purpose of this segment is to render the function or method signature
# inside the documentation box (instead of adding it overneath by hand).
# This is closer to the LoIO principle (Locality of Information Output),
# and it's easier for the user because rendering a function requires only
# a single directive.
	if mod_docitem.is_obj_function(obj):
# We achieve this by adding a (pseudo) section.
# Create a table row:
		node_row = nodes.row(classes=["wtrl-section"])
# Left column
		node_entry = nodes.entry()
		node_paragraph = nodes.paragraph()
		node_paragraph.extend(ctx.parse(node_paragraph,0,ctx.add_role_label("Signature")))
		node_entry += node_paragraph
		node_row += node_entry
# Right column
		node_entry = nodes.entry()
# Callable module, classes, head in multicolor.
		node_entry += render_head_of_callable(ctx,obj)
# drop_self=True only removes self,cls,mcls, so most likely we can leave as True. Not 100% sure though.
		node_entry += render_params_and_return_of_callable(ctx,obj,drop_self = True)
		node_row += node_entry
# Add table row to table body.
		node_tbody += node_row

	for label,item_section in doc_items.items():
# New table row per section
		node_row = nodes.row(classes=["wtrl-section"])

		node_entry = nodes.entry()
		node_paragraph = nodes.paragraph()
# Sectionlabels don't have underscores for human readable output.
		node_paragraph.extend(ctx.parse(node_paragraph,0,ctx.add_role_label(cast(Any, item_section).label().replace("_"," "))))
		node_entry += node_paragraph
		node_row += node_entry

		node_entry = nodes.entry()
		if label in ("Preamble","Contract"):
#			node_paragraph = nodes.paragraph()
#			node_entry += node_paragraph
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in cast(dict[str, Any], cast(Any, item_section).items()).items():
				if label1 == "profile":
					continue
# Human-readable substring label
				label1_hr = label1
				if label1 in ("normative_sections",):
					label1_hr = label1.replace("_"," ")

				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_label(label1_hr)))
				if label1 in ("normative_sections","traits","status","scope"):
					node2_bullet_list = nodes.bullet_list()
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()
					sub_items = list(cast(Iterable[str], cast(Any, item_subsection).items()))
					if len(sub_items) > 0:
						if label1 in ("normative_sections",):
							node2_paragraph.extend(ctx.parse(node2_paragraph,0,", ".join([ctx.add_role_label(content.replace("_"," ")) for content in sub_items])))
						elif label1 in ("traits","status","scope"):
							node2_paragraph.extend(ctx.parse(node2_paragraph,0,", ".join([ctx.add_role_value(content) for content in sub_items])))
					else:
						node2_paragraph.extend(ctx.parse(node1_paragraph,0,"|empty|"))
					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				elif label1 in ("base",):
					node2_bullet_list = nodes.bullet_list()
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()
					sub_items = list(cast(Iterable[str], cast(Any, item_subsection).items()))
# Always one entry.
					render_linked_base_entry(node2_paragraph,sub_items[0],objname,"wtrl_func",ctx.add_role_func)
#					node2_paragraph.extend(ctx.parse(node2_paragraph,0,ctx.add_role_func(sub_items[0])))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				elif label1 in ("general","constructor","requires","ensures","invariants",):
					node2_bullet_list = build_bullet_list_from_subsection_items(item_subsection.items())
				else:
					raise NotImplementedError("dude",label1)
				node_list_item += node1_paragraph
				node_list_item += node2_bullet_list
				node_bullet_list += node_list_item

			node_entry += node_bullet_list

		elif label in ("Definitions","Terminology"):
			dl = nodes.definition_list(classes=["wtrl-dfn-list"])
			if label == "Definitions":
				obj_definitions = cast(mod_docitem.docitem_definitions,item_section)
				if obj_definitions.inherited():
# We would like to link to the module doc
					direct_module = mod_docitem.get_obj_direct_module(obj)
					dli = nodes.definition_list_item()
# Label "<Inherited terms>"
					dt = nodes.term()

					if direct_module:
						node_inh = _build_internal_ref(
							ctx,
							direct_module,
							"<Terms inherited from module>",
							"wtrl_label",
						)
						dt += node_inh
					else:
						dt.extend(ctx.parse(dt, 0, ctx.add_role_label("<Terms inherited from module>")))
					dli += dt
					dd = nodes.definition()
					p = nodes.paragraph()
					p.extend(ctx.parse(p, 0, ", ".join([ctx.add_role_dfn(inh) for inh in obj_definitions.inherited()])))
					dd += p
					dli += dd
					dl += dli

			if label == "Definitions":
				seen: Dict[Any,List[str]] = {}
				term_str = ""
# Collect terms having the same content (we have a DAG, not a tree!)
				for term, item_subsection in item_section.items().items():
					if item_subsection in seen:
						seen[item_subsection].append(term)
						continue
					seen[item_subsection] = [term]
# Now render
				for item_subsection,terms in seen.items():
					if not terms:
						continue
					dli = nodes.definition_list_item()
# Term
					dt = nodes.term()
					if len(terms) > 1:
						dt.extend(ctx.parse(dt, 0, ctx.add_role_dfn(terms[0] + " [" + ", ".join(terms[1:]) + "]")))
					else:
						dt.extend(ctx.parse(dt, 0, ctx.add_role_dfn(terms[0])))
					dli += dt
						# Definition
					dd = nodes.definition()
# Content
					for paragraph in build_paragraphs_from_items(item_subsection.items()):
						dd += paragraph
					dli += dd
					dl += dli
			else:
				for term, item_subsection in item_section.items().items():
					dli = nodes.definition_list_item()
# Term
					dt = nodes.term()
					dt.extend(ctx.parse(dt, 0, ctx.add_role_dfn(term)))
					dli += dt
						# Definition
					dd = nodes.definition()
# Content
					for paragraph in build_paragraphs_from_items(item_subsection.items()):
						dd += paragraph
					dli += dd
					dl += dli
			node_entry += dl
# Both a freeform. "Description" is non-normative. "Returns" is normative,
# yet we msut provide tools  like itemization and enumeration in order to
# resolve the inner structure of the returned object, therefore freeform.
		elif label in ("Description", "Returns"):
# Content
			for paragraph in build_paragraphs_from_items(item_section.items()):
				node_entry += paragraph
		elif label in ("Notes",):
			for term, item_subsection in item_section.items().items():
# Rubric, allows classes=['',...]
				rub = nodes.rubric(classes=['wtrl-note-title'])
				rub.extend(ctx.parse(rub, 0, term))
				node_entry += rub
# Content
				for paragraph in build_paragraphs_from_items(item_subsection.items()):
					paragraph["classes"].append("wtrl-freeform-paragraph-content")
					node_entry += paragraph
# Factory: List of function names, each with a line-by-line executable contract.
		elif label in ("Factory"):
			node_bullet_list = build_bullet_list_from_section_items(
				item_section.items(),
				lambda p, lbl: render_linked_factory_entry(
					p, lbl, objname, "wtrl_func", ctx.add_role_func
				),
			)
			node_entry += node_bullet_list
# New in 0.1.1: Parameters and Class/Method/Function_overview are rendered as freeform, like Public_...
# The reason for parameters is that we must have tools like itemization and enumeration
# in order to resolve the inner structure of single parameters.
# The reason for Class/Method/Function_overview is that it makes little sense
# to enforce a line-by-line executable conract style for non-normative sections.
# From an aesthetic point of view we get rid of many bullets of non-items.
		elif label in ("Public_constants", "Public_variables", "Public_types", "Parameters", "Class_overview", "Method_overview", "Function_overview"):
# Bullet list where each item is the name of a public constant/variable plus some free-form content.
			node_bullet_list = nodes.bullet_list()
			for label1, item_subsection in item_section.items().items():
# The list item.
				node_list_item = nodes.list_item()
# First paragraph of the list item: clickable constant/variable label.
				node_label_paragraph = nodes.paragraph()
# Add a clickable label. Pass "Public_constants"/"Public_variables"/"Public_types" as label for warnings.
				if label in ("Public_constants", "Public_variables"):
					render_linked_public_entry(node_label_paragraph,label1,objname_q,"wtrl_var",ctx.add_role_var,label)
				elif label in ("Public_types",):
					render_linked_public_entry(node_label_paragraph,label1,objname_q,"wtrl_type",ctx.add_role_type,label)
# Add a label with semantic role |var|.
				elif label in ("Parameters",):
					render_plain_entry(node_label_paragraph,label1,"wtrl_var",ctx.add_role_var,label)
				elif label in ("Class_overview",):
					render_plain_entry(node_label_paragraph,label1,"wtrl_type",ctx.add_role_type,label)
				elif label in ("Method_overview",):
					render_plain_entry(node_label_paragraph,label1,"wtrl_func",ctx.add_role_func,label)
				elif label in ("Function_overview",):
					render_plain_entry(node_label_paragraph,label1,"wtrl_func",ctx.add_role_func,label)
				node_list_item += node_label_paragraph
# Iterate over logical lines in the public constant's/variable's content and add each paragraph as sibling node in the list item.
				for paragraph in build_paragraphs_from_items(item_subsection.items()):
					paragraph["classes"].append("wtrl-freeform-paragraph-content")
					node_list_item += paragraph
				node_bullet_list += node_list_item
			node_entry += node_bullet_list

		elif label in ("Raises"):
# For section "Raises" we enforce the line-by-line style and interpret the content as an executable contract.
			if len(item_section.items()) == 0:
				node_entry.extend(parse_text(node1_paragraph,"|empty|"))
			else:
				node_bullet_list = build_bullet_list_from_section_items(
					item_section.items(),
					lambda p, lbl: render_linked_raises_entry_label(p, lbl),
				)
				node_entry += node_bullet_list
		elif label in ("Derived_from"):
			node1_paragraph = nodes.paragraph()
			render_linked_derived_from_entries(
				node1_paragraph,
				cast(Sequence[str], item_section.items()),
				"wtrl_type",
				ctx.add_role_type,
			)
			node_entry += node1_paragraph
		elif label in ("See_also",):
			node1_paragraph = nodes.paragraph()
			render_linked_see_also_entries(
				node1_paragraph,
				cast(Sequence[str], item_section.items()),
				is_normative_section("See_also"),
				obj.__name__ if mod_docitem.is_obj_module(obj) else getattr(obj, "__module__", None),
			)
			node_entry += node1_paragraph
# The following three, Public_classes/functions/methods have the
# same structure, only different semantic roles and style classes.
# The content is simply a list of resolvable clickable objects.
		elif label in ("Public_classes",):
			node1_paragraph = nodes.paragraph()
			render_linked_public_entries(
				node1_paragraph,
				cast(Sequence[str], item_section.items()),
				objname_q, "wtrl_type", ctx.add_role_type, label)
			node_entry += node1_paragraph
		elif label in ("Public_functions","Public_methods"):
			node1_paragraph = nodes.paragraph()
			render_linked_public_entries(
				node1_paragraph,
				cast(Sequence[str], item_section.items()),
				objname_q, "wtrl_func", ctx.add_role_func, label)
			node_entry += node1_paragraph
# Catch-all. Scan HTML for "TBD" in order to detect bugs.
		else:
			node_paragraph = nodes.paragraph(text="TBD")
			node_entry += node_paragraph

		node_row += node_entry
		node_tbody += node_row

	return [node_table]

def build_sphinx_nodes_full(ctx : context, class_obj: Any, session: mod_docitem.DocSession) -> List[nodes.Node]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| analyze the docstring and methods of the class object.
			|Must| create a list of sphinx nodes, with elements as specified in the following and have the order as indicated:
			The list |must| contain nodes representing the class' docstring.
			The list |must| contain nodes produced by |func|`ctx.build_prolog_method_overview`.
			For each public method as indicated by the class' normative docstring:
			1. The list |must| contain nodes produced by |func|`ctx.build_prolog_method_block`.
			2. The list |must| contain nodes representing the class' public method's docstring.
	Parameters:
		ctx:
			The context
		class_obj:
			The class object to generate a sphinx documentation node list from.
		session:
			An object to store state and cache information across multiple calls to this function.
	Returns:
		A list of sphinx nodes representing the class and public member documentation.
	Raises:
		RuntimeError:
			|Must| raise if something goes wrong parsing a docstring.
		BaseException:
			|Must| forward exceptions from Sphinx
	"""
# Tracer
	tr = ctx.tr
	with mod_docitem.traced_section(tr, class_obj.__name__):
		nodes_out: List[nodes.Node] = []

# Validate class docstring and Method_overview coverage
		class_doc_txt = mod_docitem.get_obj_docstring(class_obj)
		if not class_doc_txt:
			raise RuntimeError(f"class {class_obj} has no docstring.")
		top = cast(mod_docitem.docitem_docstring_class,mod_docitem.validate_docstring(tr,class_obj, top=None, session=session))
		mod_docitem.validate_class_method_coverage(tr,class_obj,top,session=session)
		assert isinstance(class_doc_txt, str)

		tree_cls = mod_docitem.parse_indent_docstring(tr,class_doc_txt, session)
		di_cls = mod_docitem.docitem_docstring_class()
		di_cls.parse(tr,tree_cls)
		mod_docitem.validate_docstring(tr,class_obj,di_cls, session=session)
		if not _is_doc_visible_in_current_scope(ctx, di_cls):
# Scope-aware rendering omits invisible objects entirely. If later
# we need author-facing placeholders, this is the class-level exit to adapt.
			return []

# Render class block
		nodes_out.extend(build_sphinx_nodes(ctx, class_obj, di_cls))

# Render public classes
		if "Public_classes" in di_cls.items():
#			nodes_out.extend(ctx.build_prolog_method_overview(ctx))
			pc_node = di_cls._items["Public_classes"]
			assert isinstance(pc_node, mod_docitem.docitem_public_classes)
			if len(pc_node.items()) > 0:
				rubric = nodes.rubric()
				rubric += ctx.parse(rubric, ctx.i_line, f"Nested classes in {ctx.add_role_type(class_obj.__name__)}")
				nodes_out.append(rubric)
			for cls_name in pc_node.items():
				if not hasattr(class_obj, cls_name):
					continue
				cls_obj = getattr(class_obj, cls_name)
# Recusrive call
				nodes_out.extend(build_sphinx_nodes_full(ctx,cls_obj, session=session))


# Render public methods
		if "Public_methods" in di_cls.items():
			try:
				pm_node = di_cls._items["Public_methods"]
				assert isinstance(pm_node, mod_docitem.docitem_public_methods)
				if len(pm_node.items()) > 0:
					rubric = nodes.rubric()
					rubric += ctx.parse(rubric, ctx.i_line, f"Public Methods in class {ctx.add_role_type(mod_docitem.get_obj_name(class_obj))}")
					nodes_out.append(rubric)
				for meth_name in pm_node.items():
					if not hasattr(class_obj, meth_name):
						continue
					meth_obj = getattr(class_obj, meth_name)
					func_obj = mod_docitem.get_func_obj_from_callable(meth_obj)
					if not func_obj:
						continue
					func_doc_txt = mod_docitem.get_obj_docstring(func_obj)
					if not func_doc_txt:
						continue
					tree_m = mod_docitem.parse_indent_docstring(tr,func_doc_txt, session)

					profile = mod_docitem.get_profile_of_tree(tr,tree_m)
					di_m :  mod_docitem.docitem_base
					if profile == "inherited_method":
						di_m = mod_docitem.docitem_docstring_inherited_method()
					else:
						di_m = mod_docitem.docitem_docstring_method()

					di_m.parse(tr,tree_m)
					mod_docitem.validate_docstring(tr,func_obj,di_m, session=session)
					if not _is_doc_visible_in_current_scope(ctx, di_m):
						continue
					nodes_out.extend(ctx.build_prolog_method_block(ctx, None, class_obj, func_obj))
					nodes_out.extend(build_sphinx_nodes(ctx, func_obj, di_m))
			except:
				pass
# Render properties.
		if "Public_variables" in di_cls.items():
			node_methods = di_cls._items["Public_variables"]
			assert isinstance(node_methods, mod_docitem.docitem_public_variables)
# Iterate over property candidates
			for prop_name in node_methods.items():
				if not hasattr(class_obj, prop_name):
					continue
# Extract and check if it is a property
				prop_obj = inspect.getattr_static(class_obj, prop_name)
				if not isinstance(prop_obj, property):
					continue
# Extract method objects
				meth_objs: list[Tuple[Callable[...,Any],str]] = []
# Check for existence, just to be sure. Insert only if it is a method object.
				for attr_name in ("fget", "fset", "fdel"):
					meth = getattr(prop_obj, attr_name)
					if meth is not None:
						meth_objs.append((meth,prop_name + "." + attr_name))
				for func_obj,func_name in meth_objs:
					func_doc_txt = mod_docitem.get_obj_docstring(func_obj)
					if not func_doc_txt:
						continue
					tree_m = mod_docitem.parse_indent_docstring(tr,func_doc_txt, session)

					profile = mod_docitem.get_profile_of_tree(tr,tree_m)
					di_prop_meth :  mod_docitem.docitem_base
					if profile == "inherited_method":
						di_prop_meth = mod_docitem.docitem_docstring_inherited_method()
					else:
						di_prop_meth = mod_docitem.docitem_docstring_method()

					di_prop_meth.parse(tr,tree_m)
					mod_docitem.validate_docstring(tr,func_obj,di_prop_meth, session=session)
					if not _is_doc_visible_in_current_scope(ctx, di_prop_meth):
						continue
#					nodes_out.extend(ctx.build_prolog_method_block(ctx, None, prop_obj, func_obj))
					nodes_out.extend(build_sphinx_nodes(ctx, func_obj, di_prop_meth))
		return nodes_out

#===== Sphinx extension stuff =================================#

def resolve_qualified_name(ctx: context | None, qname: str) -> tuple[object, str, str, list[str]]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| resolve the qualified name |var|`qname` using current module/class context in |var|`ctx` when present.
		|Must| try to import the resolved object as criterion that resolution succeeded (see section |label|`Raises`)
		|Must| try fully qualified forms in this order: current module + current class + |var|`qname`, current module + |var|`qname`, then |var|`qname` as given.
Parameters:
	ctx:
		The context which provides current module and current class.
	qname:
		The qualified name to resolve.
Returns:
	|Must| return a tuple |type|`(obj, module_name, head_name, tail_parts)` where
	|var|`obj` is the resolved object, |var|`module_name` is the imported module name,
	|var|`head_name` is the last attribute component, and |var|`tail_parts`
	is the attribute chain after the module components.
Raises:
	ImportError:
		|Must| raise if the module of the qualified name cannot be resolved.
	ValueError:
		|Must| raise if no attribute is specified after a resolved module name.
	BaseException:
		|Must| propagate exceptions from the module import.
	"""
	env = ctx.env if ctx is not None else None
	def _resolve_absolute(abs_qname: str) -> tuple[object, str, str, list[str]]:
		parts = abs_qname.split(".")
		mod = None
		modname = None
		split_at = None
		for i in range(len(parts), 0, -1):
			cand = ".".join(parts[:i])
			try:
				mod = importlib.import_module(cand)
				modname = cand
				split_at = i
				break
			except ImportError:
				continue
		if mod is None:
			raise ImportError(f"Could not import any module prefix from: {abs_qname} (2)")
		tail = parts[split_at:]
		if not tail:
			head_name = parts[-1]
			assert modname is not None
			return mod, modname, head_name, []
		obj = mod
		for p in tail:
			try:
				obj = getattr(obj, p)
			except AttributeError as exc:
				raise ImportError(f"{cand} has no attribute {p}") from exc
		head_name = tail[-1]
		assert modname is not None
		return obj, modname, head_name, tail

	candidates = []
	cur_mod = get_current_module(env) if has_current_module(env) else None
	cur_cls = get_current_class(env) if has_current_class(env) else None
	if cur_mod and cur_cls:
		candidates.append(f"{cur_mod}.{cur_cls}.{qname}")
	if cur_mod:
		candidates.append(f"{cur_mod}.{qname}")
	candidates.append(qname)
	seen = set()
	for cand in candidates:
		if cand in seen:
			continue
		seen.add(cand)
		try:
			return _resolve_absolute(cand)
		except ImportError:
			continue
	raise ImportError(f"Could not resolve qualified name '{qname}' with module/class context {cur_mod}/{cur_cls}.")

def import_by_path(path: str) -> Any:
	if "." in path:
		mod, _, attr = path.rpartition(".")
	else:
		mod, attr = "conf", path
	return getattr(importlib.import_module(mod), attr)

#----- begin Sphinx nodes for function signatures -------------#

def render_signature_tokens_inline(ctx: context, func_qname: str, *, drop_self: bool = True, display_scope: bool = False) -> List[nodes.Node]:
	obj, modname, head_name, tail = resolve_qualified_name(ctx, func_qname)

	display_mod = ".".join([modname] + tail[:-1])
	display_name = head_name

# detect decorators
	decorator_lines = mod_docitem.get_obj_decorators(obj)
# detect async
	coroutine_marker = ""
	if inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj):
		coroutine_marker = "async "

	sig = _signature_for(obj)
	sig = _maybe_drop_first_param(sig, drop=drop_self)

	def _tkn(role_fn: Callable[[str], str], text: str) -> List[nodes.Node]:
		markup = role_fn(text)
		m = re.match(r":([A-Za-z0-9_]+):`(.+)`", markup)
		if m:
			role_name, body = m.group(1), m.group(2)
			return [nodes.inline(body, body, classes=[role_name])]
		return [nodes.inline(markup, markup)]

	tokens: List[nodes.Node] = []

# decorators - does not look good in practice because it's inline.
# Better use the block representation.
	if decorator_lines:
		for decorator_line in decorator_lines:
			tokens.extend(_tkn(ctx.add_role_attr, decorator_line + " "))
# coroutine
	if coroutine_marker:
		tokens.extend(_tkn(ctx.add_role_attr, coroutine_marker))

	if display_scope:
		tokens.extend(_tkn(ctx.add_role_func, display_mod))
		tokens.extend(_tkn(ctx.add_role_op, "."))
	tokens.extend(_tkn(ctx.add_role_func, display_name))
	tokens.extend(_tkn(ctx.add_role_op, "("))

	first = True
	for pname, p in sig.parameters.items():
		if not first:
			tokens.extend(_tkn(ctx.add_role_op, ", "))
		first = False

		if p.kind == inspect.Parameter.VAR_POSITIONAL:
			tokens.extend(_tkn(ctx.add_role_op, "*"))
		elif p.kind == inspect.Parameter.VAR_KEYWORD:
			tokens.extend(_tkn(ctx.add_role_op, "**"))

		tokens.extend(_tkn(ctx.add_role_var, pname))

		ann = format_type(p.annotation)
		if ann != "Any":
			tokens.extend(_tkn(ctx.add_role_op, ": "))
			tokens.extend(_tkn(ctx.add_role_type, ann))

		dflt = format_default(p.default)
		if dflt:
			tokens.extend(_tkn(ctx.add_role_op, " = "))
			tokens.extend(_tkn(ctx.add_role_lit, dflt))

	tokens.extend(_tkn(ctx.add_role_op, ")"))
	tokens.extend(_tkn(ctx.add_role_op, " -> "))
	tokens.extend(_tkn(ctx.add_role_type, format_type(sig.return_annotation)))
	return tokens

def _tkn(role_fn: Callable[[str], str], text: str) -> List[nodes.Node]:
	markup = role_fn(text)
	m = re.match(r":([A-Za-z0-9_]+):`(.+)`", markup)
	if m:
		role_name, body = m.group(1), m.group(2)
		return [nodes.inline(body, body, classes=[role_name])]
	return [nodes.inline(markup, markup)]

# Multiline variant: one parameter per line, hanging indent.
def render_signature_tokens_multiline(ctx: context, func_qname: str, *, drop_self: bool = True, display_scope: bool = True) -> List[nodes.Node]:
	obj, modname, head_name, tail = resolve_qualified_name(ctx, func_qname)

	display_mod = ".".join([modname] + tail[:-1])
	display_name = head_name

# detect decorators
	decorator_lines = mod_docitem.get_obj_decorators(obj)

# detect async
	coroutine_marker = ""
	if inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj):
		coroutine_marker = "async "

	lines: List[nodes.line] = []
	# header line
	header = nodes.line(classes=["wtrl-signature-head"])
# decorator
	decorator = nodes.line(classes=["wtrl-signature-decorator"])
	if decorator_lines:
		for decorator_line in decorator_lines:
			node_deco = nodes.line()
			node_deco += _tkn(ctx.add_role_attr, decorator_line)
			decorator.append(node_deco)
# coroutine
	if coroutine_marker:
		header += _tkn(ctx.add_role_attr, coroutine_marker)
# [qualified] function name
	if display_scope:
		header += _tkn(ctx.add_role_func, display_mod)
		header += _tkn(ctx.add_role_op, ".")
	header += _tkn(ctx.add_role_func, display_name)
	header += _tkn(ctx.add_role_op, "(")

# Prepend decorators if there are any, one per line as in the source code.
	if(decorator_lines):
		lines.append(decorator)

	lines.append(header)

	lines += render_params_and_return_of_callable(ctx,obj,drop_self)
	
	# Wrap in a line_block so that Docutils renders each line separately
	line_block = nodes.line_block(classes=["wtrl-signature", "wtrl-signature-multiline"])
	for ln in lines:
		line_block += ln
	return [line_block]

def render_head_of_callable(ctx: context, obj: object, display_scope: bool = True) -> List[nodes.line]:
	lines: List[nodes.line] = []
	objname = mod_docitem.get_obj_name(obj)
	objname_segments = objname.split(".")
# detect decorators
	decorator_lines = mod_docitem.get_obj_decorators(obj)
# detect async
	coroutine_marker = ""
	if inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj):
		coroutine_marker = "async "
# find module
	mod = obj.__module__
# decorator
	decorator = nodes.line(classes=["wtrl-signature-decorator"])
	if decorator_lines:
		for decorator_line in decorator_lines:
			node_deco = nodes.line()
			node_deco += _tkn(ctx.add_role_attr, decorator_line)
			decorator.append(node_deco)
		lines.append(decorator)
# Header: Coroutine marker, module, class hierarchy and function name.
	header = nodes.line(classes=["wtrl-signature-head"])
# coroutine
	if coroutine_marker:
		header += _tkn(ctx.add_role_attr, coroutine_marker)
	if display_scope:
# module name
		header += _tkn(ctx.add_role_mod, mod_docitem.get_obj_name(mod))
		header += _tkn(ctx.add_role_op, ".")
# qualified function name: class segments
	for i_seg in range(len(objname_segments) - 1):
# Class and nested classes
		header += _tkn(ctx.add_role_type, objname_segments[i_seg])
		header += _tkn(ctx.add_role_op, ".")
# Unqualified function name.
	header += _tkn(ctx.add_role_func, objname_segments[-1])
	header += _tkn(ctx.add_role_op, "(")
	lines.append(header)
	return lines

def render_params_and_return_of_callable(ctx: context, obj: object,drop_self: bool = True) -> List[nodes.line]:
	lines: List[nodes.line] = []
	sig = _signature_for(obj)
	sig = _maybe_drop_first_param(sig, drop=drop_self)

# parameter lines
	for pname, p in sig.parameters.items():
# Important: build a style in order to shape indentation for parameters.
		line = nodes.line(classes=["wtrl-signature-param"])

		if p.kind == inspect.Parameter.VAR_POSITIONAL:
			line += _tkn(ctx.add_role_op, "*")
		elif p.kind == inspect.Parameter.VAR_KEYWORD:
			line += _tkn(ctx.add_role_op, "**")

		line += _tkn(ctx.add_role_var, pname)

		ann = format_type(p.annotation)
# Decomment in order to suppress ": Any" for unannotaated code.
# Better: use Annotations!
#		if ann != "Any":
		if 1:
			line += _tkn(ctx.add_role_op, ": ")
			line += _tkn(ctx.add_role_type, ann)

		dflt = format_default(p.default)
		if dflt:
			line += _tkn(ctx.add_role_op, " = ")
			line += _tkn(ctx.add_role_lit, dflt)

		lines.append(line)

 # closing line with return annotation
	closing = nodes.line(classes=["wtrl-signature-ret"])
	closing += _tkn(ctx.add_role_op, ")")
	closing += _tkn(ctx.add_role_op, " -> ")
	closing += _tkn(ctx.add_role_type, format_type(sig.return_annotation))
	lines.append(closing)
	return lines


#----- end Sphinx nodes for function signatures ---------------#

#----- begin directive classes --------------------------------#
class WtrlDirectiveBase(Directive):
	required_arguments = 1
	has_content = False

	def _run(self,node_builder: Callable[[SphinxAppProtocol | Any, InlinerProtocol, int, str], list[nodes.Node]]) -> list[nodes.Node]:
		env = self.state.document.settings.env
		app = env.app
		qname = self.arguments[0].strip()

		try:
			return node_builder(app, cast(InlinerProtocol, self.state.inliner), self.lineno, qname)
		except Exception as e:
		 # Directive-style error message with file/line.
			raise self.error(str(e))

class WtrlAutodocModuleDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_autodoc_module_nodes)

class WtrlAutodocFunctionDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_autodoc_function_nodes)

class WtrlAutodocClassDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_autodoc_class_nodes)

class WtrlAutodocClassFullDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_autodoc_class_full_nodes)

class WtrlPushCurrentModuleDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_push_current_module_nodes)

class WtrlPushCurrentClassDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_push_current_class_nodes)

class WtrlPopCurrentModuleDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_pop_current_module_nodes)

class WtrlPopCurrentClassDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_pop_current_class_nodes)

class WtrlPushCurrentScopeDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_push_current_scope_nodes)

class WtrlPopCurrentScopeDirective(WtrlDirectiveBase):
	required_arguments = 1
	optional_arguments = 0
	def run(self) -> list[nodes.Node]:
		env = self.state.document.settings.env
		app = env.app
		scope_tag = self.arguments[0].strip()
		return wtrl_build_pop_current_scope_nodes(app, cast(InlinerProtocol, self.state.inliner), self.lineno, scope_tag)

class WtrlMethodSignatureDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_method_signature_nodes)

class WtrlFunctionSignatureDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_function_signature_nodes)

class WtrlMethodSignatureBlockDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_method_signature_block_nodes)

class WtrlFunctionSignatureBlockDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_function_signature_block_nodes)

#----- end directive classes ----------------------------------#

#----- begin node builder functions ---------------------------#

def wtrl_build_autodoc_module_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| resolve the dotted module name |var|`text` to a Python module object taking into account the current module state.
		|Must| parse and validate the module's Waterloo docstring.
		|Must| render the parsed docstring into Docutils nodes using the configured context.
Description:
	Implementation of role |attr|`:wtrl_autodoc_module:`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified module name to build nodes for.
Returns:
	The list of generated |type|`docutils.nodes.Node` representing the module doumentation.
Raises:
	RuntimeError:
		|Must| raise if the qualified name cannot be resolved
		|Must| raise if parsing the docstring fails.
		|Must| raise if validating the docstring tree fails
	BaseException:
		|May| raise if building the list of Docutils nodes fails.
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner,parent,ln,txt), lineno)
	tr = ctx.tr
	session = mod_docitem.DocSession()
	with mod_docitem.traced_section(tr, qname):
		module_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_module(module_obj):
			raise RuntimeError(f"{qname} does not resolve to a module.")
		mod_doc_txt = mod_docitem.get_obj_docstring(module_obj)
		if not mod_doc_txt:
			raise RuntimeError(f"{qname} has no docstring.")

		tree_mod = mod_docitem.parse_indent_docstring(tr,mod_doc_txt, session)
		di_mod = mod_docitem.docitem_docstring_module()
		di_mod.parse(tr,tree_mod)
		mod_docitem.validate_docstring(tr,module_obj, di_mod, session=session)
		return build_sphinx_nodes(ctx, module_obj, di_mod)

def wtrl_build_autodoc_function_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| resolve the dotted function name |var|`qname` to a callable taking into account the current module/class state.
		|Must| parse and validate the function's Waterloo docstring.
		|Must| render the parsed docstring into Docutils nodes using the configured context.
Description:
	Implementation of directive |attr|`.. wtrl_autodoc_function::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified function name to document.
Returns:
	List of generated |type|`docutils.nodes.Node`.
Raises:
	RuntimeError:
		|Must| raise if the qualified name cannot be resolved.
		|Must| raise if parsing the docstring fails.
		|Must| raise if validating the docstring tree fails.
	BaseException:
		|May| raise if building the list of Docutils nodes fails.
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	session = mod_docitem.DocSession()
	with mod_docitem.traced_section(tr, qname):
		function_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not callable(function_obj):
			raise RuntimeError(f"{qname} does not resolve to a callable.")
		func_doc_txt = mod_docitem.get_obj_docstring(function_obj)
		if not func_doc_txt:
			raise RuntimeError(f"{qname} has no docstring.")

		tree_meth = mod_docitem.parse_indent_docstring(tr,func_doc_txt, session)
		if mod_docitem.get_profile_of_tree(mod_docitem.tracer(),tree_meth) in ("function","method"):
			di_meth = mod_docitem.docitem_docstring_method()
			di_meth.parse(tr,tree_meth)
			mod_docitem.validate_docstring(tr,function_obj, di_meth, session=session)
			return build_sphinx_nodes(ctx, function_obj, di_meth)
		else:
			di_inhmeth = mod_docitem.docitem_docstring_inherited_method()
			di_inhmeth.parse(tr,tree_meth)
			mod_docitem.validate_docstring(tr,function_obj, di_inhmeth, session=session)
			return build_sphinx_nodes(ctx, function_obj, di_inhmeth)

def wtrl_build_autodoc_class_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| resolve the dotted class name |var|`qname` to a class taking into account the current module/class state.
		|Must| parse and validate the class' Waterloo docstring.
		|Must| render the parsed docstring into Docutils nodes using the configured context.
Description:
	Implementation of directive |attr|`.. wtrl_autodoc_class::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified class name to document.
Returns:
	List of generated |type|`docutils.nodes.Node`.
Raises:
	RuntimeError:
		|Must| raise if the qualified name cannot be resolved.
		|Must| raise if parsing the docstring fails.
		|Must| raise if validating the docstring tree fails.
	BaseException:
		|May| raise if building the list of Docutils nodes fails.
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	session = mod_docitem.DocSession()
	with mod_docitem.traced_section(tr, qname):
		obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_class(obj):
			raise RuntimeError(f"{qname} is not a class.")
		class_doc_txt = mod_docitem.get_obj_docstring(obj)
		if not class_doc_txt:
			raise RuntimeError(f"{qname} has no docstring.")

		tree_mod = mod_docitem.parse_indent_docstring(tr,class_doc_txt, session)
		di_node = mod_docitem.docitem_docstring_class()
		di_node.parse(tr,tree_mod)
		mod_docitem.validate_docstring(tr,obj, di_node, session=session)
		return build_sphinx_nodes(ctx, obj,di_node)

def wtrl_build_autodoc_class_full_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the class's docstring and create a docstring tree.
		|Must| parse the class methods' docstrings and create docstring trees.
		|Must| validate the docstring trees.
		|Must| convert the docstring trees into a list of Docutils nodes that represent the docstrings.
Description:
	Implementation of directive |attr|`.. wtrl_autodoc_class_full::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified name of the class to be documented.
Returns:
	List of generated |type|`docutils.nodes.Node`.
Raises:
	RuntimeError:
		|Must| raise if the qualified name cannot be resolved.
		|Must| raise if parsing of any of the docstrings fails.
		|Must| raise if validating the docstring tree fails.
	BaseException:
		|May| raise if building the list of Docutils nodes fails.
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	session = mod_docitem.DocSession()
	with mod_docitem.traced_section(tr, qname):
		obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_class(obj):
			raise RuntimeError(f"{qname} is not a class.")
		class_doc_txt = mod_docitem.get_obj_docstring(obj)
		if not class_doc_txt:
			raise RuntimeError(f"{qname} has no docstring.")
		try:
			return build_sphinx_nodes_full(ctx, obj, session=session)
		except Exception as e:
			print(tr.str_by_severity(mod_docitem.tracer.Severity.DEBUG),file=sys.stderr)
			raise

def wtrl_build_push_current_module_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| push the qualified module name in |var|`text` to the module stack, which makes it the new current module.
		|Must| resolve |var|`qname`.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to |file|`stdout`.
Description:
	Implementation of directive |attr|`.. wtrl_push_current_module::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified module name to push onto the stack.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the resulting default module state.
Raises:
	RuntimeError:
		|Must| raise if |var|`qname` does not resolve to a module.
	BaseException:
		|May| propagate exceptions from |func|`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	with mod_docitem.traced_section(tr, qname):
		mod_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_module(mod_obj):
			raise RuntimeError(f"{qname} does not resolve to a module.")
		push_current_module(qname, env=ctx.env)
		msg = f"Classes and functions below this point implicitly belong to package/module {ctx.add_role_var(qname)}. "
		node_par = nodes.paragraph(classes=["wtrl-current-module-message", "wtrl-current-module-push"])
		node_par.extend(parse_inline(inliner, node_par, lineno, msg))
		return [node_par]

def wtrl_build_push_current_class_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| push the qualified class name in |var|`text` to the class stack, which makes it the new current class.
		|Must| resolve |var|`qname`.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to |file|`stdout`.
Description:
	Implementation of directive |attr|`.. wtrl_push_current_class::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified class name to push onto the stack.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the resulting default module state.
Raises:
	RuntimeError:
		|Must| raise if |var|`qname` does not resolve to a class.
	BaseException:
		|May| propagate exceptions from |func|`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	with mod_docitem.traced_section(tr, qname):
		cls_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_class(cls_obj):
			raise RuntimeError(f"{qname} does not resolve to a class.")
		push_current_class(qname, env=ctx.env)
		msg = f"Methods below this point implicitly belong to class {ctx.add_role_var(qname)}."
		node_par = nodes.paragraph(classes=["wtrl-current-class-message", "wtrl-current-class-push"])
		node_par.extend(parse_inline(inliner, node_par, lineno, msg))
		return [node_par]

def wtrl_build_push_current_scope_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, scope_tag: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| push the scope identifier in |var|`scope_tag` to the scope stack, which makes it the new current scope.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to |file|`stdout`.
Description:
	Implementation of directive |attr|`.. wtrl_push_current_scope::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	scope_tag:
		The scope identifier to push onto the stack.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the resulting default scope state.
Raises:
	RuntimeError:
		|Must| raise if |var|`scope_tag` is unknown.
	BaseException:
		|May| propagate exceptions from within Sphinx or Docutils.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	with mod_docitem.traced_section(tr, scope_tag):
		push_current_scope(scope_tag, env=ctx.env)
		msg = f"Scope below this point is set to {ctx.add_role_var(scope_tag)}."
		node_par = nodes.paragraph(classes=["wtrl-current-scope-message", "wtrl-current-scope-push"])
		node_par.extend(parse_inline(inliner, node_par, lineno, msg))
		return [node_par]

def wtrl_build_pop_current_module_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| compare the qualified module name in |var|`qname` to the top of the module stack and raise an exception in case of mismatch.
		|Must| resolve |var|`qname` against the current module/class context.
		|Must| pop one element from the module stack.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to |file|`stdout`.
Description:
	Implementation of directive |attr|`.. wtrl_pop_current_module::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified module name to compare and pop from the stack.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the resulting default module state.
Raises:
	RuntimeError:
		|Must| raise on the attempt to access an element from an empty stack.
		|Must| raise if |var|`qname` does not resolve to a module.
	BaseException:
		|May| propagate exceptions from |func|`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	with mod_docitem.traced_section(tr, qname):
		mod_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_module(mod_obj):
			raise RuntimeError(f"{qname} does not resolve to a module.")
		text_top = get_current_module(ctx.env)
		if text_top != qname:
			raise RuntimeError(f"module stack push/pop mismatch, expected {text_top} got {qname}.")
		pop_current_module(ctx.env)
		if has_current_module(ctx.env):
			new_top = get_current_module(ctx.env)
			msg = f"Default module qualifier {ctx.add_role_var(text_top)} ends here. New default: {ctx.add_role_var(new_top)}. "
		else:
			msg = f"Default module qualifier {ctx.add_role_var(text_top)} ends here. No default module active. "
		node_par = nodes.paragraph(classes=["wtrl-current-module-message", "wtrl-current-module-pop"])
		node_par.extend(parse_inline(inliner, node_par, lineno, msg))
		return [node_par]

def wtrl_build_pop_current_class_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| compare the qualified class name in |var|`qname` to the top of the class stack and raise an exception in case of mismatch.
		|Must| resolve |var|`qname` against the current module/class context.
		|Must| pop one element from the class stack.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to |file|`stdout`.
Description:
	Implementation of directive |attr|`.. wtrl_pop_current_class::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		The qualified class name to compare and pop from the stack.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the resulting default class state.
Raises:
	RuntimeError:
		|Must| raise on the attempt to access an element from an empty stack.
		|Must| raise if |var|`qname` does not resolve to a class.
	BaseException:
		|May| propagate exceptions from |func|`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	tr = ctx.tr
	with mod_docitem.traced_section(tr, qname):
		cls_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_class(cls_obj):
			raise RuntimeError(f"{qname} does not resolve to a class.")
		text_top = get_current_class(ctx.env)
		if text_top != qname:
			raise RuntimeError(f"class stack push/pop mismatch, expected {text_top} got {qname}.")
		pop_current_class(ctx.env)
		if has_current_class(ctx.env):
			new_top = get_current_class(ctx.env)
			msg = f"Default class qualifier {ctx.add_role_var(text_top)} ends here. New default: {ctx.add_role_var(new_top)}. "
		else:
			msg = f"Default class qualifier {ctx.add_role_var(text_top)} ends here. No default class active. "
		node_par = nodes.paragraph(classes=["wtrl-current-class-message", "wtrl-current-class-pop"])
		node_par.extend(parse_inline(inliner, node_par, lineno, msg))
		return [node_par]

def wtrl_build_pop_current_scope_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, scope_tag: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| compare the scope identifier name in |var|`qname` to the top of the scope stack and raise an exception in case of mismatch.
		|Must| pop one element from the scope stack.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to |file|`stdout`.
Description:
	Implementation of directive |attr|`.. wtrl_pop_current_scope::`.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	scope_tag:
		The scope identifier to compare and pop from the stack.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the resulting default scope state.
Raises:
	RuntimeError:
		|Must| raise on the attempt to access an element from an empty stack.
		|Must| raise if |var|`scope_tag` is unknown or mismatches the stack top.
	BaseException:
		|May| propagate exceptions from within Sphinx or Docutils.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner,parent,ln,txt), lineno)
	tr = ctx.tr
	with mod_docitem.traced_section(tr, scope_tag):
		if not has_current_scope(ctx.env):
			raise RuntimeError("Cannot pop current scope: stack is empty.")
		text_top_scope = get_current_scope(ctx.env)
		if scope_tag not in mod_docitem.SCOPE_TAG_MAP:
			raise RuntimeError(f"Unknown scope '{scope_tag}'. Expected one of {list(mod_docitem.SCOPE_TAG_MAP.keys())}.")
		if text_top_scope !=  mod_docitem.SCOPE_TAG_MAP[scope_tag]:
			raise RuntimeError(f"scope stack push/pop mismatch, expected {text_top_scope} got {scope_tag}.")
		pop_current_scope(env=ctx.env)
		if has_current_scope(ctx.env):
			new_scope = get_current_scope(ctx.env)
			msg = f"Scope qualifier {ctx.add_role_var(scope_tag)} ends here. New current scope: {ctx.add_role_var(mod_docitem.Scope(new_scope).name.lower())}. "
		else:
			msg = f"Scope qualifier {ctx.add_role_var(scope_tag)} ends here. No current scope active. "
		node_par = nodes.paragraph(classes=["wtrl-current-scope-message", "wtrl-current-scope-pop"])
		node_par.extend(parse_inline(inliner, node_par, lineno, msg))
		return [node_par]

def wtrl_build_method_signature_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		core
Contract:
	general:
		|Must| create a list of |type|`docutil`-nodes representing the method signature as inline text.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		Qualified name of method to render.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the method signature.
Raises:
	BaseException:
		|May| propagate exceptions from |type|`docutils`.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return render_signature_tokens_inline(ctx, qname)

def wtrl_build_function_signature_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		core
Contract:
	general:
		|Must| create a list of |type|`docutil`-nodes representing the function signature as inline text.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		Qualified name of method to render.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the function signature.
Raises:
	BaseException:
		|May| propagate exceptions from |type|`docutils`.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return render_signature_tokens_inline(ctx, qname, drop_self=False)

def wtrl_build_method_signature_block_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		core
Contract:
	general:
		|Must| create a list of |type|`docutil`-nodes representing the method signature as paragraph with one parameter per line.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		Qualified name of method to render.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the method signature.
Raises:
	BaseException:
		|May| propagate exceptions from |type|`docutils`.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return render_signature_tokens_multiline(ctx, qname)

def wtrl_build_function_signature_block_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		core
Contract:
	general:
		|Must| create a list of |type|`docutil`-nodes representing the function signature as paragraph with one parameter per line.
Parameters:
	app:
		The Sphinx application instance that carries configuration and environment state.
	inliner:
		The Docutils inliner used to parse inline markup into nodes.
	lineno:
		Line number in the source document.
	qname:
		Qualified name of method to render.
Returns:
	The list of generated |type|`docutils.nodes.Node` describing the function signature.
Raises:
	BaseException:
		|May| propagate exceptions from |type|`docutils`.
Notes:
	Last review:
		2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return render_signature_tokens_multiline(ctx, qname, drop_self=False)

#----- end node builder functions -----------------------------#

def on_builder_inited(app: Any) -> None:
	cfg = app.config.docitem_context_config
	if cfg is None:
		return
	app.docitem_context_configurator = cfg

WTRL_PROLOG = r"""
.. |Must| replace:: :wtrl_norm:`Must`
.. |must| replace:: :wtrl_norm:`must`
.. |Must_not| replace:: :wtrl_norm:`Must not`
.. |must_not| replace:: :wtrl_norm:`must not`
.. |Should| replace:: :wtrl_norm:`Should`
.. |should| replace:: :wtrl_norm:`should`
.. |Should_not| replace:: :wtrl_norm:`Should not`
.. |should_not| replace:: :wtrl_norm:`should not`
.. |May| replace:: :wtrl_norm:`May`
.. |may| replace:: :wtrl_norm:`may`
.. |Self| replace:: :wtrl_value:`Self`
.. |None| replace:: :wtrl_value:`None`
.. |True| replace:: :wtrl_value:`True`
.. |False| replace:: :wtrl_value:`False`
.. |empty| replace:: :wtrl_value:`<empty>`
"""

MARKUP_WHITELIST = frozenset({
	"Must","must","Must_not","must_not",
	"Should","should","Should_not","should_not",
	"May","may","May_not","may_not",
	"Self","None","True","False",
	"empty",
	"LoII","LoIO","SSoT","BinNorm",
	"SoSaC","SCaA","DrPrv","MVAuth"
	})

_SENTINEL = "\n.. wtrl-prolog:begin\n"

def _inject_wtrl_prolog(app: Any, config :Any) -> None:
# idempotent: nicht doppelt einfuegen
	current = getattr(config, "rst_prolog", "") or ""
	if "wtrl-prolog:begin" in current:
		return
	config.rst_prolog = current + _SENTINEL + WTRL_PROLOG + "\n.. wtrl-prolog:end\n"

#----- helpers ------------------------------------------------#

# Not in use
def build_prolog_method_overview(ctx: context,class_name : str) -> List[nodes.Node]:
	return [cast(nodes.Node,nodes.rubric(text="Public methods of class :wtrl_type:`" + class_name + "`"))]

def build_prolog_method_block(ctx: context,parent : nodes.Element | None,class_obj: type[object],meth_obj : Callable[..., Any]) -> List[nodes.Node]:
# Render the signature directly (multiline variant) instead of parsing a directive string.
# Use fully-qualified name so resolution works even for nested classes.
#	qname = mod_docitem.get_obj_fully_qualified_name(meth_obj)
#	return render_signature_tokens_multiline(ctx, qname, drop_self=True, display_scope=True)
	return []

def wtrl_attr_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_attr"])
	return [node], []

def wtrl_class_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_class"])
	return [node], []

def wtrl_cmd_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_cmd"])
	return [node], []

def wtrl_dfn_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_dfn"])
	return [node], []

def wtrl_file_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_file"])
	return [node], []

def wtrl_func_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_func"])
	return [node], []

def wtrl_key_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_key"])
	return [node], []

def wtrl_label_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_label"])
	return [node], []

def wtrl_lit_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_lit"])
	return [node], []

def wtrl_mod_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_mod"])
	return [node], []

def wtrl_norm_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_norm"])
	return [node], []

def wtrl_op_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_op"])
	return [node], []

def wtrl_opt_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_opt"])
	return [node], []

def wtrl_pkg_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_pkg"])
	return [node], []

def wtrl_tag_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_tag"])
	return [node], []

def wtrl_term_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_term"])
	return [node], []

def wtrl_url_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_url"])
	return [node], []

def wtrl_type_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_type"])
	return [node], []

def wtrl_value_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_value"])
	return [node], []

def wtrl_var_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_var"])
	return [node], []

from typing import Any, Mapping, List, Tuple
from docutils import nodes

def wtrl_var_type_role(name: str,rawtext: str,text: str,lineno: int,inliner: InlinerProtocol,options: Mapping[str, Any] | None = None,content: list[str] | None = None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	if ":" not in text:
		msg = inliner.reporter.error(
		 f"wtrl_var_type expects 'var:type', got '{text}'",
		 line=lineno,
		)
		return [], [msg]

	var, type_ = (s.strip() for s in text.split(":", 1))
	if not var or not type_:
		msg = inliner.reporter.error(
		 f"wtrl_var_type expects 'var:type' with non-empty var and type, got '{text}'",
		 line=lineno,
		)
		return [], [msg]

	node = nodes.inline('', '', classes=["wtrl_var_type"])
	node += nodes.inline(var, var, classes=["wtrl_var"])
	node += nodes.inline(": ", ": ", classes=["wtrl_op"])
	node += nodes.inline(type_, type_, classes=["wtrl_type"])
	return [node], []

def _add_static_path(config: Any, path : str) -> None:
	lst = list(getattr(config, "html_static_path", []) or [])
	if path not in lst:
		lst.append(path)
	config.html_static_path = lst

def _add_css_files(app: Any) -> None:
	app.add_css_file("common_styles.css")
	app.add_css_file("alabaster_waterloo.css")

def on_source_read(app: Any, docname: str, source: List[str]) -> None:
	pass

def setup(app: Any) -> dict[str, Any]:
	here = Path(__file__).resolve().parent
	ext_static = str(here / "_static")

# Official way to configure this extension.
# conf.py defines "docitem_context_config" and we tell the app instance.
# We cannot be sure if it exists, but that's how it is named.
	app.add_config_value("docitem_context_config",None,"env")
# Add a hook, so that we know when the builder is ready.
	app.connect("config-inited", lambda app, config: _add_static_path(config, ext_static))
	app.connect("config-inited", _inject_wtrl_prolog)
	app.connect("builder-inited", on_builder_inited)
	app.connect("builder-inited", _add_css_files)
#	app.connect("source-read", on_source_read)

# Render documentation boxes.
	app.add_directive("wtrl_autodoc_module", WtrlAutodocModuleDirective)
	app.add_directive("wtrl_autodoc_function", WtrlAutodocFunctionDirective)
	app.add_directive("wtrl_autodoc_method", WtrlAutodocFunctionDirective)
	app.add_directive("wtrl_autodoc_class", WtrlAutodocClassDirective)
# Render box for class and all member classes and methods, recursively.
	app.add_directive("wtrl_autodoc_class_full", WtrlAutodocClassFullDirective)
# Current module
	app.add_directive("wtrl_push_current_module", WtrlPushCurrentModuleDirective)
	app.add_directive("wtrl_pop_current_module", WtrlPopCurrentModuleDirective)
# Current class
	app.add_directive("wtrl_push_current_class", WtrlPushCurrentClassDirective)
	app.add_directive("wtrl_pop_current_class", WtrlPopCurrentClassDirective)
# Current scope
	app.add_directive("wtrl_push_current_scope", WtrlPushCurrentScopeDirective)
	app.add_directive("wtrl_pop_current_scope", WtrlPopCurrentScopeDirective)
# Method signature
	app.add_directive("wtrl_method_signature", WtrlMethodSignatureDirective)
	app.add_directive("wtrl_method_signature_block", WtrlMethodSignatureBlockDirective)
# Function signature
	app.add_directive("wtrl_function_signature", WtrlFunctionSignatureDirective)
	app.add_directive("wtrl_function_signature_block", WtrlFunctionSignatureBlockDirective)

	role_map = {
	 "wtrl_attr":wtrl_attr_role,
	 "wtrl_class":wtrl_class_role,
	 "wtrl_cmd":wtrl_cmd_role,
	 "wtrl_dfn":wtrl_dfn_role,
	 "wtrl_file":wtrl_file_role,
	 "wtrl_func":wtrl_func_role,
	 "wtrl_key":wtrl_key_role,
	 "wtrl_label":wtrl_label_role,
	 "wtrl_lit":wtrl_lit_role,
	 "wtrl_mod":wtrl_mod_role,
	 "wtrl_norm":wtrl_norm_role,
	 "wtrl_op":wtrl_op_role,
	 "wtrl_opt":wtrl_opt_role,
	 "wtrl_pkg":wtrl_pkg_role,
	 "wtrl_tag":wtrl_tag_role,
	 "wtrl_term":wtrl_term_role,
	 "wtrl_type":wtrl_type_role,
	 "wtrl_url":wtrl_url_role,
	 "wtrl_value":wtrl_value_role,
	 "wtrl_var":wtrl_var_role,
	 "wtrl_var_type":wtrl_var_type_role,
	 }
	for name,func in role_map.items():
		roles.register_local_role(name,cast(RoleHandler,func))

	return {
	 "version": "0.1",
	 "parallel_read_safe": True,
	 "parallel_write_safe": True,
	 }


#===== Autotesting document consistency =======================#
if __name__ == "__main__":
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, "__main__"):
		mod_docitem.validate_docstring(tr,context,top=None, session=mod_docitem.DocSession())
		mod_docitem.validate_class_coverage(tr,context)
		mod_docitem.validate_module_coverage(tr,sys.modules[__name__])
