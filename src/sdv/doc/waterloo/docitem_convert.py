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
	to_node_legend_json
	to_node_docstring_tree_json
	to_node_signature_json
	to_string_legend_yaml
	to_string_yaml
	to_string_signature_yaml
	to_string_md
	build_node_json
Public_types:
	WtrlJsonNode_t:
		Type for JSON nodes. This type |must| be public because |func|`to_node_docstring_tree_json` and |func|`to_node_signature_json` are.
"""

from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, Optional, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast
from typing_extensions import Self
import re,copy,inspect
import json
import textwrap

try:
	from sdv_doc_docitem import *
except ImportError:
	from sdv.doc.waterloo.docitem import *

#===== Constants ==============================================#
RE_YAML_SIMPLE_KEY_COMPILED = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*$')

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
	"dfn": "Definition of a term",
	"file": "File or path",
	"func": "Function or callable",
	"key": "Key on the keyboard",
	"label": "Section/Subsection label",
	"lit": "Literal text or code",
	"mod": "Module name",
	"op": "Operator symbol",
	"opt": "Command-line option or flag",
	"tag": "Tag or marker",
	"term": "Domain-specific term",
	"type": "Type name or annotation",
	"value": "Concrete value",
	"var": "Variable name",
	"var_type": "Variable and type, like 'var:type'",
}

#===== Type Checking ==========================================#
WtrlJsonNode_t: TypeAlias = Dict[str, "WtrlJsonNode_t"] | List["WtrlJsonNode_t"] | str | int | float | bool | None
WtrlYamlNode_t: TypeAlias = Union[Dict[str, "WtrlYamlNode_t"], List[Any], str, int, float, bool, None]

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

#===== YAML ===================================================#

#----- begin YAML helpers -------------------------------------#

def _emit_node(out: List[str],node: WtrlYamlNode_t,config: YamlConfig,parent_key: Optional[str]=None) -> None:
	def _ordered_items(d: Dict[str, Any], parent: Optional[str]) -> List[Tuple[str, Any]]:
		orig_keys = list(d.keys())
		order: Sequence[str] | None = None
		if parent is None:
			order = list(CANONICAL_ORDER_OF_SECTIONS.keys())
		else:
			order = CANONICAL_ORDER_OF_SECTIONS.get(parent)
		if order is None:
			return [(k, d[k]) for k in orig_keys]
		seen: Set[str] = set()
		result: List[Tuple[str, Any]] = []
		for k in order:
			if k in d:
				result.append((k, d[k]))
				seen.add(k)
		for k in orig_keys:
			if k not in seen:
				result.append((k, d[k]))
		# If any child is itself a mapping, sort its children too
		sorted_result: List[Tuple[str, Any]] = []
		for k, v in result:
			if isinstance(v, dict):
				sorted_result.append((k, dict(_ordered_items(v, k))))
			else:
				sorted_result.append((k, v))
		return sorted_result

	if isinstance(node, dict):
		for k, v in _ordered_items(node, parent_key):
			key_yaml = build_yaml_key(k)
			if isinstance(v, dict):
				out.append(f"{config.indent_str()}{key_yaml}:")
				_emit_node(out, v, config.inc_level(), parent_key=k)
			elif isinstance(v, list):
				if not v:
					out.append(f"{config.indent_str()}{key_yaml}: []")
				else:
					out.append(f"{config.indent_str()}{key_yaml}:")
					_emit_sequence(out, v, config.inc_level(), parent_key=k)
			elif isinstance(v, (str, int, float, bool)) or v is None:
			# simple scalar
				val = "null" if v is None else (_yaml_scalar(str(v)) if isinstance(v, str) else str(v).lower() if isinstance(v,bool) else str(v))
				out.append(f"{config.indent_str()}{key_yaml}: {val}")
			else:
				raise TypeError(f"Unexpected node type: {type(v).__name__}")
	elif isinstance(node, list):
		_emit_sequence(out, node,config,parent_key=parent_key)
	else:
		raise TypeError(f"Unexpected node type: {type(node).__name__}")

def _emit_sequence(out: List[str],items: List[Any],config: YamlConfig,parent_key: Optional[str]=None) -> None:
	pad = config.indent_str()
	for s in items:
		if isinstance(s, dict):
			if not s:
				out.append(f"{pad}- {{}}")
				continue
			items_iter = list(s.items())
			first_k, first_v = items_iter[0]
			key_yaml = build_yaml_key(first_k)
			if isinstance(first_v, (str, int, float, bool)) or first_v is None:
				val = "null" if first_v is None else (_yaml_scalar(str(first_v)) if isinstance(first_v, str) else str(first_v).lower() if isinstance(first_v,bool) else str(first_v))
				out.append(f"{pad}- {key_yaml}: {val}")
				rest = items_iter[1:]
				if rest:
					tmp_dict = {k:v for k,v in rest}
					_emit_node(out, tmp_dict, config.inc_level(), parent_key=parent_key)
			else:
				out.append(f"{pad}- {key_yaml}:")
				_emit_node(out, first_v, config.inc_level(), parent_key=first_k)
				rest = items_iter[1:]
				if rest:
					tmp_dict = {k:v for k,v in rest}
					_emit_node(out, tmp_dict, config.inc_level(), parent_key=parent_key)
		elif isinstance(s, list):
			out.append(f"{pad}-")
			_emit_sequence(out, s, config.inc_level(), parent_key=parent_key)
		else:
			s_str = str(s)
			if config.fold_long_scalars and _should_fold(s_str, config.fold_threshold):
				out.append(f"{pad}- >-")
				for line in _wrap_text(s_str, width=config.wrap_width):
					out.append(f"{pad}{' ' * config.indent}{line}")
			else:
				out.append(f"{pad}- {_yaml_scalar(s_str)}")


def _should_fold(s: str, threshold: int) -> bool:
# Simple rule: too long -> fold.
	return len(s) >= threshold and " " in s

def _wrap_text(s: str, *, width: int) -> List[str]:
# Minimal word wrap (keeps tabs/spaces inside words as-is; splits on spaces).
	words = s.split(" ")
	lines: List[str] = []
	cur: List[str] = []
	cur_len = 0

	for w in words:
		add_len = (1 if cur else 0) + len(w)
		if cur and (cur_len + add_len) > width:
			lines.append(" ".join(cur))
			cur = [w]
			cur_len = len(w)
		else:
			if cur:
				cur_len += 1 + len(w)
			else:
				cur_len = len(w)
			cur.append(w)

	if cur:
		lines.append(" ".join(cur))
	return lines

def build_yaml_key(k: str) -> str:
# Simple keys without quotes, others with single quotes.
	return k if RE_YAML_SIMPLE_KEY_COMPILED.match(k) else _yaml_scalar(k)

def _yaml_scalar(s: str) -> str:
# YAML single-quoted scalars: the only escape is: '  ->  ''
	esc = s.replace("'", "''")
	return f"'{esc}'"

#----- end YAML helpers ---------------------------------------#

#----- begin YAML rendering -----------------------------------#

class YamlConfig:
	def __init__(self) -> None:
# Set to True if the Yaml code is a snippet within a larger Yaml code.
		self.embedded: bool = False
# Depends on the embedding, you'll find out.
		self.start_level: int = 0
		self.indent: int = 2
		self.level: int = 0
		self.fold_long_scalars: bool = True
		self.fold_threshold: int = 110
		self.wrap_width: int = 76
	def indent_str(self) -> str:
		return ' ' * ((self.start_level + self.level) * self.indent)
	def inc_level(self) -> Self:
		c = copy.copy(self)
		c.level += 1
		return c

# Legend export as YAML
def to_string_legend_yaml(config: YamlConfig = YamlConfig()) -> str:
	"""
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
			|Must| render the Waterloo roles legend as YAML using the existing emitter.
	Parameters:
		config:
			How to render the YAML code.
	Returns:
		The YAML string containing the legend.
	Raises:
	"""
	out_lines: List[str] = ["---"] if not config.embedded else []
	_emit_node(out_lines, {"__WTRL_ROLES__": cast(Dict[str, WtrlYamlNode_t], ROLES_LEGEND)}, config)
	return "\n".join(out_lines) + "\n"

def to_string_signature_yaml(obj: object, config: YamlConfig = YamlConfig()) -> str:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
		status:
			draft
	Contract:
		general:
			|Must| render a YAML snippet as defined by |var|`config`, representing the 
			signature of the callable |var|`obj`.
			The root key |must| be |attr|`signature`, containing the subkeys 
			|attr|`text`, |attr|`parameters`, and |attr|`returns`.
			|attr|`text` |must| provide an inline-style representation of the signature.
			|attr|`parameters` |must| contain a sequence of elements, each providing:
			|attr|`name`: The parameter identifier.
			|attr|`kind`: The slot-filling strategy (e.g., positional-only, keyword-only, 
			or variadic) as defined by the Python |func|`inspect` semantics.
			|attr|`annotation`: The parameter's type hint or annotation.
			|attr|`default`: |value|`null` if no default value is defined; otherwise, 
			a string representation of the default value.
			The subkey |attr|`returns` |must| represent the return type of the callable.
	Parameters:
		obj:
			The callable whose signature is to be inspected and rendered.
		config:
			Configuration object controlling indentation, line folding, and 
			the embedding of the emitted YAML.
	Returns:
		The generated YAML string.
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
		raise TypeError("obj must be callable to render its signature")

	sig = inspect.signature(cast(Callable[..., Any], obj))

	def _ann_node(ann: Any) -> Optional[Dict[str, str]]:
		if ann is inspect._empty:
			return None
		if isinstance(ann, type):
			return {"type": get_obj_name(ann)}
		if isinstance(ann, str):
			return {"type": ann}
		return {"repr": repr(ann)}

	def _default_node(default: Any) -> Optional[Dict[str, str]]:
		if default is inspect._empty:
			return None
		if isinstance(default, (str, int, float, bool)) or default is None:
			return {"repr": repr(default)}
		# For objects: avoid evaluating user code; prefer type + safe repr
		def _safe_repr(obj: Any) -> str:
			try:
				return repr(obj)
			except Exception as exc:  # pragma: no cover - defensive
				return f"<unreprable {get_obj_name(obj)}: {exc}>"

		return {"repr": _safe_repr(default)}

	param_items: List[Dict[str, Any]] = []
	for p in sig.parameters.values():
		entry: Dict[str, Any] = {
			"name": p.name,
			"kind": p.kind.name,
			"annotation": _ann_node(p.annotation),
			"default": _default_node(p.default),
		}
		param_items.append(entry)

	ret_node = _ann_node(sig.return_annotation)

	yaml_dict: Dict[str, Any] = {
		"signature": {
			"text": f"{get_obj_name(obj)}{sig}",
			"parameters": param_items,
			"returns": ret_node,
		}
	}

	out_lines: List[str] = ["---"] if not config.embedded else []
	_emit_node(out_lines, yaml_dict, config)
	return "\n".join(out_lines) + "\n"

def to_string_yaml(tree: DocstringTree, flavour: Flavour, config: YamlConfig = YamlConfig()) -> str:
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
			|Must| render the tree as YAML-string using the given flavour.
			|Must| reproduce the tree structure by indentation in YAML.
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
			Each list element becomes a YAML sequence item (\"-\"), preserving\
			the original nesting of the docstring tree. Long scalars are emitted as folded\
			blocks (>-) to keep line lengths reasonable for linters.
	Parameters:
		tree:
			The tree to render as string.
		flavour:
			The style to render Normativity Keywords in.
		config:
			How to render the YAML code.
	Returns:
		The YAML string
	Raises:
		ParseError:
			|Must| propagate if the docstring tree cannot be turned into a docitem AST.
		TypeError:
			|Must| raise if |var|`flavour` is not a |type|`Flavour`.
	See_also:
		sdv.doc.waterloo.docitem.Flavour, sdv.doc.waterloo.docitem.Format
	"""
	ast = to_node_docstring_tree_json(tree, flavour)
	out_lines: List[str] = ["---"] if not config.embedded else []
	_emit_node(out_lines, ast, config)
	return "\n".join(out_lines) + "\n"

#----- end YAML rendering -------------------------------------#

if __name__ == "__main__":
	print(to_string_signature_yaml(to_string_signature_yaml,YamlConfig()))
