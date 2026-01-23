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
	The module introduces a configurable :wtrl_type:`context` object which encapsulates all
	project-specific presentation logic, including role expansion, symbol rendering, and
	HTML layout decisions. This context is configured by the target project via its
	:wtrl_file:`conf.py` and is intentionally decoupled from the core implementation.
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
		such as :wtrl_type:`paragraph`, :wtrl_type:`section`, or :wtrl_type:`literal`.
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
		|Must| provide a class :wtrl_type:`context` which provides abstract roles to be configured by the target project's :wtrl_file:`conf.py`.
		|Must| provide a function for building Docutils nodes from a module docstring in waterloo format.
		|Must| provide a function for building Docutils nodes from a function docstring in waterloo format.
		|Must| provide a function for building Docutils nodes from a class docstring in waterloo format.
		|Must| provide a function for building Docutils nodes from a class docstring and the class' method docstrings in waterloo format.
		|Must| provide a Docutils role for rendering a function prototype.
		|Must| provide a Docutils role for rendering a method prototype.
		|Must| maintain a stack with semantics "current module" and :wtrl_func:`push`-, :wtrl_func:`pop`-, :wtrl_func:`get`-methods.
		|Must| maintain a stack with semantics "current class" and :wtrl_func:`push`-, :wtrl_func:`pop`-, :wtrl_func:`get`-methods.
		|Must| provide Docutils roles or directives for modifying these stacks.
Public_classes:
	context:
		Internal class, please ignore
Public_functions:
	build_sphinx_nodes:
		Build a list of Docutils nodes from a docstring tree.
	build_sphinx_nodes_full:
		Build a list of Docutils nodes of a class object and its member functions from a docstring tree.
	resolve_qualified_name:
		Analyze a qualified name and return the object it refers to plus resolved name components.

	wtrl_build_autodoc_module_nodes:
		Implementation of role :wtrl_attr:`.. wtrl_autodoc_module::`
	wtrl_build_autodoc_function_nodes:
		Implementation of role :wtrl_attr:`.. wtrl_autodoc_function::`
	wtrl_build_autodoc_class_nodes:
		Implementation of role :wtrl_attr:`.. wtrl_autodoc_class::`
	wtrl_build_autodoc_class_full_nodes:
		Implementation of role :wtrl_attr:`.. wtrl_autodoc_class_full::`

	wtrl_build_push_current_module_nodes:
		Implementation of directive :wtrl_attr:`.. wtrl_push_current_module::`
	wtrl_build_push_current_class_nodes:
		Implementation of directive :wtrl_attr:`.. wtrl_push_current_class::`
	wtrl_build_pop_current_module_nodes:
		Implementation of directive :wtrl_attr:`.. wtrl_pop_current_module::`
	wtrl_build_pop_current_class_nodes:
		Implementation of directive :wtrl_attr:`.. wtrl_pop_current_class::`

	wtrl_method_signature_role:
		Implementation of role :wtrl_lit:`wtrl_method_signature`
	wtrl_function_signature_role:
		Implementation of role :wtrl_lit:`wtrl_function_signature`

	
