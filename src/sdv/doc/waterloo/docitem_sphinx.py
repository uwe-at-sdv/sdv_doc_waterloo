"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
		Public_classes
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
	build_sphinx_nodes
	build_sphinx_nodes_full
	resolve_qualified_name
	wtrl_build_autodoc_module_nodes
	wtrl_build_autodoc_function_nodes
	wtrl_build_autodoc_class_nodes
	wtrl_build_autodoc_class_full_nodes
	wtrl_build_push_current_module_nodes
	wtrl_build_push_current_class_nodes
	wtrl_build_push_current_scope_nodes
	wtrl_build_pop_current_module_nodes
	wtrl_build_pop_current_class_nodes
	wtrl_build_pop_current_scope_nodes
	wtrl_build_method_signature_nodes
	wtrl_build_function_signature_nodes
	wtrl_build_method_signature_block_nodes
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

#Terminology:
#	Docutils node:
#		An element of the Docutils abstract syntax tree (AST), such as :wtrl_type:`paragraph`, :wtrl_type:`section`, or :wtrl_type:`literal`.
#	Docutils role:
#		An inline markup construct of the form ``:role:`content``` implemented
#		using the Docutils role API. Custom roles provided by this module are
#		registered via Sphinx but conceptually belong to Docutils.
#	Sphinx extension:
#		A Python module loaded by Sphinx to extend its parsing, transformation,
#		or rendering behavior. This module is implemented as a Sphinx extension
#		but operates primarily on Docutils data structures.

import inspect
import re
import importlib
import sys,os,re
from docutils import nodes
from pathlib import Path

from docutils.parsers.rst import roles
from docutils.parsers.rst import languages
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.parsers.rst.states import Struct as RstStruct  # type: ignore[attr-defined]
from typing import Sequence, TypeAlias, cast, no_type_check

try:
	import sdv_doc_docitem
	mod_docitem = sdv_doc_docitem
except ImportError:
	import sdv.doc.waterloo.docitem
	mod_docitem = sdv.doc.waterloo.docitem

__version__ = "0.0.1"

#===== Typechecking ===========================================#

Struct = RstStruct


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
		self.env = None
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


# Signature rendering helpers (role-agnostic; use ctx role formatters)
_ARG_RE = re.compile(r"\s*([A-Za-z0-9_]+)\s*:\s*(.+)\s*")
_PROTO_RE = re.compile(r"\s*([A-Za-z0-9_]+)\s*\((.*?)\)\s*(->\s*(.*))?$")

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

# The are fallback variables in case of testing from outside
# the Sphinx context. In nomal usage the stacks are locaced
# in some appropriate place within Sphinx.
_global_current_module: List[str] = []
_global_current_class: List[str] = []
_global_current_scope: List[mod_docitem.Scope] = [mod_docitem.Scope.PUBLIC]

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

def push_current_module(qualified_module_name : str, env: Any | None = None) -> None:
	stack = _get_module_stack(env)
	stack.append(qualified_module_name)
def pop_current_module(env: Any | None = None) -> None:
	stack = _get_module_stack(env)
	del stack[-1]
def get_current_module(env: Any | None = None) -> str:
	return _get_module_stack(env)[-1]
def has_current_module(env: Any | None = None) -> bool:
	return len(_get_module_stack(env)) > 0

def push_current_class(qualified_class_name : str, env: Any | None = None) -> None:
	stack = _get_class_stack(env)
	stack.append(qualified_class_name)
	print(f"push_current_class: {stack[-1]}")
def pop_current_class(env: Any | None = None) -> None:
	stack = _get_class_stack(env)
	del stack[-1]
def get_current_class(env: Any | None = None) -> str:
	return _get_class_stack(env)[-1]
def has_current_class(env: Any | None = None) -> bool:
	return len(_get_class_stack(env)) > 0

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

#==============================================================#

# Official markup resolver: converts |role|`text` into :wtrl_role:`text`
def resolve_markup(text : str) -> str:
	def _repl(m: re.Match[str]) -> str:
		role = m.group(1)
		body = m.group(2)
		return f":wtrl_{role}:`{body}`"
	s =  mod_docitem.RE_WTRL_MARKUP_BACKTICK_COMPILED.sub(_repl, text)
	return s

