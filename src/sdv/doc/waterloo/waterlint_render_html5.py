r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
	scope:
		extension
Contract:
	general:
		|Must| provide a function |func|`render_html5` that serves as\
		the main entry point for the |cmd|`waterlint render-html5` subcommand.
Public_functions:
	render_html5, render_html5_document, build_parser
Function_overview:
	render_html5:
		Main entry point for the `waterlint render-html5` subcommand.
		This function takes in a list of input JSON document paths,
		merges them, and generates a self-contained HTML5 file that
		presents the documented objects in a clear and navigable format.
		The function also handles error reporting via the provided
		tracer instance and supports various customization options for the output HTML.
	render_html5_document:
		Render a single HTML5 document from the merged JSON data.
	build_parser:
		Construct and return the argparse subparser for the render-html5 command.
"""

from __future__ import annotations

import argparse
import json
import html
import re
import sys
import traceback
import importlib.resources as importlib_resources
from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple, TypeAlias
from sdv.doc.waterloo import docitem
from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo.docitem_helper import (
	get_obj_fully_qualified_name,
	tracer,
)
from sdv.doc.waterloo.waterlint_common import (
	Origin_t,
)

# Not relevant yet, but in case we set up a plugin concept,
# vendors should be encouraged to follow semantic versioning
# for their plugins.
__version__ = "0.1.2"

#===== Typing ================================================#
# "obj" is a fallback for objects that do not map to a more specific kind.
Kind_t: TypeAlias = Literal["mod", "cls", "func", "meth", "type", "var", "const", "obj"]

#=============================================================#

SOURCE_CODE_ERRORS = (AttributeError, IndexError, KeyError, NameError, AssertionError, NotImplementedError, SyntaxError)


def _build_tracer_json_doc(tr: tracer, include_debug: bool = False) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=wl_common.WTRL_DOCITEM_VERSION,
		id_prefix=f"urn:waterlint:wtrl-tracer-json:{__version__}",
		include_debug=include_debug,
	)


def _emit_tracer(tr: tracer, out_path: str | None, out_json_path: str | None = None, debug: bool = False) -> None:
	wl_common.emit_tracer(
		tr,
		out_path,
		out_json_path,
		debug=debug,
		callback_build_json_doc=lambda tr_: _build_tracer_json_doc(tr_, include_debug=debug),
	)


def _final_exit_code(base_code: int, tr: tracer, fail_on_warning: bool) -> int:
	code = base_code
	if tr.has_errors():
		code = 1
	if code == 0 and fail_on_warning and tr.has_warnings():
		code = 1
	return code

try:
	from pygments import highlight
	from pygments.lexers import get_lexer_by_name
	from pygments.formatters import HtmlFormatter
	_HAS_PYGMENTS = True
except Exception:
	_HAS_PYGMENTS = False

def _require_dict(name: str, val: Any) -> Dict[str, Any]:
	if not isinstance(val, dict):
		raise RuntimeError(f"{name} must be an object")
	return val


def _infer_kind_for_qid(
	qid: str,
	toc_modules: Dict[str, Any],
	toc_classes: Dict[str, Any],
	toc_callables: Dict[str, Any],
	toc_types: Dict[str, Any],
	toc_vars: Dict[str, Any],
	toc_consts: Dict[str, Any],
) -> Kind_t:
	if qid in toc_modules:
		return "mod"
	if qid in toc_classes:
		return "cls"
	if qid in toc_callables:
		parent = qid.rsplit(".", 1)[0] if "." in qid else ""
		if parent in toc_classes:
			return "meth"
		return "func"
	if qid in toc_types:
		return "type"
	if qid in toc_vars:
		return "var"
	if qid in toc_consts:
		return "const"
	return "obj"


def _build_anchor_for_qid(qid: str, kind: str) -> str:
	segs = [s for s in qid.split(".") if s]
	if not segs:
		return f"wtrl-{kind}"
	enc = "-".join(f"{len(s)}:{s}" for s in segs)
	return f"wtrl-{kind}-{enc}"


def _load_one_json(path: str) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as fh:
		doc = json.load(fh)
	if not isinstance(doc, dict):
		raise RuntimeError(f"input is not a JSON object: {path}")
	return doc


def _load_render_js_source() -> str:
	"""Load JavaScript source for render-html5 from packaged data."""
	rel_path = Path("js") / "waterlint_render_html5.js"
	candidates: list[Path] = []
	candidates.append(Path(__file__).resolve().parent / rel_path)
	try:
		p = importlib_resources.files("sdv.doc.waterloo") / "js" / "waterlint_render_html5.js"
		candidates.append(Path(str(p)))
	except Exception:
		pass
	for p in candidates:
		if p.is_file():
			return p.read_text(encoding="utf-8")
	raise RuntimeError(
		"Cannot load JavaScript asset 'js/waterlint_render_html5.js'. "
		+ "Tried: "
		+ ", ".join(str(p) for p in candidates)
	)

def _load_default_css_source() -> str:
	"""Load default CSS source for render-html5 from packaged data."""
	rel_paths = [
		Path("css") / "common_styles.css",
		Path("css") / "wtrl-style.css",
	]
	s = ""
	for rel_path in rel_paths:
		candidates: list[Path] = []
		# Candidate 1: Try to load from the same directory as this script (useful for development).
		candidates.append(Path(__file__).resolve().parent / rel_path)
		try:
			# Candidate 2: Try to load from the installed package resources (useful for production).
			p = importlib_resources.files("sdv.doc.waterloo") / str(rel_path)
			candidates.append(Path(str(p)))
		except Exception:
			pass
		for p in candidates:
			if p.is_file():
				s += p.read_text(encoding="utf-8") + "\n"
				break
		else:
			raise RuntimeError(
				"Cannot load default CSS asset 'css/{}'. ".format(rel_path)
				+ "Tried: "
				+ ", ".join(str(p) for p in candidates)
			)
	return s


_DEFAULT_PYGMENTS_THEME = "gruvbox-light"
_DEFAULT_PYGMENTS_DARK_THEME = "gruvbox-dark"


def _make_pygments_formatter(style_name: str) -> HtmlFormatter:
	try:
		return HtmlFormatter(cssclass="wtrl-code", nowrap=False, style=style_name)
	except Exception:
		return HtmlFormatter(cssclass="wtrl-code", nowrap=False)


def _scope_css_rule(rule: str, prefixes: list[str]) -> str:
	head, sep, tail = rule.partition("{")
	if not sep:
		return rule
	selectors = [part.strip() for part in head.split(",") if part.strip()]
	if not selectors:
		return rule
	scoped = []
	for prefix in prefixes:
		for selector in selectors:
			scoped.append(f"{prefix} {selector}")
	return ", ".join(scoped) + " {" + tail


def _scope_pygments_css(css: str, prefixes: list[str]) -> str:
	lines = []
	for line in css.splitlines():
		stripped = line.strip()
		if not stripped or stripped.startswith("@") or "{" not in line:
			lines.append(line)
			continue
		lines.append(_scope_css_rule(line, prefixes))
	return "\n".join(lines)


def _build_pygments_theme_css(light_theme: str, dark_theme: str) -> str:
	light_formatter = _make_pygments_formatter(light_theme)
	dark_formatter = _make_pygments_formatter(dark_theme)
	light_css = _scope_pygments_css(
		light_formatter.get_style_defs(".wtrl-code"),
		["html[data-wtrl-theme=\"light\"]", "html[data-wtrl-theme=\"auto\"]"],
	)
	dark_css = _scope_pygments_css(
		dark_formatter.get_style_defs(".wtrl-code"),
		["html[data-wtrl-theme=\"dark\"]"],
	)
	auto_dark_css = _scope_pygments_css(
		dark_formatter.get_style_defs(".wtrl-code"),
		["html[data-wtrl-theme=\"auto\"]"],
	)
	return "\n".join([
		light_css,
		dark_css,
		"@media (prefers-color-scheme: dark) {",
		auto_dark_css,
		"}",
	])


def _build_examples_html_map(
	merged: Dict[str, Any],
	pygments_theme: str | None = None,
	pygments_dark_theme: str | None = None,
) -> Tuple[Dict[str, str], str]:
	"""Build HTML-rendered example code map and CSS (via pygments if available)."""
	examples = _require_dict("examples", merged.get("examples", {}))
	if not _HAS_PYGMENTS:
		html_map: Dict[str, str] = {}
		for ex_key, ex_node in examples.items():
			if not isinstance(ex_node, dict):
				continue
			code = str(ex_node.get("code", ""))
			html_map[str(ex_key)] = "<pre><code>" + html.escape(code) + "</code></pre>"
		return html_map, ""

	style_name = pygments_theme or _DEFAULT_PYGMENTS_THEME
	dark_style_name = pygments_dark_theme or _DEFAULT_PYGMENTS_DARK_THEME
	formatter = _make_pygments_formatter(style_name)
	css = _build_pygments_theme_css(style_name, dark_style_name)
	html_map = {}
	for ex_key, ex_node in examples.items():
		if not isinstance(ex_node, dict):
			continue
		lang = str(ex_node.get("lang", "python"))
		code = str(ex_node.get("code", ""))
		try:
			lexer = get_lexer_by_name(lang)
		except Exception:
			lexer = get_lexer_by_name("text")
		html_map[str(ex_key)] = highlight(code, lexer, formatter)
	return html_map, css


def _merge_docs_strict(input_paths: List[str]) -> Tuple[Dict[str, Any], str, str]:
	if not input_paths:
		raise RuntimeError("at least one --in must be provided")

	base_scope: str | None = None
	base_flavour: str | None = None
	base_schema_version: str | None = None

	merged_objects: Dict[str, Any] = {}
	merged_toc_modules: Dict[str, Any] = {}
	merged_toc_classes: Dict[str, Any] = {}
	merged_toc_callables: Dict[str, Any] = {}
	merged_toc_types: Dict[str, Any] = {}
	merged_toc_variables: Dict[str, Any] = {}
	merged_toc_constants: Dict[str, Any] = {}
	merged_examples: Dict[str, Any] = {}
	roles: Dict[str, Any] | None = None
	scopes: Dict[str, Any] | None = None
	modules_in_inputs: List[str] = []

	for in_path in input_paths:
		doc = _load_one_json(in_path)
		meta = _require_dict("__WTRL_META__", doc.get("__WTRL_META__"))
		ver = _require_dict("__WTRL_VERSION__", doc.get("__WTRL_VERSION__"))

		# We make sure not to mix scopes, flavours, or schema versions across inputs,
		# as this would indicate a likely error in the input documents or an unsupported use case for merging.
		scope = str(meta.get("scope", ""))
		flavour = str(meta.get("flavour", ""))
		schema_version = str(ver.get("schema", ""))

		if base_scope is None:
			base_scope = scope
		elif scope != base_scope:
			raise RuntimeError(f"scope mismatch across inputs: '{scope}' != '{base_scope}'")

		if base_flavour is None:
			base_flavour = flavour
		elif flavour != base_flavour:
			raise RuntimeError(f"flavour mismatch across inputs: '{flavour}' != '{base_flavour}'")

		# We should consider implementing a waterlint command like `update-json-schema`
		# that can update input documents to a common schema version if needed,
		# but for now we require all inputs to already be on the same version.
		if base_schema_version is None:
			base_schema_version = schema_version
		elif schema_version != base_schema_version:
			raise RuntimeError(f"schema version mismatch across inputs: '{schema_version}' != '{base_schema_version}'")

		if roles is None:
			roles = _require_dict("__WTRL_ROLES__", doc.get("__WTRL_ROLES__", {}))
		if scopes is None:
			scopes = _require_dict("__WTRL_SCOPES__", doc.get("__WTRL_SCOPES__", {}))

		toc_modules = _require_dict("__WTRL_TOC_MODULES__", doc.get("__WTRL_TOC_MODULES__", {}))
		toc_classes = _require_dict("__WTRL_TOC_CLASSES__", doc.get("__WTRL_TOC_CLASSES__", {}))
		toc_callables = _require_dict("__WTRL_TOC_CALLABLES__", doc.get("__WTRL_TOC_CALLABLES__", {}))
		toc_types = _require_dict("__WTRL_TOC_TYPES__", doc.get("__WTRL_TOC_TYPES__", {}))
		toc_vars = _require_dict("__WTRL_TOC_VARIABLES__", doc.get("__WTRL_TOC_VARIABLES__", {}))
		toc_consts = _require_dict("__WTRL_TOC_CONSTANTS__", doc.get("__WTRL_TOC_CONSTANTS__", {}))
		examples = _require_dict("__WTRL_EXAMPLES__", doc.get("__WTRL_EXAMPLES__", {}))
		objects = _require_dict("__WTRL_OBJECTS__", doc.get("__WTRL_OBJECTS__", {}))

		for key in objects.keys():
			if key in merged_objects:
				raise RuntimeError(f"qualified-identifier collision while merging: '{key}'")
		merged_objects.update(objects)

		merged_toc_modules.update(toc_modules)
		merged_toc_classes.update(toc_classes)
		merged_toc_callables.update(toc_callables)
		merged_toc_types.update(toc_types)
		merged_toc_variables.update(toc_vars)
		merged_toc_constants.update(toc_consts)
		for ex_key, ex_node in examples.items():
			if ex_key in merged_examples and merged_examples[ex_key] != ex_node:
				raise RuntimeError(f"example-id collision while merging: '{ex_key}'")
			merged_examples[ex_key] = ex_node

		for mod_qid in toc_modules.keys():
			if mod_qid not in modules_in_inputs:
				modules_in_inputs.append(mod_qid)

	if base_scope is None or base_flavour is None:
		raise RuntimeError("cannot determine scope/flavour from inputs")

	merged: Dict[str, Any] = {
		"meta": {
			"scope": base_scope,
			"flavour": base_flavour,
			"schema": base_schema_version,
			"modules": modules_in_inputs,
		},
		"roles": roles or {},
		"scopes": scopes or {},
		"toc_modules": merged_toc_modules,
		"toc_classes": merged_toc_classes,
		"toc_callables": merged_toc_callables,
		"toc_types": merged_toc_types,
		"toc_variables": merged_toc_variables,
		"toc_constants": merged_toc_constants,
		"examples": merged_examples,
		"objects": merged_objects,
	}
	return merged, base_scope, base_flavour


def _build_ui_index(merged: Dict[str, Any]) -> List[Dict[str, str]]:
	objects = _require_dict("objects", merged.get("objects"))
	toc_modules = _require_dict("toc_modules", merged.get("toc_modules"))
	toc_classes = _require_dict("toc_classes", merged.get("toc_classes"))
	toc_callables = _require_dict("toc_callables", merged.get("toc_callables"))
	toc_types = _require_dict("toc_types", merged.get("toc_types"))
	toc_vars = _require_dict("toc_variables", merged.get("toc_variables"))
	toc_consts = _require_dict("toc_constants", merged.get("toc_constants"))

	index: List[Dict[str, str]] = []
	for qid in sorted(objects.keys()):
		kind = _infer_kind_for_qid(qid, toc_modules, toc_classes, toc_callables, toc_types, toc_vars, toc_consts)
		anchor = _build_anchor_for_qid(qid, kind)
		index.append({"label": qid, "target": qid, "kind": kind, "anchor": anchor})
	return index


def _drop_preamble_sections(merged: Dict[str, Any]) -> None:
	"""Remove top-level doc section 'Preamble' from all rendered object nodes."""
	objects = _require_dict("objects", merged.get("objects"))
	for _, node in objects.items():
		if not isinstance(node, dict):
			continue
		doc = node.get("doc")
		if not isinstance(doc, dict):
			continue
		if "Preamble" in doc:
			doc.pop("Preamble", None)


def _validate_header_fragment(fragment: str) -> None:
	"""Apply a minimal safety and binding contract to custom header HTML."""
	if not re.search(r"""id\s*=\s*["']wtrl-title["']""", fragment, re.IGNORECASE):
		raise KeyError("custom header fragment does not contain required element '#wtrl-title'")
	if re.search(r"""<\s*script\b""", fragment, re.IGNORECASE):
		raise RuntimeError("custom header fragment must not contain <script> elements")
	if re.search(r"""<\s*/?\s*(?:html|head|body|main)\b""", fragment, re.IGNORECASE):
		raise RuntimeError("custom header fragment must not contain document-level elements (<html>, <head>, <body>, <main>)")


def _build_html_doc(merged: Dict[str, Any], allow_raw_object_node: bool = True) -> str:
	meta = _require_dict("meta", merged.get("meta"))
	index = _build_ui_index(merged)
	pygments_theme = merged.get("meta", {}).get("pygments_theme", None)
	pygments_dark_theme = merged.get("meta", {}).get("pygments_dark_theme", None)
	examples_html_map, pygments_css = _build_examples_html_map(
		merged,
		str(pygments_theme) if pygments_theme else None,
		str(pygments_dark_theme) if pygments_dark_theme else None,
	)

	data_json = json.dumps(merged, ensure_ascii=False)
	index_json = json.dumps(index, ensure_ascii=False)
	examples_html_json = json.dumps(examples_html_map, ensure_ascii=False)

	css_base = """
html, body { margin:0; padding:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#f7f7f4; color:#1f2428; }
.wtrl-app { display:grid; grid-template-columns: 340px 1fr; min-height:100vh; }
.wtrl-side { border-right:1px solid #ddd; background:#fff; padding:16px; }
.wtrl-main { padding:20px 24px; }
.wtrl-meta { font-size:12px; color:#666; margin-bottom:12px; }
.wtrl-search-row { display:flex; gap:8px; align-items:center; }
.wtrl-nav { flex:0 0 auto; width:32px; min-width:32px; padding:9px 0; border:1px solid #bbb; border-radius:8px; background:#fff; color:#334155; cursor:pointer; }
.wtrl-nav:hover { background:#f3f6fa; }
.wtrl-nav:disabled { opacity:0.45; cursor:default; background:#fff; }
.wtrl-nav-history { flex:0 0 280px; min-width:180px; max-width:320px; box-sizing:border-box; padding:9px 10px; border:1px solid #bbb; border-radius:8px; background:#fff; color:#334155; font-size:13px; }
.wtrl-nav-history:disabled { opacity:0.55; background:#f8fafc; }
.wtrl-filter-row { display:grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap:8px; margin-top:8px; align-items:center; }
.wtrl-filter-pair { display:flex; gap:8px; align-items:center; min-width:0; }
.wtrl-filter-label { flex:0 0 auto; font-size:13px; color:#334155; }
.wtrl-kind-filter, .wtrl-label-mode { flex:1 1 auto; min-width:0; box-sizing:border-box; padding:9px 10px; border:1px solid #bbb; border-radius:8px; background:#fff; color:#334155; font-size:13px; }
.wtrl-kind-filter:disabled { opacity:0.55; background:#f8fafc; }
.wtrl-label-mode:disabled { opacity:0.55; background:#f8fafc; }
.wtrl-input { flex:1 1 auto; min-width:0; box-sizing:border-box; padding:10px 12px; border:1px solid #bbb; border-radius:8px; font-size:14px; }
.wtrl-clear { flex:0 0 auto; padding:9px 12px; border:1px solid #bbb; border-radius:8px; background:#fff; color:#334155; cursor:pointer; }
.wtrl-clear:hover { background:#f3f6fa; }
.wtrl-hitlist { margin-top:12px; max-height:75vh; overflow:auto; border:1px solid #ddd; border-radius:8px; background:#fff; }
.wtrl-hit { display:block; width:100%; text-align:left; border:0; border-bottom:1px solid #eee; background:transparent; padding:8px 10px; font-size:13px; cursor:pointer; }
.wtrl-hit:hover { background:#f3f6fa; }
.wtrl-kind { color:#57606a; font-size:11px; margin-right:8px; }
.wtrl-title { margin:0 0 10px 0; font-size:22px; }
.wtrl-sub { margin:0 0 16px 0; color:#57606a; }
.wtrl-block { border:1px solid #ddd; border-radius:10px; background:#fff; padding:14px; }
.wtrl-signature { margin:0; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:12px; color:#334155; white-space:pre-wrap; }
.wtrl-signature-line { margin:0 0 2px 0; }
.wtrl-section { margin: 0 0 14px 0; border:1px solid #ececec; border-radius:8px; padding:10px 12px; background:#fff; }
.wtrl-section-head { font-weight:700; margin:0 0 8px 0; color:#0f172a; }
.wtrl-subsection { margin:0 0 8px 0; }
.wtrl-subsection-head { font-weight:600; margin:0 0 4px 0; color:#1f2937; }
.wtrl-text { margin:0 0 4px 0; white-space:pre-wrap; }
.wtrl-list { margin:4px 0 8px 20px; }
.wtrl-obj { margin:0; white-space:pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:12px; color:#334155; }
.wtrl-examples { margin-top:14px; }
.wtrl-example-head { font-weight:600; margin:0 0 6px 0; color:#334155; }
.wtrl-func, .wtrl_func { color:#3040ff; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-class, .wtrl_class { color:#770000; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-type, .wtrl_type { color:#770000; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-var, .wtrl_var { color:#a00; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-label, .wtrl_label { color:#1f2937; font-style:italic; }
.wtrl-value, .wtrl_value { color:#b26a00; }
.wtrl-mod, .wtrl_mod { color:#374151; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-attr, .wtrl_attr { color:#7c3aed; }
.wtrl-lit, .wtrl_lit { color:#1f2937; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-dfn, .wtrl_dfn, .wtrl-term, .wtrl_term { font-style:italic; }
.wtrl-op, .wtrl_op { color:#b91c1c; }
.wtrl-file, .wtrl_file { color:#0f766e; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-cmd, .wtrl_cmd, .wtrl-opt, .wtrl_opt, .wtrl-tag, .wtrl_tag { color:#4b5563; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-ref, .wtrl_ref { color:#005cc5; text-decoration-line:underline; text-decoration-style:dotted; text-decoration-thickness:1px; text-underline-offset:0.12em; }
.wtrl-norm, .wtrl_norm { color:#b42318; font-weight:700; }
a.wtrl-ref.wtrl-func, a.wtrl_ref.wtrl_func { color:#3040ff; text-decoration-line:underline; text-decoration-style:dotted; text-decoration-thickness:1px; text-underline-offset:0.12em; }
a.wtrl-ref.wtrl-type, a.wtrl_ref.wtrl_type { color:#770000; text-decoration-line:underline; text-decoration-style:dotted; text-decoration-thickness:1px; text-underline-offset:0.12em; }
a.wtrl-ref.wtrl-var, a.wtrl_ref.wtrl_var { color:#a00; text-decoration-line:underline; text-decoration-style:dotted; text-decoration-thickness:1px; text-underline-offset:0.12em; }
a.wtrl-ref.wtrl-func:visited, a.wtrl_ref.wtrl_func:visited { color:#3040ff; }
a.wtrl-ref.wtrl-type:visited, a.wtrl_ref.wtrl_type:visited { color:#770000; }
a.wtrl-ref.wtrl-var:visited, a.wtrl_ref.wtrl_var:visited { color:#a00; }
a.wtrl-ref:visited { color:inherit; }
button.wtrl-hit-kind-module { color:#770000; }
button.wtrl-hit-kind-class { color:#770000; }
button.wtrl-hit-kind-callable { color:#3040ff; }
button.wtrl-hit-kind-type { color:#770000; }
button.wtrl-hit-kind-assignable { color:#308030; }
button.wtrl-hit-kind-variable { color:#308030; }
button.wtrl-hit-kind-constant { color:#308030; }
"""

	js = _load_render_js_source()

	css_primary = str(merged.get("meta", {}).get("css_primary", ""))
	css_append = str(merged.get("meta", {}).get("css_append", ""))
	header_html = str(merged.get("meta", {}).get("header_html", "")).strip()
	if css_primary:
		css = css_primary + ("\n" + css_append if css_append else "") + ("\n" + pygments_css if pygments_css else "")
	else:
		css = css_base + ("\n" + css_append if css_append else "") + ("\n" + pygments_css if pygments_css else "")

	if not header_html:
		header_html = """
      <h1 id="wtrl-title" class="wtrl-title"></h1>
      <p id="wtrl-sub" class="wtrl-sub"></p>"""

	raw_object_html = ""
	if allow_raw_object_node:
		raw_object_html = """
        <details style="margin-top:12px">
          <summary>Raw object node</summary>
          <pre id="wtrl-obj" class="wtrl-obj"></pre>
        </details>"""

	html = f"""<!doctype html>
<html lang="en">
<head>
	  <meta charset="utf-8">
	  <meta name="viewport" content="width=device-width, initial-scale=1">
	  <title>Waterloo HTML5 Documentation</title>
	  <script>
	    try {{
	      document.documentElement.dataset.wtrlTheme = localStorage.getItem("wtrl-html5-theme") || "auto";
	    }} catch (_) {{
	      document.documentElement.dataset.wtrlTheme = "auto";
	    }}
	  </script>
	  <style>{css}</style>
	</head>
	<body>
	  <div class="wtrl-app">
	    <aside class="wtrl-side">
	      <div class="wtrl-theme-switcher" aria-label="Theme">
	        <button id="wtrl-theme-light" class="wtrl-theme-button wtrl-theme-light" type="button" title="Use light theme" aria-label="Use light theme"></button>
	        <button id="wtrl-theme-auto" class="wtrl-theme-button wtrl-theme-auto" type="button" title="Use system theme" aria-label="Use system theme"></button>
	        <button id="wtrl-theme-dark" class="wtrl-theme-button wtrl-theme-dark" type="button" title="Use dark theme" aria-label="Use dark theme"></button>
	      </div>
	      <div class="wtrl-meta"><strong>Scope:</strong> <span id="wtrl-scope"></span></div>
      <div class="wtrl-meta"><strong>Flavour:</strong> <span id="wtrl-flavour"></span></div>
      <div class="wtrl-meta"><strong>Modules:</strong> <span id="wtrl-modules"></span></div>
      <div class="wtrl-meta"><strong>Classes:</strong> <span id="wtrl-num-classes"></span></div>
      <div class="wtrl-meta"><strong>Callables:</strong> <span id="wtrl-num-callables"></span></div>
      <div class="wtrl-search-row">
        <button id="wtrl-nav-back" class="wtrl-nav" type="button" aria-label="Back"></button>
        <button id="wtrl-nav-forward" class="wtrl-nav" type="button" aria-label="Forward"></button>
        <select id="wtrl-nav-history" class="wtrl-nav-history" aria-label="History"></select>
<!--        <input id="wtrl-search" class="wtrl-input" list="wtrl-search-list" placeholder="Search qid / type / var / const" autocomplete="off" spellcheck="false"> -->
        <input id="wtrl-search" class="wtrl-input" placeholder="Search qid / type / var / const">
        <button id="wtrl-search-clear" class="wtrl-clear" type="button" aria-label="Clear search">Clear</button>
        <div class="wtrl-filter-row">
          <div class="wtrl-filter-pair">
            <label for="wtrl-kind-filter" class="wtrl-filter-label">Kind</label>
            <select id="wtrl-kind-filter" class="wtrl-kind-filter" aria-label="Kind filter">
            <option value="*">All</option>
            <option value="objects">Objects</option>
            <option value="modules">Modules</option>
            <option value="classes">Classes</option>
            <option value="callables">Callables</option>
            <option value="functions">Functions</option>
            <option value="methods">Methods</option>
            <option value="types">Types</option>
            <option value="assignables">Assignables</option>
            <option value="constants">Constants</option>
            <option value="variables">Variables</option>
            </select>
          </div>
          <div class="wtrl-filter-pair">
            <label for="wtrl-label-mode" class="wtrl-filter-label">Name</label>
            <select id="wtrl-label-mode" class="wtrl-label-mode" aria-label="Name display mode">
              <option value="full">Full</option>
              <option value="from-module" selected>With module</option>
              <option value="no-module">Without module</option>
            </select>
          </div>
        </div>
      </div>
      <datalist id="wtrl-search-list"></datalist>
      <div id="wtrl-hitlist" class="wtrl-hitlist"></div>
    </aside>
    <main class="wtrl-main">
{header_html}
      <section class="wtrl-block">
        <div class="wtrl-section">
          <div class="wtrl-section-head">Signature</div>
          <div id="wtrl-signature" class="wtrl-signature"></div>
        </div>
        <div id="wtrl-doc"></div>
        <div id="wtrl-examples"></div>
{raw_object_html}
      </section>
    </main>
  </div>
  <script>
{js.replace("__DATA_JSON__", data_json).replace("__INDEX_JSON__", index_json).replace("__EXAMPLES_HTML_JSON__", examples_html_json)}
  </script>
</body>
</html>
"""
	return html

def render_html5_document(
	tr: tracer,
	*,
	input_paths: List[str],
	out_file: str | None,
	out_dir: str | None,
	css_path: str | None = None,
	additional_css_path: str | None = None,
	header_html_path: str | None = None,
	pygments_theme: str | None = None,
	pygments_dark_theme: str | None = None,
	no_render_preamble: bool = False,
	allow_raw_object_node: bool = True,
) -> str:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Notes:
		About:
			This is the main entry point for the render-html5 command. This function orchestrates the entire
			rendering process, from loading and merging input JSON documents to building
			the final HTML output and writing it to a file. It also handles error
			reporting via the provided tracer instance.
	Contract:
		general:
			|Must| render the provided Waterloo JSON documents into a single self-contained\
			HTML5 file that presents the documented objects in a clear and navigable format.
			|Must_not| raise exceptions.
		requires:
			Input JSON documents |must| all have the same "scope", "flavour", and schema version.
			They |must| be valid against a Waterloo JSON schema version whose declared schema\
			identifier and version are compatible with the installed |lit|`waterlint` version.
		ensures:
			On success, the output file |must| be written and its path |must| be returned as a string.
			On failure, an output file |must_not| be generated and an empty string |must| be returned.
			The rendered HTML |should| be self-contained, with all CSS and JavaScript embedded directly\
			in the file, and |should_not| require any external assets to function correctly.
	Description:
		The rendered HTML will include a client-side search interface for navigating
		the documented objects, as well as a clean presentation of doc sections and example code.
	Parameters:
		tr:
			The tracer instance to report errors to. Errors will be reported with rule-ids in the form "RHTM-XXX" and a "tool" source.
		input_paths:
			A list of one or more paths to input JSON documents in the Waterloo format.
			These documents will be merged together to form the basis of the rendered HTML output.
		out_file:
			The path to the output HTML file to generate. This parameter is mutually exclusive with `out_dir`.
		out_dir:
			The directory in which to place the output HTML file. This parameter is mutually exclusive with `out_file`.
			If `out_dir` is provided, the output file will be named according to the pattern |file|`waterloo-docs.{scope}.{flavour}.html`
			and placed inside the specified directory.
		css_path:
			The path to a custom CSS file to use for styling the HTML output. If not provided, a default CSS will be used.
		additional_css_path:
			The path to an additional CSS file to append to the primary CSS. This allows for further customization of the HTML output.
		header_html_path:
			The path to a custom HTML fragment to use as the header of the document. This allows for adding custom content or branding to the top of the HTML output.
		pygments_theme:
			The name of the Pygments theme to use for syntax highlighting in code examples. If not provided, a default theme will be used.
		pygments_dark_theme:
			The name of the Pygments theme to use for syntax highlighting in code examples when the rendered HTML is in dark mode.
		no_render_preamble:
			If set to True, the |label|`Preamble` section of the input documents will not be rendered in the output HTML.
		allow_raw_object_node:
			If set to True, raw object nodes will be allowed in the output HTML. This can be useful for debugging or advanced customization.
	Returns:
		|Must| return the path to the generated HTML file on success, or an empty string on failure.
	Raises:
	"""
	def _add_error(rule_id: str, msg: str) -> None:
		try:
			tr.add_error(rule_id, "tool", msg)
		except Exception:
			pass

	try:
		if (out_file is None and out_dir is None) or (out_file is not None and out_dir is not None):
			_add_error("RHTM-002", "Exactly one of --out or --out-dir must be provided.")
			return ""

		try:
			merged, scope, flavour = _merge_docs_strict(input_paths)
		except Exception as exc:
			_add_error("RHTM-003", f"Cannot merge input JSON documents: {exc}")
			return ""

		if no_render_preamble:
			try:
				_drop_preamble_sections(merged)
			except Exception as exc:
				_add_error("RHTM-006", f"Cannot drop Preamble sections: {exc}")
				return ""

		if css_path:
			try:
				with open(css_path, "r", encoding="utf-8") as fh:
					merged["meta"]["css_primary"] = fh.read()
				merged["meta"]["css_append"] = ""
			except Exception as exc:
				_add_error("RHTM-004", f"Cannot read CSS file '{css_path}': {exc}")
				return ""
		else:
			try:
				merged["meta"]["css_primary"] = _load_default_css_source()
				merged["meta"]["css_append"] = ""
			except Exception as exc:
				_add_error("RHTM-004", f"Cannot load default CSS asset: {exc}")
				return ""

		if additional_css_path:
			try:
				with open(additional_css_path, "r", encoding="utf-8") as fh:
					merged["meta"]["css_append"] = fh.read()
			except Exception as exc:
				_add_error("RHTM-004", f"Cannot read additional CSS file '{additional_css_path}': {exc}")
				return ""

		if header_html_path:
			try:
				with open(header_html_path, "r", encoding="utf-8") as fh:
					header_html = fh.read()
			except Exception as exc:
				_add_error("RHTM-007", f"Cannot read custom header fragment '{header_html_path}': {exc}")
				return ""
			try:
				_validate_header_fragment(header_html)
			except KeyError as exc:
				_add_error("RHTM-008", str(exc))
				return ""
			except Exception as exc:
				_add_error("RHTM-009", f"Cannot embed custom header fragment safely: {exc}")
				return ""
			merged["meta"]["header_html"] = header_html

		if pygments_theme:
			merged["meta"]["pygments_theme"] = pygments_theme
		if pygments_dark_theme:
			merged["meta"]["pygments_dark_theme"] = pygments_dark_theme

		try:
			html = _build_html_doc(merged, allow_raw_object_node=allow_raw_object_node)
		except Exception as exc:
			_add_error("RHTM-005", f"Cannot build HTML output: {exc}")
			return ""

		if out_file is None:
			od = Path(str(out_dir))
			if not od.exists():
				_add_error("RHTM-002", f"Output directory does not exist: {out_dir}")
				return ""
			if not od.is_dir():
				_add_error("RHTM-002", f"Output path is not a directory: {out_dir}")
				return ""
			out_file = str(od / f"waterloo-docs.{scope}.{flavour}.html")

		try:
			wl_common.write_text_output(html, out_file)
		except Exception as exc:
			_add_error("RHTM-005", f"Cannot write HTML output '{out_file}': {exc}")
			return ""
		return out_file
	except Exception as exc:
		_add_error("RHTM-001", f"Unexpected render-html5 failure: {exc}")
		return ""


def render_html5(args: argparse.Namespace) -> int:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| execute the render-html5 command on one or more Waterloo JSON inputs and write the resulting HTML output.
	Parameters:
		args:
			Namespace containing the parsed render-html5 command line options.
			|must| provide the attributes expected by this command:
			* |attr|`input_files`: one or more input groups as produced by repeated |opt|`--in` options; each group |must| contain one or more Waterloo JSON file paths.
			* Exactly one of |attr|`out_file` or |attr|`out_dir` |must| be present and designate the HTML output target.
			* |attr|`fail_on_warning` |must| be present, because the exit code depends on it.
			* |attr|`out_diag` and |attr|`out_diag_json` |may| be present as optional tracer-diagnostics targets.
			* |attr|`css_file`, |attr|`additional_css_file`, |attr|`header_html_file`, |attr|`pygments_theme`, |attr|`pygments_dark_theme`, |attr|`no_render_preamble`, and |attr|`allow_raw_object_node` |may| be present as rendering controls.
			* |attr|`debug` |may| be present as a reserved global flag.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)
	try:
		in_files: list[str] = []
		if args.input_files:
			for grp in args.input_files:
				if isinstance(grp, list):
					in_files.extend(grp)
				else:
					in_files.append(str(grp))
		if not in_files:
			raise RuntimeError("at least one --in must be provided")
		out_path = render_html5_document(
			tr,
			input_paths=in_files,
			out_file=getattr(args, "out_file", None),
			out_dir=getattr(args, "out_dir", None),
			css_path=getattr(args, "css_file", None),
			additional_css_path=getattr(args, "additional_css_file", None),
			header_html_path=getattr(args, "header_html_file", None),
			pygments_theme=getattr(args, "pygments_theme", None),
			pygments_dark_theme=getattr(args, "pygments_dark_theme", None),
			no_render_preamble=getattr(args, "no_render_preamble", False),
			allow_raw_object_node=getattr(args, "allow_raw_object_node", True),
		)
		if not out_path:
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		tr.add_info(f"HTML5 documentation written to: {out_path}")
	except SOURCE_CODE_ERRORS:
		if not out_diag:
			wl_common.add_traceback(tr)
			_emit_tracer(tr, out_diag)
			return 1
		raise
	except Exception as exc:
		tr.add_error("RHTM-001", "tool", f"[{get_obj_fully_qualified_name(exc)}] Unexpected failure in render-html5 command: {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
) -> argparse.ArgumentParser:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| construct and return the argparse subparser for the render_html5 command.
	Parameters:
		subparsers:
			The argparse subparser registry of the main command line interface.
		parser_parts:
			Shared parser parts provided by the main program. Render-html5 uses the formatter class and the global CLI options.
	Returns:
		|Must| return the configured render_html5 subparser.
	Raises:
	"""
	prsr = subparsers.add_parser(
		"render-html5",
		help="Render Waterloo JSON to bundled HTML5",
		parents=[parser_parts["global_opts"]],
		formatter_class=parser_parts["formatter_class"])
	prsr.add_argument(
		"--in",
		dest="input_files",
		required=True,
		nargs="+",
		action="append",
		metavar="JSON",
		help="One or more Waterloo JSON files. Option may be repeated.",
	)
	prsr_out = prsr.add_mutually_exclusive_group(required=True)
	prsr_out.add_argument("--out", dest="out_file", metavar="HTML", help="Write HTML to HTML.")
	prsr_out.add_argument("--out-dir", dest="out_dir", metavar="DIR", help="Write HTML to DIR with generated filename.")
	prsr.add_argument("--css", dest="css_file", metavar="FILE", help="Primary CSS file to embed instead of the built-in default CSS.")
	prsr.add_argument("--additional-css", dest="additional_css_file", metavar="FILE", help="Additional CSS file to append after the primary CSS.")
	prsr.add_argument("--header-html", dest="header_html_file", metavar="FILE", help="HTML fragment file used instead of the built-in header markup.")
	prsr.add_argument("--pygments-theme", dest="pygments_theme", default=_DEFAULT_PYGMENTS_THEME, metavar="THEME", help=f"Pygments style name for rendered examples in light mode (default: {_DEFAULT_PYGMENTS_THEME}).")
	prsr.add_argument("--pygments-dark-theme", dest="pygments_dark_theme", default=_DEFAULT_PYGMENTS_DARK_THEME, metavar="THEME", help=f"Pygments style name for rendered examples in dark mode (default: {_DEFAULT_PYGMENTS_DARK_THEME}).")
	prsr.add_argument("--no-render-preamble", dest="no_render_preamble", action="store_true", help="Do not render section 'Preamble' in HTML output.")
	prsr.add_argument("--allow-raw-object-node", dest="allow_raw_object_node", action="store_true", default=True, help="Include collapsible section 'Raw object node' in HTML output (default).")
	prsr.add_argument("--no-allow-raw-object-node", dest="allow_raw_object_node", action="store_false", help="Do not include section 'Raw object node' in HTML output.")
	prsr.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return prsr

if __name__ == "__main__":
	print(__version__)
	exit(0)