"""
from __future__ import annotations

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


from typing import Any, Callable, Dict, Generator, Iterable, Iterator, List, Mapping, Protocol, Tuple, Type, TypeAlias, TypeGuard, Union
import inspect
import importlib
import sys,os,re
from docutils import nodes
from pathlib import Path

from docutils.parsers.rst import roles
from docutils.parsers.rst import languages
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.parsers.rst.states import Struct as RstStruct  # type: ignore[attr-defined]
from typing import Sequence, cast, no_type_check

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

try:
	import sdv_doc_docitem
	mod_docitem = sdv_doc_docitem
except ImportError:
	import sdv.doc.waterloo.docitem
	mod_docitem = sdv.doc.waterloo.docitem

__version__ = "0.1.0"

class context:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
Contract:
	general:
		|Must| be able to hold data from both the Sphinx environment and the user-defined configuration in :wtrl_file:`conf.py`.
		|Must| provide a method which allows configuration by means of a simple, documented data structure.
		|Must| provide access to role decorator functions which map plain text to decorated text.
		|Must| provide setters to specify these role decorator functions.
	constructor:
		Internal class, TBD later, complicated sphinx stuff.
Public_methods:
	"""
	def __init__(self,parse_inline : Callable[[nodes.Element, int, str], List[nodes.Node]],lineno: int) -> None:
		self.parse = parse_inline
		self.i_line = lineno
		self.env = None
		self.add_role_dfn = lambda t:f":wtrl_dfn:`{t}`"
		self.add_role_func = lambda t:f":wtrl_func:`{t}`"
		self.add_role_label = lambda t:f":wtrl_label:`{t}`"
		self.add_role_method = lambda t:f":wtrl_func:`{t}`"
		self.add_role_op = lambda t:f":wtrl_op:`{t}`"
		self.add_role_type = lambda t:f":wtrl_type:`{t}`"
		self.add_role_value = lambda t:f":wtrl_value:`{t}`"
		self.add_role_var = lambda t:f":wtrl_var:`{t}`"
		self.build_prolog_public_methods : Callable[[context],List[nodes.Node]] = lambda ctx: []
		self.build_prolog_method_block : Callable[[context,nodes.Node | None,object,object],List[nodes.Node]] = lambda ctx, parent, cls, meth: []
		
	def set_add_role_dfn(self,c : Callable[[str],str]) -> None:
		self.add_role_dfn = c
	def set_add_role_func(self,c : Callable[[str],str]) -> None:
		self.add_role_func = c
	def set_add_role_label(self,c : Callable[[str],str]) -> None:
		self.add_role_label = c
	def set_add_role_method(self,c : Callable[[str],str]) -> None:
		self.add_role_method = c
	def set_add_role_op(self,c : Callable[[str],str]) -> None:
		self.add_role_op = c
	def set_add_role_type(self,c : Callable[[str],str]) -> None:
		self.add_role_type = c
	def set_add_role_var(self,c : Callable[[str],str]) -> None:
		self.add_role_var = c
	def set_add_role_value(self,c : Callable[[str],str]) -> None:
		self.add_role_value = c
	def set_build_prolog_public_methods(self,c : Callable[[context],List[nodes.Node]]) -> None:
		self.build_prolog_public_methods = c
	def set_build_prolog_method_block(self,c : Callable[[context,nodes.Node | None,object,object],List[nodes.Node]]) -> None:
		self.build_prolog_method_block = c
	def apply_config(self, cfg: dict[str,str]) -> None:
		def mk_role(role : str) -> Callable[[str],str]:
			return lambda t: f":{role}:`{t}`"
		self.set_add_role_dfn(mk_role(cfg["role_dfn"]))
		self.set_add_role_func(mk_role(cfg["role_func"]))
		self.set_add_role_label(mk_role(cfg["role_label"]))
		self.set_add_role_method(mk_role(cfg["role_method"]))
		self.set_add_role_op(mk_role(cfg["role_op"]))
		self.set_add_role_type(mk_role(cfg["role_type"]))
		self.set_add_role_value(mk_role(cfg["role_value"]))
		self.set_add_role_var(mk_role(cfg["role_var"]))
		self.set_build_prolog_public_methods(import_by_path(cfg["prolog_public_methods"]))
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
	if len(params) <= 1:
		return inspect.Signature(parameters=[], return_annotation=sig.return_annotation)
	return inspect.Signature(parameters=params[1:], return_annotation=sig.return_annotation)

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

#==============================================================#

# This is going to be the official markup-resolver.
def resolve_markup(text : str) -> str:
	return text.replace("|term|",":emphasis:")