def build_sphinx_nodes(ctx : context,objname : str,doc: mod_docitem.docitem_docstring_base) -> List[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| convert a parsed |type|`docitem_docstring_module`, |type|`docitem_docstring_class` or |type|`docitem_docstring_method` into a list of docutils nodes.
		|Must| render section/key/value content into a two-column table with section labels on the left and content on the right.
		|Must| apply role-formatters provided by |type|`context` (labels, types, vars, funcs, methods).
Parameters:
	ctx:
		Rendering context providing inline parser and role-formatters.
	objname:
		Name of the documented object (module, class or method) used in headings.
	doc:
		Parsed docstring tree (representing one of the defined profiles).
Returns:
	List of |type|`docutils.nodes.Node` representing the rendered documentation table.
Raises:
	RuntimeError:
		|May| raise if unexpected section structure is encountered.
Notes:
	Usage:
		This function is typically not called directly. It is called
		by the various |func|`autodoc` functions.
	"""
	node_root: List[nodes.Node] = []
	def parse_text(parent: nodes.Element, text: str) -> List[nodes.Node]:
		return ctx.parse(parent, 0, resolve_markup(text))

# Build table
	node_table = nodes.table(classes=["sdv-meta"])
	node_tgroup = nodes.tgroup(cols=2)
	node_tgroup += nodes.colspec(colwidth=18)
	node_tgroup += nodes.colspec(colwidth=82)
	node_tbody = nodes.tbody()
	node_tgroup += node_tbody

	doc_items = cast(dict[str, Any], doc.items())
	profile = cast(str, cast(Any, doc_items["Preamble"]).items()["profile"].items()[0])
	node_thead = nodes.thead(classes=["sdv-meta-head-" + profile])
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

	for label,item_section in doc_items.items():
# New table row per section
		node_row = nodes.row()

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
				if label1 in ("api","normative_sections","traits","status","scope"):
					node2_bullet_list = nodes.bullet_list()
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()
					sub_items = list(cast(Iterable[str], cast(Any, item_subsection).items()))
					if len(sub_items) > 0:
						if label1 in ("api","normative_sections"):
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
					node2_paragraph.extend(ctx.parse(node2_paragraph,0,ctx.add_role_func(sub_items[0])))
					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				elif label1 in ("general","constructor","requires","ensures","invariants",):
					node2_bullet_list = nodes.bullet_list()
# Content
					for content in cast(Iterable[str], cast(Any, item_subsection).items()):
						node2_list_item = nodes.list_item()
						node2_paragraph = nodes.paragraph()

						node2_paragraph.extend(parse_text(node2_paragraph, content))

						node2_list_item += node2_paragraph
						node2_bullet_list += node2_list_item
				else:
					raise NotImplementedError("dude",label1)

				node_list_item += node1_paragraph
				node_list_item += node2_bullet_list
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Definitions",):
			dl = nodes.definition_list(classes=["wtrl-dfn-list"])
			for term, item_subsection in item_section.items().items():
				dli = nodes.definition_list_item()
# Term
				dt = nodes.term()
				dt.extend(ctx.parse(dt, 0, ctx.add_role_dfn(term)))
				dli += dt
# Definition
				dd = nodes.definition()
				p = nodes.paragraph()
# Content
				p.extend(parse_text(p, " ".join([content for content in item_subsection.items()])))
				dd += p

				dli += dd
				dl += dli
			node_entry += dl
		elif label in ("Terminology",):
			dl = nodes.definition_list(classes=["wtrl-dfn-list"])
			for term, item_subsection in item_section.items().items():
				dli = nodes.definition_list_item()
# Term
				dt = nodes.term()
				dt.extend(ctx.parse(dt, 0, ctx.add_role_dfn(term)))
				dli += dt
# Definition
				dd = nodes.definition()
				p = nodes.paragraph()
# Content
				p.extend(parse_text(p, " ".join([content for content in item_subsection.items()])))
				dd += p

				dli += dd
				dl += dli
			node_entry += dl
		elif label in ("Notes",):
			for term, item_subsection in item_section.items().items():
# Rubric, allows classes=['',...]
				rub = nodes.rubric(classes=['wtrl-note-title'])
				rub.extend(ctx.parse(rub, 0, term))
				node_entry += rub
# Content
				p_def = nodes.paragraph(classes=['wtrl-note-content'])
				p_def.extend(parse_text(p_def, " ".join(item_subsection.items())))
				node_entry += p_def
		elif label in ("Factory"):
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_func(label1)))

				node2_bullet_list = nodes.bullet_list()
# Content
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(parse_text(node2_paragraph, content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Method_overview"):
#			node_paragraph = nodes.paragraph()
#			node_paragraph.extend(ctx.parse(node_paragraph,0,"This section is |normative|. The list below defines the set of public methods."))
#			node_entry += node_paragraph

			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_func(label1)))

				node2_bullet_list = nodes.bullet_list()
# Content
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(parse_text(node2_paragraph, content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Function_overview"):
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_func(label1)))

				node2_bullet_list = nodes.bullet_list()
# Content
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(parse_text(node2_paragraph, content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Class_overview"):
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_type(label1)))

				node2_bullet_list = nodes.bullet_list()
# Content
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(parse_text(node2_paragraph,content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Public_types"):
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_type(label1)))

				node2_bullet_list = nodes.bullet_list()
# Content
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(parse_text(node2_paragraph,content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Public_constants", "Public_variables"):
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_var(label1)))

				node2_bullet_list = nodes.bullet_list()
# Content
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(parse_text(node2_paragraph, content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Parameters"):
#			node_paragraph = nodes.paragraph()
#			node_entry += node_paragraph
			if len(item_section.items()) == 0:
				node_entry.extend(parse_text(node1_paragraph,"|empty|"))
			else:
				node_bullet_list = nodes.bullet_list()
				for label1,item_subsection in item_section.items().items():
					node_list_item = nodes.list_item()
					node1_paragraph = nodes.paragraph()
					node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_var(label1)))

					node2_bullet_list = nodes.bullet_list()
# Content
					for content in item_subsection.items():
						node2_list_item = nodes.list_item()
						node2_paragraph = nodes.paragraph()

						node2_paragraph.extend(parse_text(node2_paragraph, content))

						node2_list_item += node2_paragraph
						node2_bullet_list += node2_list_item
					node1_paragraph += node2_bullet_list

					node_list_item += node1_paragraph
					node_bullet_list += node_list_item

				node_entry += node_bullet_list
		elif label in ("Raises"):
#			node_paragraph = nodes.paragraph()
#			node_entry += node_paragraph
			if len(item_section.items()) == 0:
				node_entry.extend(parse_text(node1_paragraph,"|empty|"))
			else:
				node_bullet_list = nodes.bullet_list()
				for label1,item_subsection in item_section.items().items():
					node_list_item = nodes.list_item()
					node1_paragraph = nodes.paragraph()
					node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_type(label1)))

					node2_bullet_list = nodes.bullet_list()
# Content
					for content in item_subsection.items():
						node2_list_item = nodes.list_item()
						node2_paragraph = nodes.paragraph()

						node2_paragraph.extend(parse_text(node2_paragraph, content))

						node2_list_item += node2_paragraph
						node2_bullet_list += node2_list_item
					node1_paragraph += node2_bullet_list

					node_list_item += node1_paragraph
					node_bullet_list += node_list_item

				node_entry += node_bullet_list
		elif label in ("Description",):
			node1_paragraph = nodes.paragraph()
			restart = True
# Content
			for content in item_section.items():
				if content == "|":
					node_entry += node1_paragraph
					node1_paragraph = nodes.paragraph()
					restart = True
				else:
					node1_paragraph.extend(parse_text(node1_paragraph,("" if restart else " ") + content))
					restart = False
			node_entry += node1_paragraph

		elif label in ("Returns"):
			node1_paragraph = nodes.paragraph()
# Content
			node1_paragraph.extend(parse_text(node1_paragraph," ".join([content for content in item_section.items()])))
			node_entry += node1_paragraph
		elif label in ("Derived_from"):
			node1_paragraph = nodes.paragraph()
# Content
			node1_paragraph.extend(ctx.parse(node1_paragraph,0,", ".join([ctx.add_role_type(content) for content in item_section.items()])))
			node_entry += node1_paragraph
		elif label in ("See_also","Public_classes"):
			node1_paragraph = nodes.paragraph()
# Content
			node1_paragraph.extend(ctx.parse(node1_paragraph,0,", ".join([ctx.add_role_var(content) for content in item_section.items()])))
			node_entry += node1_paragraph
		elif label in ("Public_functions","Public_methods"):
			node1_paragraph = nodes.paragraph()
# Content
			node1_paragraph.extend(ctx.parse(node1_paragraph,0,", ".join([ctx.add_role_func(content) for content in item_section.items()])))
			node_entry += node1_paragraph
		else:
			node_paragraph = nodes.paragraph(text="TBD")
			node_entry += node_paragraph

		node_row += node_entry
		node_tbody += node_row

	return [node_table]

def build_sphinx_nodes_full(ctx : context, class_obj: Any) -> List[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
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
Returns:
	A list of sphinx nodes representing the class and public member documentation.
Raises:
	RuntimeError:
		|Must| raise if something goes wrong parsing a docstring.
	BaseException:
		|Must| forward exceptions from Sphinx
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, class_obj.__name__):
		nodes_out: List[nodes.Node] = []

# Validate class docstring and Method_overview coverage
		if not isinstance(class_obj.__doc__, str):
			raise RuntimeError(f"class {class_obj} has no docstring.")
		top = cast(mod_docitem.docitem_docstring_class,mod_docitem.validate_docstring(tr,class_obj))
		mod_docitem.validate_class_method_coverage(tr,class_obj,top)
		assert isinstance(class_obj.__doc__,str)

		tree_cls = mod_docitem.parse_indent_docstring(tr,class_obj.__doc__)
		di_cls = mod_docitem.docitem_docstring_class()
		di_cls.parse(tr,tree_cls)
		mod_docitem.validate_docstring(tr,class_obj,di_cls)

# Render class block
		nodes_out.extend(build_sphinx_nodes(ctx, class_obj.__name__, di_cls))

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
				if not isinstance(cls_obj.__doc__, str):
					continue
				tree_cls = mod_docitem.parse_indent_docstring(tr,cls_obj.__doc__)

				profile = mod_docitem.get_profile_of_tree(tr,tree_cls)
				di_nested_cls = mod_docitem.docitem_docstring_class()
				di_nested_cls.parse(tr,tree_cls)
				mod_docitem.validate_docstring(tr,cls_obj,di_nested_cls)
#				nodes_out.extend(ctx.build_prolog_method_block(ctx, None, class_obj, cls_obj))
				nodes_out.extend(build_sphinx_nodes(ctx, cls_name, di_cls))

# Render public methods
		if "Public_methods" in di_cls.items():
			pm_node = di_cls._items["Public_methods"]
			assert isinstance(pm_node, mod_docitem.docitem_public_methods)
			if len(pm_node.items()) > 0:
				rubric = nodes.rubric()
				rubric += ctx.parse(rubric, ctx.i_line, f"Public Methods in class {ctx.add_role_type(class_obj.__name__)}")
				nodes_out.append(rubric)
			for meth_name in pm_node.items():
				if not hasattr(class_obj, meth_name):
					continue
				meth_obj = getattr(class_obj, meth_name)
				func_obj = mod_docitem.get_func_obj_from_callable(meth_obj)
				if not func_obj:
					continue
				if not isinstance(func_obj.__doc__, str):
					continue
				tree_m = mod_docitem.parse_indent_docstring(tr,func_obj.__doc__)

				profile = mod_docitem.get_profile_of_tree(tr,tree_m)
				di_m :  mod_docitem.docitem_base
				if profile == "inherited_method":
					di_m = mod_docitem.docitem_docstring_inherited_method()
				else:
					di_m = mod_docitem.docitem_docstring_method()
    
				di_m.parse(tr,tree_m)
				mod_docitem.validate_docstring(tr,func_obj,di_m)
				nodes_out.extend(ctx.build_prolog_method_block(ctx, None, class_obj, func_obj))
				nodes_out.extend(build_sphinx_nodes(ctx, meth_name, di_m))
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
					if not isinstance(func_obj.__doc__, str):
						continue
					tree_m = mod_docitem.parse_indent_docstring(tr,func_obj.__doc__)

					profile = mod_docitem.get_profile_of_tree(tr,tree_m)
					di_prop_meth :  mod_docitem.docitem_base
					if profile == "inherited_method":
						di_prop_meth = mod_docitem.docitem_docstring_inherited_method()
					else:
						di_prop_meth = mod_docitem.docitem_docstring_method()

					di_prop_meth.parse(tr,tree_m)
					mod_docitem.validate_docstring(tr,func_obj,di_prop_meth)
#					nodes_out.extend(ctx.build_prolog_method_block(ctx, None, prop_obj, func_obj))
					nodes_out.extend(build_sphinx_nodes(ctx, func_name, di_prop_meth))
		return nodes_out

#===== Sphinx extension stuff =================================#

def resolve_qualified_name(ctx: context | None, qname: str) -> tuple[object, str, str, list[str]]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
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

def get_signature_tokens(ctx: context, func_qname: str, *, drop_self: bool = True, display_scope: bool = False) -> List[nodes.Node]:
	obj, modname, head_name, tail = resolve_qualified_name(ctx, func_qname)

	display_mod = ".".join([modname] + tail[:-1])
	display_name = head_name

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
			tokens.extend(_tkn(ctx.add_role_label, dflt))

	tokens.extend(_tkn(ctx.add_role_op, ")"))
	tokens.extend(_tkn(ctx.add_role_op, " -> "))
	tokens.extend(_tkn(ctx.add_role_type, format_type(sig.return_annotation)))
	return tokens

# Multiline variant: one parameter per line, hanging indent.
def render_signature_tokens_multiline(ctx: context, func_qname: str, *, drop_self: bool = True, display_scope: bool = True) -> List[nodes.Node]:
	obj, modname, head_name, tail = resolve_qualified_name(ctx, func_qname)

	display_mod = ".".join([modname] + tail[:-1])
	display_name = head_name

	sig = _signature_for(obj)
	sig = _maybe_drop_first_param(sig, drop=drop_self)

	def _tkn(role_fn: Callable[[str], str], text: str) -> List[nodes.Node]:
		markup = role_fn(text)
		m = re.match(r":([A-Za-z0-9_]+):`(.+)`", markup)
		if m:
			role_name, body = m.group(1), m.group(2)
			return [nodes.inline(body, body, classes=[role_name])]
		return [nodes.inline(markup, markup)]

	lines: List[nodes.line] = []
	# header line
	header = nodes.line(classes=["wtrl-signature-head"])
	if display_scope:
		header += _tkn(ctx.add_role_func, display_mod)
		header += _tkn(ctx.add_role_op, ".")
	header += _tkn(ctx.add_role_func, display_name)
	header += _tkn(ctx.add_role_op, "(")
	lines.append(header)

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
			line += _tkn(ctx.add_role_label, dflt)

		lines.append(line)

 # closing line with return annotation
	closing = nodes.line(classes=["wtrl-signature-ret"])
	closing += _tkn(ctx.add_role_op, ")")
	closing += _tkn(ctx.add_role_op, " -> ")
	closing += _tkn(ctx.add_role_type, format_type(sig.return_annotation))
	lines.append(closing)

	# Wrap in a line_block so that Docutils renders each line separately
	line_block = nodes.line_block(classes=["wtrl-signature", "wtrl-signature-multiline"])
	for ln in lines:
		line_block += ln
	return [line_block]

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
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner,parent,ln,txt), lineno)

		module_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_module(module_obj):
			raise RuntimeError(f"{qname} does not resolve to a module.")
		if not isinstance(module_obj.__doc__, str):
			raise RuntimeError(f"{qname} has no docstring.")

		tree_mod = mod_docitem.parse_indent_docstring(tr,module_obj.__doc__)
		di_mod = mod_docitem.docitem_docstring_module()
		di_mod.parse(tr,tree_mod)
		mod_docitem.validate_docstring(tr,module_obj, di_mod)
		return build_sphinx_nodes(ctx, module_obj.__name__, di_mod)

def wtrl_build_autodoc_function_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
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
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)

		function_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not callable(function_obj):
			raise RuntimeError(f"{qname} does not resolve to a callable.")
		if not isinstance(function_obj.__doc__, str):
			raise RuntimeError(f"{qname} has no docstring.")

		tree_meth = mod_docitem.parse_indent_docstring(tr,function_obj.__doc__)
		loc_name = getattr(function_obj, "__name__", qname)
		if mod_docitem.get_profile_of_tree(mod_docitem.tracer(),tree_meth) in ("function","method"):
			di_meth = mod_docitem.docitem_docstring_method()
			di_meth.parse(tr,tree_meth)
			mod_docitem.validate_docstring(tr,function_obj, di_meth)
			return build_sphinx_nodes(ctx, loc_name, di_meth)
		else:
			di_inhmeth = mod_docitem.docitem_docstring_inherited_method()
			di_inhmeth.parse(tr,tree_meth)
			mod_docitem.validate_docstring(tr,function_obj, di_inhmeth)
			return build_sphinx_nodes(ctx, loc_name, di_inhmeth)

def wtrl_build_autodoc_class_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
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
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_class(obj):
			raise RuntimeError(f"{qname} is not a class.")
		if not isinstance(obj.__doc__, str):
			raise RuntimeError(f"{qname} has no docstring.")

		tree_mod = mod_docitem.parse_indent_docstring(tr,obj.__doc__)
		di_node = mod_docitem.docitem_docstring_class()
		di_node.parse(tr,tree_mod)
		mod_docitem.validate_docstring(tr,obj, di_node)
		return build_sphinx_nodes(ctx, qname,di_node)

def wtrl_build_autodoc_class_full_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
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
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_class(obj):
			raise RuntimeError(f"{qname} is not a class.")
		if not isinstance(obj.__doc__, str):
			raise RuntimeError(f"{qname} has no docstring.")
		return build_sphinx_nodes_full(ctx, obj)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		mod_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_module(mod_obj):
			raise RuntimeError(f"{qname} does not resolve to a module.")
		push_current_module(qname, env=ctx.env)
		msg = f"Classes and functions below this point implicitly belong to module/package {ctx.add_role_var(qname)}. "
		parent = nodes.paragraph()
		return parse_inline(inliner, parent, lineno, msg)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		cls_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not mod_docitem.is_obj_class(cls_obj):
			raise RuntimeError(f"{qname} does not resolve to a class.")
		push_current_class(qname, env=ctx.env)
		msg = f"Methods below this point implicitly belong to class {ctx.add_role_var(qname)}."
		parent = nodes.paragraph()
		return parse_inline(inliner, parent, lineno, msg)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, scope_tag):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		push_current_scope(scope_tag, env=ctx.env)
		msg = f"Scope below this point is set to {ctx.add_role_var(scope_tag)}."
		parent = nodes.paragraph()
		return parse_inline(inliner, parent, lineno, msg)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
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
		parent = nodes.paragraph()
		return parse_inline(inliner, parent, lineno, msg)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
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
		parent = nodes.paragraph()
		return parse_inline(inliner, parent, lineno, msg)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, scope_tag):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner,parent,ln,txt), lineno)
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
		parent = nodes.paragraph()
		return parse_inline(inliner,parent,lineno,msg)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return get_signature_tokens(ctx, qname)

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
	Drift:
		Last reviewed on 2026-02-04
	"""
	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return get_signature_tokens(ctx, qname, drop_self=False)

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
	Drift:
		Last reviewed on 2026-02-04
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
	Drift:
		Last reviewed on 2026-02-04
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
.. |May_not| replace:: :wtrl_norm:`May not`
.. |may_not| replace:: :wtrl_norm:`may not`
.. |Self| replace:: :wtrl_value:`Self`
.. |None| replace:: :wtrl_value:`None`
.. |True| replace:: :wtrl_value:`True`
.. |False| replace:: :wtrl_value:`False`
.. |empty| replace:: :wtrl_value:`<empty>`
.. |LoII| replace:: :ref:`LoII <principles>`
.. |LoIO| replace:: :ref:`LoIO <principles>`
.. |SSoT| replace:: :ref:`SSoT <principles>`
.. |BinNorm| replace:: :ref:`BinNorm <principles>`
.. |SoSaC| replace:: :ref:`SoSaC <principles>`
.. |SCaA| replace:: :ref:`SCaA <principles>`
.. |DrPrv| replace:: :ref:`DrPrv <principles>`
.. |MVAuth| replace:: :ref:`MVAuth <principles>`
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
	qname = f"{class_obj.__module__}.{class_obj.__name__}.{meth_obj.__name__}"
	return render_signature_tokens_multiline(ctx, qname, drop_self=True, display_scope=True)

def wtrl_attr_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_attr"])
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

def wtrl_label_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_label"])
	return [node], []

def wtrl_lit_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_lit"])
	return [node], []

def wtrl_opt_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_opt"])
	return [node], []

def wtrl_tag_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_tag"])
	return [node], []

def wtrl_term_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_term"])
	return [node], []

def wtrl_type_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	node = nodes.literal(text, text, classes=["wtrl_type"])
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
# conf.py defines "docitem_context_config" and we tell the app instance,
# We cannot be sure if it exists, but that' how it is named.
	app.add_config_value("docitem_context_config",None,"env")
# Add a hook, so that we know when the builder is ready.
	app.connect("config-inited", lambda app, config: _add_static_path(config, ext_static))
	app.connect("config-inited", _inject_wtrl_prolog)
	app.connect("builder-inited", on_builder_inited)
	app.connect("builder-inited", _add_css_files)
#	app.connect("source-read", on_source_read)

# new: directives
	app.add_directive("wtrl_autodoc_module", WtrlAutodocModuleDirective)
	app.add_directive("wtrl_autodoc_function", WtrlAutodocFunctionDirective)
	app.add_directive("wtrl_autodoc_method", WtrlAutodocFunctionDirective)
	app.add_directive("wtrl_autodoc_class", WtrlAutodocClassDirective)
	app.add_directive("wtrl_autodoc_class_full", WtrlAutodocClassFullDirective)
	app.add_directive("wtrl_push_current_module", WtrlPushCurrentModuleDirective)
	app.add_directive("wtrl_push_current_class", WtrlPushCurrentClassDirective)
	app.add_directive("wtrl_pop_current_module", WtrlPopCurrentModuleDirective)
	app.add_directive("wtrl_pop_current_class", WtrlPopCurrentClassDirective)
	app.add_directive("wtrl_push_current_scope", WtrlPushCurrentScopeDirective)
	app.add_directive("wtrl_pop_current_scope", WtrlPopCurrentScopeDirective)
# only experimental - most likely roles are more appropriate here.
	app.add_directive("wtrl_method_signature", WtrlMethodSignatureDirective)
	app.add_directive("wtrl_function_signature", WtrlFunctionSignatureDirective)
# New. These must be directives since they create a block, not inline text
	app.add_directive("wtrl_method_signature_block", WtrlMethodSignatureBlockDirective)
	app.add_directive("wtrl_function_signature_block", WtrlFunctionSignatureBlockDirective)

	role_map = {
	 "wtrl_attr":wtrl_attr_role,
	 "wtrl_cmd":wtrl_cmd_role,
	 "wtrl_dfn":wtrl_dfn_role,
	 "wtrl_file":wtrl_file_role,
	 "wtrl_func":wtrl_func_role,
	 "wtrl_label":wtrl_label_role,
	 "wtrl_lit":wtrl_lit_role,
	 "wtrl_mod":wtrl_mod_role,
	 "wtrl_norm":wtrl_norm_role,
	 "wtrl_op":wtrl_op_role,
	 "wtrl_opt":wtrl_opt_role,
	 "wtrl_tag":wtrl_tag_role,
	 "wtrl_term":wtrl_term_role,
	 "wtrl_type":wtrl_type_role,
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
		mod_docitem.validate_docstring(tr,context)
		mod_docitem.validate_class_coverage(tr,context)
		mod_docitem.validate_module_coverage(tr,sys.modules[__name__])
