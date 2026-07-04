"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions, Public_types
	scope:
		public
Contract:
	general:
		|Must| provide converter functions for all flavours and formats in |mod|`sdv.doc.waterloo.helper`.
Public_functions:
	to_node_legend_json,
	to_node_docstring_tree_json,
	to_node_signature_json,
	to_string_md,
	build_node_json
Public_types:
	WtrlJsonNode_t:
		Type for JSON nodes. This type |must| be public because |func|`to_node_docstring_tree_json` and |func|`to_node_signature_json` are.
"""

from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, Optional, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast
import re,inspect

from sdv.doc.waterloo.docitem import *

#===== Constants ==============================================#
MAP_NORM_KEYWORD_BY_FLAVOUR: Final[Dict[str,str]] = {
	"Must": "MUST",
	"must": "MUST",
	"Must_not": "MUST NOT",
	"must_not": "MUST NOT",
	"Should": "SHOULD",
	"should": "SHOULD",
	"Should_not": "SHOULD NOT",
	"should_not": "SHOULD NOT",
	"May": "MAY",
	"may": "MAY",
}

ROLES_LEGEND: Final[Dict[str, str]] = {
	"attr": "Attribute name",
	"cmd": "Shell or CLI command",
	"class": "Class name",
	"dfn": "Definition of a term",
	"file": "File or path",
	"func": "Function or callable",
	"key": "Key on the keyboard",
	"label": "Section/Subsection label",
	"lit": "Literal text or code",
	"mod": "Module name",
	"norm": "Normativity keyword used as metadata",
	"op": "Operator symbol",
	"opt": "Command-line option or flag",
	"pkg": "Package name",
	"url": "URL",
	"tag": "Tag or marker",
	"term": "Domain-specific term",
	"type": "Type name or annotation",
	"value": "Concrete value",
	"var": "Variable name",
	"var_type": "Variable and type, like 'var:type'",
}

#===== Type Checking ==========================================#
WtrlJsonNode_t: TypeAlias = Dict[str, "WtrlJsonNode_t"] | List["WtrlJsonNode_t"] | str | int | float | bool | None

#===== Helpers ================================================#

def _render_token(txt: str, flavour: Flavour) -> str:
	"""
	Replace Waterloo normativity tokens depending on flavour.
	RAW: keep original
	RFC_2119: drop pipes and upper-case keywords
	MARKDOWN: drop pipes and render keywords bold + upper-case
	"""
	if flavour == Flavour.RAW:
		return txt

	def repl(m: re.Match[str]) -> str:
		word = m.group(1)
		if word not in MAP_NORM_KEYWORD_BY_FLAVOUR:
			# leave untouched if it's not a normativity keyword (e.g. |lit|)
			return m.group(0)
		upper = MAP_NORM_KEYWORD_BY_FLAVOUR[word]
		if flavour == Flavour.MARKDOWN:
			return f"**{upper}**"
		return upper

	return re.sub(r"\|([A-Za-z_]+)\|", repl, txt)

#===== JSON ===================================================#

def to_node_signature_json(obj: object) -> dict[str, WtrlJsonNode_t]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
		status:
			experimental
	Contract:
		general:
			|Must| render a JSON object as configured in |var|`config`, representing\
			the signature of the callable |var|`obj`.
			The root **property** |must| be |attr|`signature`.
			This object |must| contain the **keys** |attr|`text`, |attr|`parameters`,\
			and |attr|`returns`.
			|attr|`text` |must| be a string representation of the signature.
			|attr|`parameters` |must| be an **array** of objects, each containing:
			|attr|`name`: The parameter identifier string.
			|attr|`kind`: The Python parameter mode as a string constant.
			|attr|`annotation`: The type hint string or |value|`null`.
			|attr|`default`: The default value as a string or |value|`null`.
			The **key** |attr|`returns` |must| represent the return type.
	Parameters:
		obj:
			The callable whose signature is to be inspected and rendered.
	Returns:
		The generated JSON node
	Raises:
		TypeError:
			|Must| be raised if |var|`obj` is not callable or if the signature 
			cannot be inspected.
		ValueError:
			|May| be raised if the signature includes parameter kinds that 
			cannot be serialized.
		Exception:
			|May| propagate exceptions from |func|`inspect.signature` or |func|`repr`\
			during default value rendering; callers should treat these as unexpected errors.
	Notes:
		Standard values for "kind":
			Derived from |type|`inspect.Parameter`:\
			|value|`POSITIONAL_ONLY`, |value|`POSITIONAL_OR_KEYWORD`,\
			|value|`VAR_POSITIONAL`, |value|`KEYWORD_ONLY`, |value|`VAR_KEYWORD`
	"""
	if not callable(obj):
		raise TypeError(f"Object of type {type(obj)} is not callable.")
	try:
		sig = inspect.signature(obj)
	except (ValueError, TypeError) as e:
		raise TypeError(f"Could not inspect signature: {e}")

	param_values = list(sig.parameters.values())