def build_sphinx_nodes(ctx : context,objname : str,doc: mod_docitem.docitem_docstring_module | mod_docitem.docitem_docstring_class | mod_docitem.docitem_docstring_method | mod_docitem.docitem_docstring_inherited_method) -> List[nodes.Node]:
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
		|Must| convert a parsed :wtrl_type:`docitem_docstring_module`, :wtrl_type:`docitem_docstring_class` or :wtrl_type:`docitem_docstring_method` into a list of docutils nodes.
		|Must| render section/key/value content into a two-column table with section labels on the left and content on the right.
		|Must| apply role-formatters provided by :wtrl_type:`context` (labels, types, vars, funcs, methods).
Parameters:
	ctx:
		Rendering context providing inline parser and role-formatters.
	objname:
		Name of the documented object (module, class or method) used in headings.
	doc:
		Parsed docstring tree (:wtrl_type:`docitem_docstring_module`, :wtrl_type:`docitem_docstring_class` or :wtrl_type:`docitem_docstring_method`).
Returns:
	List of :wtrl_type:`docutils.nodes.Node` representing the rendered documentation table.
Raises:
	RuntimeError:
		|May| raise if unexpected section structure is encountered.
Notes:
	Usage:
		This function is typically not called directly. It is called
		by the various :wtrl_func:`autodoc` functions.
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
		node_paragraph.extend(ctx.parse(node_paragraph,0,ctx.add_role_label(cast(Any, item_section).label())))
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
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_label(cast(Any, item_subsection).label())))
				if label1 in ("api","normative_sections","traits"):
					node2_bullet_list = nodes.bullet_list()
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()
					sub_items = list(cast(Iterable[str], cast(Any, item_subsection).items()))
					if len(sub_items) > 0:
						if label1 in ("api","normative_sections"):
							node2_paragraph.extend(ctx.parse(node2_paragraph,0,", ".join([ctx.add_role_label(content) for content in sub_items])))
						elif label1 in ("traits",):
							node2_paragraph.extend(ctx.parse(node2_paragraph,0,", ".join([ctx.add_role_value(content) for content in sub_items])))
					else:
						node2_paragraph.extend(ctx.parse(node1_paragraph,0,"|empty|"))
					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				elif label1 in ("base"):
					node2_bullet_list = nodes.bullet_list()
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()
					sub_items = list(cast(Iterable[str], cast(Any, item_subsection).items()))
# Always one entry.
					node2_paragraph.extend(ctx.parse(node2_paragraph,0,ctx.add_role_func(sub_items[0])))
					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				else:

					node2_bullet_list = nodes.bullet_list()
					for content in cast(Iterable[str], cast(Any, item_subsection).items()):
						node2_list_item = nodes.list_item()
						node2_paragraph = nodes.paragraph()

						node2_paragraph.extend(parse_text(node2_paragraph, content))

						node2_list_item += node2_paragraph
						node2_bullet_list += node2_list_item

				node_list_item += node1_paragraph
				node_list_item += node2_bullet_list
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Definitions",):
			node_bullet_list = nodes.bullet_list()
			for term, item_subsection in item_section.items().items():
				li = nodes.list_item()

				p_term = nodes.paragraph()
				p_term.extend(ctx.parse(p_term, 0, ctx.add_role_dfn(term)))
				li += p_term

				p_def = nodes.paragraph()
				p_def.extend(parse_text(p_def, " ".join(item_subsection.items())))
				li += p_def
				node_bullet_list += li
			node_entry += node_bullet_list
		elif label in ("Terminology",):
			node_bullet_list = nodes.bullet_list()
			for term, item_subsection in item_section.items().items():
				li = nodes.list_item()

				p_term = nodes.paragraph()
				p_term.extend(ctx.parse(p_term, 0, ctx.add_role_dfn(term)))
				li += p_term

				p_def = nodes.paragraph()
				p_def.extend(parse_text(p_def, " ".join(item_subsection.items())))
				li += p_def
				node_bullet_list += li
			node_entry += node_bullet_list
		elif label in ("Factory"):
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_func(label1)))

				node2_bullet_list = nodes.bullet_list()
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
		elif label in ("Public_methods"):
