#!/usr/bin/env python3
"""
Render Waterloo JSON documents into one self-contained HTML5 page.
"""

from __future__ import annotations

import json
import html
import importlib.resources as importlib_resources
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
) -> str:
	if qid in toc_modules:
		return "mod"
	if qid in toc_classes:
		return "cls"
	if qid in toc_callables:
		return "func"
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


def _build_examples_html_map(merged: Dict[str, Any], pygments_theme: str | None = None) -> Tuple[Dict[str, str], str]:
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

	style_name = pygments_theme or "gruvbox-light"
	try:
		formatter = HtmlFormatter(cssclass="wtrl-code", nowrap=False, style=style_name)
	except Exception:
		formatter = HtmlFormatter(cssclass="wtrl-code", nowrap=False)
	css = formatter.get_style_defs(".wtrl-code")
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
		kind = _infer_kind_for_qid(qid, toc_modules, toc_classes, toc_callables)
		anchor = _build_anchor_for_qid(qid, kind)
		index.append({"label": qid, "target": qid, "kind": kind, "anchor": anchor})

	def _append_aliases(toc: Dict[str, Any], alias_kind: str) -> None:
		for qid in sorted(toc.keys()):
			parent = qid.rsplit(".", 1)[0] if "." in qid else qid
			target = parent if parent in objects else qid
			index.append({"label": qid, "target": target, "kind": alias_kind, "anchor": ""})

	_append_aliases(toc_types, "type")
	_append_aliases(toc_vars, "var")
	_append_aliases(toc_consts, "const")
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


def _build_html_doc(merged: Dict[str, Any]) -> str:
	meta = _require_dict("meta", merged.get("meta"))
	index = _build_ui_index(merged)
	pygments_theme = merged.get("meta", {}).get("pygments_theme", None)
	examples_html_map, pygments_css = _build_examples_html_map(merged, str(pygments_theme) if pygments_theme else None)

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
.wtrl-func, .wtrl_func { color:#005cc5; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-type, .wtrl_type { color:#0b7285; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-var, .wtrl_var { color:#6f42c1; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-label, .wtrl_label { color:#1f2937; font-style:italic; }
.wtrl-value, .wtrl_value { color:#b26a00; }
.wtrl-mod, .wtrl_mod { color:#374151; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-attr, .wtrl_attr { color:#7c3aed; }
.wtrl-lit, .wtrl_lit { color:#1f2937; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-dfn, .wtrl_dfn, .wtrl-term, .wtrl_term { font-style:italic; }
.wtrl-op, .wtrl_op { color:#b91c1c; }
.wtrl-file, .wtrl_file { color:#0f766e; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-cmd, .wtrl_cmd, .wtrl-opt, .wtrl_opt, .wtrl-tag, .wtrl_tag { color:#4b5563; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.wtrl-ref, .wtrl_ref { color:#005cc5; text-decoration:underline; }
.wtrl-norm, .wtrl_norm { color:#b42318; font-weight:700; }
a.wtrl-func:visited, a.wtrl-type:visited, a.wtrl-var:visited, a.wtrl-ref:visited { color:inherit; }
"""

	js = _load_render_js_source()


	css_extra = str(merged.get("meta", {}).get("css_extra", ""))
	css_override = bool(merged.get("meta", {}).get("css_override", False))
	if css_override:
		css = css_extra + ("\n" + pygments_css if pygments_css else "")
	else:
		css = css_base + ("\n" + css_extra if css_extra else "") + ("\n" + pygments_css if pygments_css else "")

	html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Waterloo HTML5 Documentation</title>
  <style>{css}</style>
</head>
<body>
  <div class="wtrl-app">
    <aside class="wtrl-side">
      <div class="wtrl-meta"><strong>Scope:</strong> <span id="wtrl-scope"></span></div>
      <div class="wtrl-meta"><strong>Flavour:</strong> <span id="wtrl-flavour"></span></div>
      <div class="wtrl-meta"><strong>Modules:</strong> <span id="wtrl-modules"></span></div>
      <div class="wtrl-meta"><strong>Classes:</strong> <span id="wtrl-num-classes"></span></div>
      <div class="wtrl-meta"><strong>Callables:</strong> <span id="wtrl-num-callables"></span></div>
      <div class="wtrl-search-row">
        <input id="wtrl-search" class="wtrl-input" list="wtrl-search-list" placeholder="Search qid / type / var / const">
        <button id="wtrl-search-clear" class="wtrl-clear" type="button" aria-label="Clear search">Clear</button>
      </div>
      <datalist id="wtrl-search-list"></datalist>
      <div id="wtrl-hitlist" class="wtrl-hitlist"></div>
    </aside>
    <main class="wtrl-main">
      <h1 id="wtrl-title" class="wtrl-title"></h1>
      <p id="wtrl-sub" class="wtrl-sub"></p>
      <section class="wtrl-block">
        <div class="wtrl-section">
          <div class="wtrl-section-head">Signature</div>
          <div id="wtrl-signature" class="wtrl-signature"></div>
        </div>
        <div id="wtrl-doc"></div>
        <div id="wtrl-examples"></div>
        <details style="margin-top:12px">
          <summary>Raw object node</summary>
          <pre id="wtrl-obj" class="wtrl-obj"></pre>
        </details>
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


def render_html5(
	*,
	input_paths: List[str],
	out_file: str | None,
	out_dir: str | None,
	css_path: str | None = None,
	pygments_theme: str | None = None,
	no_render_preamble: bool = False,
) -> str:
	merged, scope, flavour = _merge_docs_strict(input_paths)
	if no_render_preamble:
		_drop_preamble_sections(merged)
	if css_path:
		with open(css_path, "r", encoding="utf-8") as fh:
			merged["meta"]["css_extra"] = fh.read()
		merged["meta"]["css_override"] = True
	if pygments_theme:
		merged["meta"]["pygments_theme"] = pygments_theme
	html = _build_html_doc(merged)

	if (out_file is None and out_dir is None) or (out_file is not None and out_dir is not None):
		raise RuntimeError("exactly one of --out or --out-dir must be provided")

	if out_file is None:
		od = Path(str(out_dir))
		if not od.exists():
			raise RuntimeError(f"output directory does not exist: {out_dir}")
		if not od.is_dir():
			raise RuntimeError(f"output path is not a directory: {out_dir}")
		out_file = str(od / f"waterloo-docs.{scope}.{flavour}.html")

	with open(out_file, "w", encoding="utf-8") as fh:
		fh.write(html)
	return out_file