# Parameter-Liste aufbauen
	params_list: List[WtrlJsonNode_t] = []
	for i_param in range(len(param_values)):
		param = param_values[i_param]
# Omit parameter decription for initial parameter self or cls.
		if i_param == 0 and param.name in ("self","cls"):
			continue
		params_list.append({
			"name": param.name,
			"kind": param.kind.name,  # Liefert POSITIONAL_OR_KEYWORD, etc.
			"annotation": (
				param.annotation.__name__ 
				if hasattr(param.annotation, "__name__") else str(param.annotation)
				) if param.annotation is not inspect.Parameter.empty else None,
			"default": (
				repr(param.default) 
				if param.default is not inspect.Parameter.empty else None
				)
			})

# Gesamte Struktur
	display_name = get_obj_name(obj)
	if display_name == "__init__" and hasattr(obj, "__qualname__"):
		display_name = get_obj_name(obj)

	signature_data: dict[str, WtrlJsonNode_t] = {
		"signature": {
			"text": f"{display_name}{sig}",
			"parameters": params_list,
			"returns": (
				sig.return_annotation.__name__ 
				if hasattr(sig.return_annotation, "__name__") else str(sig.return_annotation)
				) if sig.return_annotation is not inspect.Signature.empty else None
			}
		}
	return signature_data

def build_node_section_json(label : str,node: docitem_base, flavour: Flavour) -> WtrlJsonNode_t:
	m : WtrlJsonNode_t
	if isinstance(node,docitem_map_base):
		m = {}
		for label in node.items():
			m[label] = build_node_section_json(label,node.item(label),flavour)
	elif isinstance(node,docitem_list_base):
		if label in SINGLE_STRING_SECTIONS:
			m = _render_token(node.item_by_index(0),flavour)
		else:
			m = cast(WtrlJsonNode_t,[_render_token(item,flavour) for item in node.items()])
	else:
		raise NotImplementedError()
	return m