#			node_paragraph = nodes.paragraph()
#			node_paragraph.extend(ctx.parse(node_paragraph,0,"This section is |normative|. The list below defines the set of public methods."))
#			node_entry += node_paragraph

			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_method(label1)))

				node2_bullet_list = nodes.bullet_list()
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
		elif label in ("Public_functions"):
#			node_paragraph = nodes.paragraph()
#			node_paragraph.extend(ctx.parse(node_paragraph,0,"This section is |normative|. The list below defines the set of public functions."))
#			node_entry += node_paragraph

			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_func(label1)))

				node2_bullet_list = nodes.bullet_list()
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
		elif label in ("Public_classes"):
#			node_paragraph = nodes.paragraph()
#			node_paragraph.extend(ctx.parse(node_paragraph,0,"This section is |normative|. The list below defines the set of public classes."))
#			node_entry += node_paragraph

			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_type(label1)))

				node2_bullet_list = nodes.bullet_list()
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(ctx.parse(node2_paragraph,0,content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Public_types"):
#			node_paragraph = nodes.paragraph()
#			node_paragraph.extend(ctx.parse(node_paragraph,0,"This section is |normative|. The list below defines the set of public types / type aliases."))
#			node_entry += node_paragraph

			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_type(label1)))

				node2_bullet_list = nodes.bullet_list()
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(ctx.parse(node2_paragraph,0,content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Public_constants"):
#			node_paragraph = nodes.paragraph()
#			node_paragraph.extend(parse_text(node_paragraph,"This section is |normative|. The list below defines the set of public constants."))
#			node_entry += node_paragraph

			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_var(label1)))

				node2_bullet_list = nodes.bullet_list()
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
		elif label in ("Notes"):
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_label(label1)))

				node2_paragraph = nodes.paragraph()
				for content in item_subsection.items():
					node2_paragraph.extend(parse_text(node2_paragraph, content))
				node1_paragraph += node2_paragraph

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
		elif label in ("Description",):
			node1_paragraph = nodes.paragraph()
			restart = True
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
			node1_paragraph.extend(parse_text(node1_paragraph," ".join([content for content in item_section.items()])))
			node_entry += node1_paragraph
		elif label in ("Derived_from"):
			node1_paragraph = nodes.paragraph()
			node1_paragraph.extend(ctx.parse(node1_paragraph,0,", ".join([ctx.add_role_type(content) for content in item_section.items()])))
			node_entry += node1_paragraph
		elif label in ("See_also"):
			node1_paragraph = nodes.paragraph()
			node1_paragraph.extend(ctx.parse(node1_paragraph,0,", ".join([ctx.add_role_var(content) for content in item_section.items()])))
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
		The list |must| contain nodes produced by :wtrl_func:`ctx.build_prolog_public_methods`.
		For each public method as indicated by the class' normative docstring:
		1. The list |must| contain nodes produced by :wtrl_func:`ctx.build_prolog_method_block`.
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

# Validate class docstring and Public_methods coverage
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

# Render public methods
		if "Public_methods" in di_cls.items():
			nodes_out.extend(ctx.build_prolog_public_methods(ctx))
			pm_node = di_cls._items["Public_methods"]
			assert isinstance(pm_node, mod_docitem.docitem_public_methods)
			for meth_name in pm_node.items().keys():
				if not hasattr(class_obj, meth_name):
					continue
				meth_obj = getattr(class_obj, meth_name)
				if inspect.ismethod(meth_obj):
					func_obj = meth_obj.__func__
				elif inspect.isfunction(meth_obj):
					func_obj = meth_obj
				elif isinstance(meth_obj, staticmethod):
					func_obj = meth_obj.__func__
				elif isinstance(meth_obj, classmethod):
					func_obj = meth_obj.__func__
				else:
					continue
				if not isinstance(func_obj.__doc__, str):
					continue
				tree_m = mod_docitem.parse_indent_docstring(tr,func_obj.__doc__)

				profile = mod_docitem.get_tree_of_subsection(tr,tree_m,"Preamble","profile")[0]
				di_m :  mod_docitem.docitem_base
				if profile == "inherited_method":
					di_m = mod_docitem.docitem_docstring_inherited_method()
				else:
					di_m = mod_docitem.docitem_docstring_method()
				
				di_m.parse(tr,tree_m)
				mod_docitem.validate_docstring(tr,func_obj,di_m)
				nodes_out.extend(ctx.build_prolog_method_block(ctx, None, class_obj, func_obj))
				nodes_out.extend(build_sphinx_nodes(ctx, meth_name, di_m))
	
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
		|Must| resolve the qualified name :wtrl_var:`qname` using current module/class context in :wtrl_var:`ctx` when present.
		|Must| try to import the resolved object as criterion that resolution succeeded (see section :wtrl_label:`Raises`)
		|Must| try fully qualified forms in this order: current module + current class + :wtrl_var:`qname`, current module + :wtrl_var:`qname`, then :wtrl_var:`qname` as given.
Parameters:
	ctx:
		The context which provides current module and current class.
	qname:
		The qualified name to resolve.
Returns:
	|Must| return a tuple :wtrl_type:`(obj, module_name, head_name, tail_parts)` where
	:wtrl_var:`obj` is the resolved object, :wtrl_var:`module_name` is the imported module name,
	:wtrl_var:`head_name` is the last attribute component, and :wtrl_var:`tail_parts`
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

class WtrlMethodSignatureDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_method_signature_nodes)

class WtrlFunctionSignatureDirective(WtrlDirectiveBase):
	def run(self) -> list[nodes.Node]:
		return self._run(wtrl_build_function_signature_nodes)

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
		|Must| resolve the dotted module name :wtrl_var:`text` to a Python module object taking into account the current module state.
		|Must| parse and validate the module's Waterloo docstring.
		|Must| render the parsed docstring into Docutils nodes using the configured context.
Description:
	Implementation of role :wtrl_attr:`:wtrl_autodoc_module:`.
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
	The list of generated :wtrl_type:`docutils.nodes.Node` representing the module doumentation.
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
		if not inspect.ismodule(module_obj):
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
		|Must| resolve the dotted function name :wtrl_var:`qname` to a callable taking into account the current module/class state.
		|Must| parse and validate the function's Waterloo docstring.
		|Must| render the parsed docstring into Docutils nodes using the configured context.
Description:
	Implementation of directive :wtrl_attr:`.. wtrl_autodoc_function::`.
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
	List of generated :wtrl_type:`docutils.nodes.Node`.
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

		tree_mod = mod_docitem.parse_indent_docstring(tr,function_obj.__doc__)
		di_mod = mod_docitem.docitem_docstring_method()
		di_mod.parse(tr,tree_mod)
		mod_docitem.validate_docstring(tr,function_obj, di_mod)

		loc_name = getattr(function_obj, "__name__", qname)
		return build_sphinx_nodes(ctx, loc_name, di_mod)

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
		|Must| resolve the dotted class name :wtrl_var:`qname` to a class taking into account the current module/class state.
		|Must| parse and validate the class' Waterloo docstring.
		|Must| render the parsed docstring into Docutils nodes using the configured context.
Description:
	Implementation of directive :wtrl_attr:`.. wtrl_autodoc_class::`.
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
	List of generated :wtrl_type:`docutils.nodes.Node`.
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
		if not inspect.isclass(obj):
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
	Implementation of directive :wtrl_attr:`.. wtrl_autodoc_class_full::`.
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
	List of generated :wtrl_type:`docutils.nodes.Node`.
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
		if not inspect.isclass(obj):
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
		|Must| push the qualified module name in :wtrl_var:`text` to the module stack, which makes it the new current module.
		|Must| resolve :wtrl_var:`qname`.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to :wtrl_file:`stdout`.