def build_node_json(node_docstring: docitem_docstring_base, flavour: Flavour) -> WtrlJsonNode_t:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
		status:
			experimental
	Contract:
		general:
			|Must| build a JSON node from the Abstract Syntax Tree |var|`node_docstring`.
			|Must| convert Normativity Keywords in free-form text according to the given flavour.
		requires:
			|var|`node_docstring` |must| be a formatlly correct AST node representing\
			the docstring item of a module, class, function, method, or inherited method.
	Parameters:
		node_docstring:
			The AST node
		flavour:
			Normativity Keyword style.
	Returns:
		The JSON node, a |type|`dict` in our case, which represents the AST node.
	Raises:
		NotImplementedError:
			|May| raise in case |var|`node_docstring` has some unexpected type.
		BaseException:
			|May| propagate from underlying modules such as |mod|`re`.
	"""
	
	m: dict[str, WtrlJsonNode_t] = {}
	for label in node_docstring.items():
		if label == "Definitions":
			node_definitions = node_docstring.item(label)
			if isinstance(node_definitions, docitem_definitions):
				inherited_terms = [str(x) for x in node_definitions.inherited() if str(x).strip()]
				if inherited_terms:
	# Keep inherited definitions separate from local Definitions content.
	# `source` is filled by the renderer (waterlint) which knows object context.
					m["definitions_inherited_from_module"] = {
						"source": None,
						"terms": cast(WtrlJsonNode_t, [_render_token(t, flavour) for t in inherited_terms]),
					}
				def_map: dict[str, WtrlJsonNode_t] = {}
				for term, variations in node_definitions.map_term_to_variations().items():
					node_term = node_definitions.item(term)
					text_node = build_node_section_json(term, node_term, flavour)
					def_map[term] = {
						"variations": cast(WtrlJsonNode_t, [_render_token(v, flavour) for v in variations]),
						"text": text_node,
					}
				m[label] = def_map
				continue
		m[label] = build_node_section_json(label,node_docstring.item(label),flavour)
	return m

def to_node_docstring_tree_json(tree: DocstringTree, flavour: Flavour) -> WtrlJsonNode_t:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises, See_also
		scope:
			public
		status:
			experimental
	Contract:
		general:
			|Must| render the tree as JSON-Node using the given flavour.
			|Must| reproduce the tree structure by appropriate subobjects in JSON.
			In RFC_2199 flavour, Normativity Keywords |must| be capitalized\
			and the pipe delimiters |must| be dropped.
			In RAW flavour, Normativity Keywords |must| be rendered without\
			modification, i.e. including pipe delimiters.
			In MARKUP flavour, Normativity Keywords |must| be rendered with\
			double asterisk |lit|`**...**` instead of pipe delimiters.
		requires:
			|var|`tree` |must| be a formally correct docstring tree.
	Notes:
		Details:
			The docstring tree is rendered exactly as nested JSON arrays;\
			no additional restructuring is performed.
	Parameters:
		tree:
			The tree to render as string.
		flavour:
			The style to render Normativity Keywords in
	Returns:
		The JSON node
	Raises:
		ParseError:
			|Must| propagate from |func|`make_docitem_tree_from_docstring_tree`.
		BaseException:
			|May| propagate from |func|`make_docitem_tree_from_docstring_tree`.
			|May| propagate from nested function calls.
	See_also:
		sdv.doc.waterloo.docitem.Flavour, sdv.doc.waterloo.docitem.Format
	"""
	tr = tracer()
	node_docstring = make_docitem_tree_from_docstring_tree(tr,tree)
	m = build_node_json(node_docstring,flavour)
	return m

def to_node_legend_json() -> Dict[str, WtrlJsonNode_t]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
		status:
			stable
	Contract:
		general:
			|Must| return a JSON-serializable mapping from Waterloo role names to short descriptions.
	Parameters:
	Returns:
		Mapping of role-name -> human-readable description.
	Raises:
	"""
	return cast(Dict[str, WtrlJsonNode_t], ROLES_LEGEND)

#===== MARKDOWN ===============================================#

def to_string_md(tree: DocstringTree, flavour: Flavour = Flavour.MARKDOWN, headings: bool = True) -> str:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises, See_also
		scope:
			public
		status:
			draft
	Contract:
		general:
			|Must| render the tree as Markdown using the given flavour (default: MARKDOWN).
			|Must| preserve the sequence structure as nested unordered lists.
			|Must| render normativity tokens according to |var|`flavour` (e.g. **MUST** for MARKDOWN).
		requires:
			|var|`tree` |must| be a formally correct docstring tree.
	Parameters:
		tree:
			The docstring tree to render.
		flavour:
			The formatting style for normativity tokens.
		headings:
			If |True|, section-like items (strings ending with ':' that precede a list)
			are rendered as Markdown headings instead of plain bullets.
	Returns:
		A Markdown string.
	Raises:
		TypeError:
			|Must| raise if |var|`tree` is not a sequence made only of strings and lists, or\
			if |var|`flavour` is not a |type|`Flavour`.
	See_also:
		sdv.doc.waterloo.docitem.Flavour, sdv.doc.waterloo.docitem.Format
	"""
	node = to_node_docstring_tree_json(tree, flavour)

	def render_md(obj: WtrlJsonNode_t, depth: int) -> List[str]:
		lines: List[str] = []
		prefix = "  " * depth + "- "
		if isinstance(obj, dict):
			for k, v in obj.items():
				if headings:
					level = min(6, depth + 2)
					lines.append(f"{'#' * level} {_render_token(str(k), flavour)}")
					lines.extend(render_md(v, depth + 1))
				else:
					lines.append(prefix + _render_token(str(k), flavour))
					lines.extend(render_md(v, depth + 1))
		elif isinstance(obj, list):
			for item in obj:
				if isinstance(item, (dict, list)):
					lines.extend(render_md(item, depth + 1))
				else:
					lines.append(prefix + _render_token(str(item), flavour))
		else:
			lines.append(prefix + _render_token(str(obj), flavour))
		return lines

	return "\n".join(render_md(node, 1)) + "\n"