Description:
	Implementation of directive :wtrl_attr:`.. wtrl_push_current_module::`.
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
	The list of generated :wtrl_type:`docutils.nodes.Node` describing the resulting default module state.
Raises:
	RuntimeError:
		|Must| raise if :wtrl_var:`qname` does not resolve to a module.
	BaseException:
		|May| propagate exceptions from :wtrl_func:`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		mod_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not inspect.ismodule(mod_obj):
			raise RuntimeError(f"{qname} does not resolve to a module.")
		push_current_module(qname, env=ctx.env)
		msg = f"Classes and functions below this point implicitly belong to module/package {ctx.add_role_var(qname)}."
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
		|Must| push the qualified class name in :wtrl_var:`text` to the class stack, which makes it the new current class.
		|Must| resolve :wtrl_var:`qname`.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to :wtrl_file:`stdout`.
Description:
	Implementation of directive :wtrl_attr:`.. wtrl_push_current_class::`.
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
	The list of generated :wtrl_type:`docutils.nodes.Node` describing the resulting default module state.
Raises:
	RuntimeError:
		|Must| raise if :wtrl_var:`qname` does not resolve to a class.
	BaseException:
		|May| propagate exceptions from :wtrl_func:`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		cls_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not inspect.isclass(cls_obj):
			raise RuntimeError(f"{qname} does not resolve to a class.")
		push_current_class(qname, env=ctx.env)
		msg = f"Methods below this point implicitly belong to class {ctx.add_role_var(qname)}."
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
		|Must| compare the qualified module name in :wtrl_var:`qname` to the top of the module stack and raise an exception in case of mismatch.
		|Must| resolve :wtrl_var:`qname` against the current module/class context.
		|Must| pop one element from the module stack.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to :wtrl_file:`stdout`.
Description:
	Implementation of directive :wtrl_attr:`.. wtrl_pop_current_module::`.
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
	The list of generated :wtrl_type:`docutils.nodes.Node` describing the resulting default module state.
Raises:
	RuntimeError:
		|Must| raise on the attempt to access an element from an empty stack.
		|Must| raise if :wtrl_var:`qname` does not resolve to a module.
	BaseException:
		|May| propagate exceptions from :wtrl_func:`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		mod_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not inspect.ismodule(mod_obj):
			raise RuntimeError(f"{qname} does not resolve to a module.")
		text_top = get_current_module(ctx.env)
		if text_top != qname:
			raise RuntimeError(f"class stack push/pop mismatch, expected {text_top} got {qname}.")
		pop_current_module(ctx.env)
		if has_current_module(ctx.env):
			new_top = get_current_module(ctx.env)
			msg = f"Default module qualifier {ctx.add_role_var(text_top)} ends here. New default: {ctx.add_role_var(new_top)}."
		else:
			msg = f"Default module qualifier {ctx.add_role_var(text_top)} ends here. No default module active."
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
		|Must| compare the qualified class name in :wtrl_var:`qname` to the top of the class stack and raise an exception in case of mismatch.
		|Must| resolve :wtrl_var:`qname` against the current module/class context.
		|Must| pop one element from the module stack.
		|Must| build a list of Docutils nodes which represent a message about the changed state in the document.
		|May| write a log message to :wtrl_file:`stdout`.
Description:
	Implementation of directive :wtrl_attr:`.. wtrl_pop_current_module::`.
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
	The list of generated :wtrl_type:`docutils.nodes.Node` describing the resulting default module state.
Raises:
	RuntimeError:
		|Must| raise on the attempt to access an element from an empty stack.
		|Must| raise if :wtrl_var:`qname` does not resolve to a class.
	BaseException:
		|May| propagate exceptions from :wtrl_func:`resolve_qualified_name`.
		|May| propagate exceptions from within Sphinx or Docutils.
	"""
	tr = mod_docitem.tracer()
	with mod_docitem.traced_section(tr, qname):
		ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
		cls_obj, _, _, _ = resolve_qualified_name(ctx, qname)
		if not inspect.isclass(cls_obj):
			raise RuntimeError(f"{qname} does not resolve to a class.")
		text_top = get_current_class(ctx.env)
		if text_top != qname:
			raise RuntimeError(f"class stack push/pop mismatch, expected {text_top} got {qname}.")
		pop_current_class(ctx.env)
		if has_current_class(ctx.env):
			new_top = get_current_class(ctx.env)
			msg = f"Default class qualifier {ctx.add_role_var(text_top)} ends here. New default: {ctx.add_role_var(new_top)}."
		else:
			msg = f"Default class qualifier {ctx.add_role_var(text_top)} ends here. No default class active."
		parent = nodes.paragraph()
		return parse_inline(inliner, parent, lineno, msg)

def wtrl_build_method_signature_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:

	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return get_signature_tokens(ctx, qname)

def wtrl_build_function_signature_nodes(app: SphinxAppProtocol | Any, inliner: InlinerProtocol, lineno: int, qname: str) -> list[nodes.Node]:

	ctx = make_context(app, lambda parent, ln, txt: parse_inline(inliner, parent, ln, txt), lineno)
	return get_signature_tokens(ctx, qname, drop_self=False)

#----- end node builder functions -----------------------------#

def wtrl_method_signature_role(name: str,rawtext: str,text: str,lineno: int,inliner: InlinerProtocol,options: dict[str, Any] | None=None,content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
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
		|Must| carefully analyze the signature of the method addressed by :wtrl_var:`text`.
		|Must| produce a role-decorated version of the method signature of the method.
Description:
	Implementation of role :wtrl_attr:`:wtrl_method_signature:`.
Parameters:
	name:
		The role name as passed by Docutils.
	rawtext:
		The entire markup snippet including backticks.
	text:
		The qualified method name to decorate.
	lineno:
		Line number in the source document.
	inliner:
		The Docutils inliner instance.
	options:
		Role options provided by the caller.
	content:
		Unused role content (always empty).
Returns:
	Two-element tuple containing the list of generated :wtrl_type:`docutils.nodes.Node` and a list of system messages (always empty).
Raises:
	RuntimeError:
		|May| raise if the qualified method name cannot be resolved.
	"""
	out = wtrl_build_method_signature_nodes(inliner.document.settings.env.app, inliner, lineno, text)
	return out, []

def wtrl_function_signature_role(name: str,rawtext: str,text: str,lineno: int,inliner: InlinerProtocol,options: dict[str, Any] | None=None,content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
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
		|Must| carefully analyze the signature of the function addressed by :wtrl_var:`text`.
		|Must| produce a role-decorated version of the function signature of the function.
Description:
	Implementation of role :wtrl_attr:`:wtrl_function_signature:`.
Parameters:
	name:
		The role name as passed by Docutils.
	rawtext:
		The entire markup snippet including backticks.
	text:
		The qualified function name to decorate.
	lineno:
		Line number in the source document.
	inliner:
		The Docutils inliner instance.
	options:
		Role options provided by the caller.
	content:
		Unused role content (always empty).
Returns:
	Two-element tuple containing the list of generated :wtrl_type:`docutils.nodes.Node` and a list of system messages (always empty).
Raises:
	RuntimeError:
		|May| raise if the qualified function name cannot be resolved.
	"""
	out = wtrl_build_function_signature_nodes(inliner.document.settings.env.app, inliner, lineno, text)
	return out, []

def on_builder_inited(app: Any) -> None:
	print("ON_BUILDER_INITED")
	cfg = app.config.docitem_context_config
	if cfg is None:
		print("ON_BUILDER_INITED - None (a)")
		return
	app.docitem_context_configurator = cfg
	print(f"ON_BUILDER_INITED - {cfg} (b)")

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
"""

_SENTINEL = "\n.. wtrl-prolog:begin\n"

def _inject_wtrl_prolog(app: Any, config :Any) -> None:
# idempotent: nicht doppelt einfuegen
	current = getattr(config, "rst_prolog", "") or ""
	if "wtrl-prolog:begin" in current:
		return
	config.rst_prolog = current + _SENTINEL + WTRL_PROLOG + "\n.. wtrl-prolog:end\n"

#----- helpers ------------------------------------------------#

def build_prolog_public_methods(ctx: context) -> List[nodes.Node]:
	return [nodes.rubric(text="Public methods")]

def build_prolog_method_block(ctx: context,parent : nodes.Element,class_obj: type[object],meth_obj : Callable[..., Any]) -> List[nodes.Node]:
	return ctx.parse(parent,0,f":wtrl_method_signature:`{class_obj.__name__}.{meth_obj.__name__}`")

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

def wtrl_var_type_role(name: str, rawtext: str, text: str, lineno: int, inliner: InlinerProtocol, options: Mapping[str,Any] | None=None, content: list[str] | None=None) -> tuple[List[nodes.Node], list[nodes.Node]]:
	options = {} if options is None else options
	content = [] if content is None else content

	if ":" not in text:
		msg = inliner.reporter.error(
			f"wtrl_var_type expects 'var:type', got '{text}'",
			line=lineno
		)
		return [msg], []

	var, type_ = text.split(":", 1)

	node = nodes.inline('', '', classes=["wtrl_var_type"])
	node += nodes.inline(var, var, classes=["wtrl_var"])
	node += nodes.inline(": ", ": ", classes=["wtrl_op"])
	node += nodes.inline(type_, type_, classes=["wtrl_type"])
	return [node], []

def _add_static_path(config, path):
	lst = list(getattr(config, "html_static_path", []) or [])
	if path not in lst:
		lst.append(path)
	config.html_static_path = lst

def _add_css_files(app):
	app.add_css_file("common_styles.css")
	app.add_css_file("alabaster_waterloo.css")

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
# only experimental - most likely roles are more appropriate here.
	app.add_directive("wtrl_method_signature", WtrlMethodSignatureDirective)
	app.add_directive("wtrl_function_signature", WtrlFunctionSignatureDirective)
# roles
	roles.register_local_role("wtrl_method_signature", cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_method_signature_role))
	roles.register_local_role("wtrl_function_signature", cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_function_signature_role))

	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_attr_role)
	roles.register_local_role("wtrl_attr", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_cmd_role)
	roles.register_local_role("wtrl_cmd", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_dfn_role)
	roles.register_local_role("wtrl_dfn", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_file_role)
	roles.register_local_role("wtrl_file", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_func_role)
	roles.register_local_role("wtrl_func", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_label_role)
	roles.register_local_role("wtrl_label", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_lit_role)
	roles.register_local_role("wtrl_lit", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_mod_role)
	roles.register_local_role("wtrl_mod", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_norm_role)
	roles.register_local_role("wtrl_norm", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_op_role)
	roles.register_local_role("wtrl_op", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_opt_role)
	roles.register_local_role("wtrl_opt", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_tag_role)
	roles.register_local_role("wtrl_tag", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_type_role)
	roles.register_local_role("wtrl_type", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_value_role)
	roles.register_local_role("wtrl_value", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_var_role)
	roles.register_local_role("wtrl_var", role_reg)
	role_reg = cast(Callable[..., tuple[Sequence[nodes.reference], Sequence[nodes.reference]]], wtrl_var_type_role)
	roles.register_local_role("wtrl_var_type", role_reg)

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
