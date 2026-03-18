#!/usr/bin/env python3
"""
Render Waterloo JSON documents into one self-contained HTML5 page.
"""

from __future__ import annotations

import json
import html
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

	js = """
const WTRL_DATA = __DATA_JSON__;
const WTRL_INDEX = __INDEX_JSON__;
const WTRL_EXAMPLES_HTML = __EXAMPLES_HTML_JSON__;

function byId(id) { return document.getElementById(id); }
const TARGET_TO_ANCHOR = new Map();
for (const e of WTRL_INDEX) {
  if (e.anchor) TARGET_TO_ANCHOR.set(e.target, e.anchor);
}
const NORM_RE = /\\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\\|/g;
const TOK_RE = /(\\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\\|)|(\\|(?:None|Self|True|False)\\|)|(\\|([A-Za-z_][A-Za-z0-9_]*)\\|`([^`]*)`)/g;
const ROLE_CLASS = {
  "func": "wtrl-func wtrl_func",
  "type": "wtrl-type wtrl_type",
  "var": "wtrl-var wtrl_var",
  "label": "wtrl-label wtrl_label",
  "value": "wtrl-value wtrl_value",
  "mod": "wtrl-mod wtrl_mod",
  "attr": "wtrl-attr wtrl_attr",
  "lit": "wtrl-lit wtrl_lit",
  "dfn": "wtrl-dfn wtrl_dfn",
  "term": "wtrl-term wtrl_term",
  "op": "wtrl-op wtrl_op",
  "file": "wtrl-file wtrl_file",
  "cmd": "wtrl-cmd wtrl_cmd",
  "opt": "wtrl-opt wtrl_opt",
  "tag": "wtrl-tag wtrl_tag",
  "ref": "wtrl-ref wtrl_ref"
};

function buildAnchorMap() {
  const m = new Map();
  for (const e of WTRL_INDEX) {
    if (e.anchor) m.set(e.anchor, e.target);
  }
  return m;
}

const anchorMap = buildAnchorMap();

function parseRefBody(body) {
  const m = body.match(/^(.*)\\s<([^>]+)>$/);
  if (!m) return { label: body, target: "" };
  return { label: m[1].trim(), target: m[2].trim() };
}

function stripOuterQuotes(s) {
  const t = String(s || "");
  if ((t.startsWith("'") && t.endsWith("'")) || (t.startsWith('"') && t.endsWith('"'))) {
    return t.slice(1, -1);
  }
  return t;
}

function inferSigName(node, targetQid) {
  const sig = (node && typeof node.signature === "object") ? node.signature : null;
  const txt = sig && typeof sig.text === "string" ? sig.text : "";
  const i = txt.indexOf("(");
  if (i > 0) return txt.slice(0, i).trim();
  return String(targetQid || "").split(".").slice(-1)[0] || "callable";
}

function makeSigLine() {
  const d = document.createElement("div");
  d.className = "wtrl-signature-line";
  return d;
}

function renderSignature(node, targetQid, container) {
  container.innerHTML = "";
  const sig = (node && typeof node.signature === "object") ? node.signature : null;
  if (!sig) return;

  const decorators = Array.isArray(node.decorators) ? node.decorators : [];
  for (const deco of decorators) {
    const line = makeSigLine();
    const sp = document.createElement("span");
    sp.className = "wtrl-attr wtrl_attr";
    sp.textContent = String(deco);
    line.appendChild(sp);
    container.appendChild(line);
  }

  const head = makeSigLine();
  const fn = document.createElement("span");
  fn.className = "wtrl-func wtrl_func";
  fn.textContent = inferSigName(node, targetQid);
  head.appendChild(fn);
  head.appendChild(document.createTextNode("("));
  container.appendChild(head);

  const params = Array.isArray(sig.parameters) ? sig.parameters : [];
  for (const p of params) {
    const line = makeSigLine();
    const kind = String(p && p.kind || "");
    const rawName = String((p && p.name) || "");
    let pname = rawName;
    if (kind === "VAR_POSITIONAL") pname = "*" + pname;
    if (kind === "VAR_KEYWORD") pname = "**" + pname;

    line.appendChild(document.createTextNode("    "));
    const psp = document.createElement("span");
    psp.className = "wtrl-var wtrl_var";
    psp.textContent = pname;
    line.appendChild(psp);

    const ann = p && p.annotation;
    if (ann !== null && ann !== undefined && String(ann).trim() !== "") {
      line.appendChild(document.createTextNode(": "));
      const asp = document.createElement("span");
      asp.className = "wtrl-type wtrl_type";
      asp.textContent = stripOuterQuotes(String(ann));
      line.appendChild(asp);
    }
    if (p && p.default !== null && p.default !== undefined) {
      line.appendChild(document.createTextNode(" = " + String(p.default)));
    }
    container.appendChild(line);
  }

  const tail = makeSigLine();
  tail.appendChild(document.createTextNode(")"));
  const ret = sig.returns;
  if (ret !== null && ret !== undefined && String(ret).trim() !== "") {
    tail.appendChild(document.createTextNode(" -> "));
    const rsp = document.createElement("span");
    rsp.className = "wtrl-type wtrl_type";
    rsp.textContent = stripOuterQuotes(String(ret));
    tail.appendChild(rsp);
  }
  container.appendChild(tail);
}

function formatSectionHead(key) {
  return String(key || "").replaceAll("_", " ");
}

function getRoleClassForSubsectionHead(path, key) {
  const section = String((path && path.length > 0) ? path[0] : "");
  if (section === "Public_types") return "wtrl-type wtrl_type";
  if (section === "Public_variables" || section === "Public_constants") return "wtrl-var wtrl_var";
  if (section === "Class_overview") return "wtrl-type wtrl_type";
  if (section === "Function_overview" || section === "Method_overview") return "wtrl-func wtrl_func";
  if (section === "Raises") return "wtrl-type wtrl_type";
  if (section === "Parameters") return "wtrl-var wtrl_var";
  return "";
}

function getRoleClassForLeaf(path) {
  const section = String((path && path.length > 0) ? path[0] : "");
  const subsection = String((path && path.length > 1) ? path[1] : "");
  if (section === "Public_functions" || section === "Public_methods") return "wtrl-func wtrl_func";
  if (section === "Public_classes") return "wtrl-type wtrl_type";
  if (section === "Derived_from") return "wtrl-type wtrl_type";
  if (section === "Contract" && subsection === "base") return "wtrl-func wtrl_func";
  if (section === "Preamble" && (subsection === "profile" || subsection === "scope" || subsection === "status")) {
    return "wtrl-value wtrl_value";
  }
  if (section === "Preamble" && subsection === "normative_sections") return "wtrl-label wtrl_label";
  return "";
}

function appendMaybeStyledText(parent, txt, roleCls) {
  if (!roleCls) {
    appendInlineTokens(parent, txt);
    return;
  }
  const sp = document.createElement("span");
  sp.className = roleCls;
  appendInlineTokens(sp, txt);
  parent.appendChild(sp);
}

const FREEFORM_SECTIONS = new Set(["Description", "Definitions", "Terminology", "Returns", "Notes"]);

function isFreeformPath(path) {
  const section = String((path && path.length > 0) ? path[0] : "");
  return FREEFORM_SECTIONS.has(section);
}

function renderFreeformText(container, txt) {
  const lines = String(txt).split(/\\r?\\n/);
  const paras = [];
  let cur = [];
  for (const raw of lines) {
    if (raw.trim() === "|") {
      if (cur.length > 0) {
        paras.push(cur.join(" "));
        cur = [];
      }
      continue;
    }
    const t = raw.trim();
    if (t) cur.push(t);
  }
  if (cur.length > 0) paras.push(cur.join(" "));
  if (paras.length === 0) paras.push(String(txt).trim());

  for (const para of paras) {
    const p = document.createElement("p");
    p.className = "wtrl-text";
    appendInlineTokens(p, para);
    container.appendChild(p);
  }
}

function isNormativeSectionsPath(path) {
  return (
    Array.isArray(path) &&
    path.length >= 2 &&
    String(path[0]) === "Preamble" &&
    String(path[1]) === "normative_sections"
  );
}

function renderCompactNormativeSections(container, items) {
  const vals = items.map(v => String(v));
  for (let i = 0; i < vals.length; i += 4) {
    const row = vals.slice(i, i + 4);
    const p = document.createElement("p");
    p.className = "wtrl-text";
    for (let j = 0; j < row.length; j += 1) {
      const sp = document.createElement("span");
      sp.className = "wtrl-label wtrl_label";
      sp.textContent = row[j];
      p.appendChild(sp);
      if (j < row.length - 1) p.appendChild(document.createTextNode(", "));
    }
    container.appendChild(p);
  }
}

function _sourcePointerToQid(src) {
  const pfx = "/__WTRL_OBJECTS__/";
  const s = String(src || "");
  if (s.startsWith(pfx)) return s.slice(pfx.length);
  return "";
}

function isDefinitionsInheritedSubsectionPath(path) {
  return (
    Array.isArray(path) &&
    path.length >= 2 &&
    String(path[0]) === "Definitions" &&
    String(path[1]) === "Definitions inherited from module"
  );
}

function renderDefinitionsInheritedContent(container, value) {
  const obj = (value && typeof value === "object" && !Array.isArray(value)) ? value : {};
  const srcQid = _sourcePointerToQid(obj.source || "");
  const anchor = srcQid ? TARGET_TO_ANCHOR.get(srcQid) : "";
  const terms = Array.isArray(obj.terms) ? obj.terms : [];

  const ul = document.createElement("ul");
  ul.className = "wtrl-list";
  for (const term of terms) {
    const li = document.createElement("li");
    if (anchor) {
      const a = document.createElement("a");
      a.className = "wtrl-ref wtrl_ref wtrl-dfn wtrl_dfn";
      a.href = "#" + anchor;
      a.textContent = String(term);
      li.appendChild(a);
    } else {
      const sp = document.createElement("span");
      sp.className = "wtrl-dfn wtrl_dfn";
      sp.textContent = String(term);
      li.appendChild(sp);
    }
    ul.appendChild(li);
  }
  container.appendChild(ul);
}

function isSeeAlsoPath(path) {
  return Array.isArray(path) && path.length >= 1 && String(path[0]) === "See_also";
}

function resolveSeeAlsoTarget(entry, currentQid) {
  const raw = String(entry || "").trim();
  if (!raw) return "";
  if (TARGET_TO_ANCHOR.has(raw)) return raw;

  const cur = String(currentQid || "");
  const curParts = cur.split(".").filter(Boolean);
  if (raw.indexOf(".") < 0 && curParts.length > 1) {
    for (let i = curParts.length - 1; i >= 1; i -= 1) {
      const cand = curParts.slice(0, i).concat([raw]).join(".");
      if (TARGET_TO_ANCHOR.has(cand)) return cand;
    }
  }

  let hit = "";
  for (const qid of TARGET_TO_ANCHOR.keys()) {
    if (qid.endsWith("." + raw)) {
      if (hit && hit !== qid) return "";
      hit = qid;
    }
  }
  return hit;
}

function appendSeeAlsoEntry(parent, entry, currentQid) {
  const raw = String(entry || "").trim();
  if (!raw) return;
  const targetQid = resolveSeeAlsoTarget(raw, currentQid);
  if (!targetQid) {
    appendMaybeStyledText(parent, raw, "wtrl-func wtrl_func");
    return;
  }
  const anchor = TARGET_TO_ANCHOR.get(targetQid);
  if (!anchor) {
    appendMaybeStyledText(parent, raw, "wtrl-func wtrl_func");
    return;
  }
  const a = document.createElement("a");
  a.className = "wtrl-ref wtrl_ref wtrl-func wtrl_func";
  a.href = "#" + anchor;
  a.textContent = raw;
  parent.appendChild(a);
}

function appendInlineTokens(parent, txt) {
  let cur = 0;
  let m;
  TOK_RE.lastIndex = 0;
  while ((m = TOK_RE.exec(txt)) !== null) {
    if (m.index > cur) parent.appendChild(document.createTextNode(txt.slice(cur, m.index)));
    if (m[1]) {
      const s = document.createElement("span");
      s.className = "wtrl-norm wtrl_norm";
      s.textContent = m[1];
      parent.appendChild(s);
    } else if (m[2]) {
      const s = document.createElement("span");
      s.className = "wtrl-value wtrl_value";
      s.textContent = m[2];
      parent.appendChild(s);
    } else if (m[3]) {
      const role = m[4];
      const body = m[5];
      const cls = ROLE_CLASS[role];
      if (!cls) {
        parent.appendChild(document.createTextNode(m[3]));
      } else if (role === "ref") {
        const rb = parseRefBody(body);
        const a = document.createElement("a");
        a.className = cls;
        a.textContent = rb.label || body;
        if (rb.target.startsWith("http://") || rb.target.startsWith("https://")) {
          a.href = rb.target;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
        } else if (rb.target.startsWith("wtrl://")) {
          const qid = rb.target.slice("wtrl://".length);
          const anchor = TARGET_TO_ANCHOR.get(qid);
          if (anchor) a.href = "#" + anchor;
        }
        if (!a.getAttribute("href")) {
          const sp = document.createElement("span");
          sp.className = cls;
          sp.textContent = m[3];
          parent.appendChild(sp);
        } else {
          parent.appendChild(a);
        }
      } else if (role === "lit" && (body === "None" || body === "Self" || body === "True" || body === "False")) {
        const s = document.createElement("span");
        s.className = "wtrl-value wtrl_value";
        s.textContent = body;
        parent.appendChild(s);
      } else {
        const s = document.createElement("span");
        s.className = cls;
        s.textContent = body;
        parent.appendChild(s);
      }
    }
    cur = TOK_RE.lastIndex;
  }
  if (cur < txt.length) parent.appendChild(document.createTextNode(txt.slice(cur)));
}

function renderValue(value, container, depth, path, currentQid) {
  const pth = Array.isArray(path) ? path : [];
  const leafRoleCls = getRoleClassForLeaf(pth);
  if (value === null || value === undefined) {
    const p = document.createElement("p");
    p.className = "wtrl-text";
    appendMaybeStyledText(p, "null", leafRoleCls);
    container.appendChild(p);
    return;
  }
  if (typeof value === "string") {
    if (isSeeAlsoPath(pth)) {
      const p = document.createElement("p");
      p.className = "wtrl-text";
      const vals = value.split(",").map(s => s.trim()).filter(Boolean);
      for (let i = 0; i < vals.length; i += 1) {
        appendSeeAlsoEntry(p, vals[i], currentQid);
        if (i < vals.length - 1) p.appendChild(document.createTextNode(", "));
      }
      container.appendChild(p);
      return;
    }
    if (isNormativeSectionsPath(pth)) {
      const vals = value.split(",").map(s => s.trim()).filter(Boolean);
      renderCompactNormativeSections(container, vals);
      return;
    }
    if (isFreeformPath(pth)) {
      renderFreeformText(container, value);
      return;
    }
    const p = document.createElement("p");
    p.className = "wtrl-text";
    appendMaybeStyledText(p, value, leafRoleCls);
    container.appendChild(p);
    return;
  }
  if (Array.isArray(value)) {
    if (isSeeAlsoPath(pth) && value.every(item => typeof item === "string")) {
      const ul = document.createElement("ul");
      ul.className = "wtrl-list";
      for (const item of value) {
        const li = document.createElement("li");
        appendSeeAlsoEntry(li, String(item), currentQid);
        ul.appendChild(li);
      }
      container.appendChild(ul);
      return;
    }
    if (isNormativeSectionsPath(pth) && value.every(item => typeof item === "string")) {
      renderCompactNormativeSections(container, value);
      return;
    }
    if (isFreeformPath(pth) && value.every(item => typeof item === "string")) {
      renderFreeformText(container, value.join("\\n"));
      return;
    }
    const ul = document.createElement("ul");
    ul.className = "wtrl-list";
    for (const item of value) {
      const li = document.createElement("li");
      if (typeof item === "string") appendMaybeStyledText(li, item, leafRoleCls);
      else renderValue(item, li, depth + 1, pth, currentQid);
      ul.appendChild(li);
    }
    container.appendChild(ul);
    return;
  }
  if (typeof value === "object") {
    if (isDefinitionsInheritedSubsectionPath(pth)) {
      renderDefinitionsInheritedContent(container, value);
      return;
    }

    let entries = Object.entries(value);
    if (depth === 0 && pth.length === 0) {
      let inheritedNode;
      entries = entries.filter(([k, v]) => {
        if (k === "definitions_inherited_from_module") {
          inheritedNode = v;
          return false;
        }
        return true;
      });
      if (inheritedNode !== undefined) {
        let injected = false;
        entries = entries.map(([k, v]) => {
          if (k !== "Definitions") return [k, v];
          injected = true;
          if (v && typeof v === "object" && !Array.isArray(v)) {
            const vv = Object.assign({}, v);
            vv["Definitions inherited from module"] = inheritedNode;
            return [k, vv];
          }
          return [k, { "Definitions inherited from module": inheritedNode }];
        });
        if (!injected) {
          entries.push(["Definitions", { "Definitions inherited from module": inheritedNode }]);
        }
      }
    }

    for (const [k, v] of entries) {
      const block = document.createElement("div");
      block.className = depth === 0 ? "wtrl-section" : "wtrl-subsection";
      const h = document.createElement("div");
      h.className = depth === 0 ? "wtrl-section-head" : "wtrl-subsection-head";
      if (depth === 0) {
        h.textContent = formatSectionHead(k);
      } else {
        if (k === "normative_sections") h.textContent = formatSectionHead(k);
        else h.textContent = k;
        const roleCls = getRoleClassForSubsectionHead(pth, k);
        if (roleCls) h.className += " " + roleCls;
      }
      block.appendChild(h);
      renderValue(v, block, depth + 1, pth.concat([k]), currentQid);
      container.appendChild(block);
    }
    return;
  }
  const p = document.createElement("p");
  p.className = "wtrl-text";
  appendMaybeStyledText(p, String(value), leafRoleCls);
  container.appendChild(p);
}

function renderHitList(entries) {
  const host = byId("wtrl-hitlist");
  host.innerHTML = "";
  for (const e of entries) {
    const btn = document.createElement("button");
    btn.className = "wtrl-hit";
    btn.type = "button";
    btn.innerHTML = `<span class="wtrl-kind">${e.kind}</span>${e.label}`;
    btn.addEventListener("click", () => selectTarget(e.target, true));
    host.appendChild(btn);
  }
}

function renderDoc(targetQid) {
  const objects = WTRL_DATA.objects || {};
  const examples = WTRL_DATA.examples || {};
  const node = objects[targetQid];
  byId("wtrl-title").textContent = targetQid || "(no selection)";
  if (!node) {
    byId("wtrl-sub").textContent = "No object found.";
    byId("wtrl-signature").innerHTML = "";
    byId("wtrl-doc").innerHTML = "";
    byId("wtrl-examples").innerHTML = "";
    byId("wtrl-obj").textContent = "";
    return;
  }
  byId("wtrl-sub").textContent = "Waterloo docstring";
  renderSignature(node, targetQid, byId("wtrl-signature"));
  const docHost = byId("wtrl-doc");
  docHost.innerHTML = "";
  if (node.doc && typeof node.doc === "object") {
    renderValue(node.doc, docHost, 0, [], targetQid);
  } else {
    const p = document.createElement("p");
    p.className = "wtrl-text";
    p.textContent = "(no doc node)";
    docHost.appendChild(p);
  }
  const exHost = byId("wtrl-examples");
  exHost.innerHTML = "";
  const exPtrs = Array.isArray(node.examples) ? node.examples : [];
  for (const ptr of exPtrs) {
    if (typeof ptr !== "string") continue;
    const pfx = "/__WTRL_EXAMPLES__/";
    if (!ptr.startsWith(pfx)) continue;
    const exKey = ptr.slice(pfx.length);
    const exNode = examples[exKey];
    if (!exNode || typeof exNode !== "object") continue;
    const sec = document.createElement("div");
    sec.className = "wtrl-section wtrl-examples";
    const h = document.createElement("div");
    h.className = "wtrl-section-head";
    h.textContent = "Example";
    sec.appendChild(h);
    if (typeof exNode.path === "string" && exNode.path) {
      const head = document.createElement("div");
      head.className = "wtrl-example-head";
      const sp = document.createElement("span");
      sp.className = "wtrl-file wtrl_file";
      sp.textContent = exNode.path;
      head.appendChild(sp);
      sec.appendChild(head);
    }
    const code = document.createElement("div");
    code.className = "wtrl-example-code";
    code.innerHTML = WTRL_EXAMPLES_HTML[exKey] || "<pre><code>(no code)</code></pre>";
    sec.appendChild(code);
    exHost.appendChild(sec);
  }
  byId("wtrl-obj").textContent = JSON.stringify(node, null, 2);
}

function selectTarget(targetQid, updateHash) {
  if (updateHash) {
    const hit = WTRL_INDEX.find(x => x.target === targetQid && x.anchor);
    if (hit && hit.anchor) {
      location.hash = hit.anchor;
    } else {
      location.hash = "";
    }
  }
  byId("wtrl-search").value = targetQid;
  renderDoc(targetQid);
}

function handleHashNavigation() {
  const h = (location.hash || "").replace(/^#/, "");
  if (!h) return false;
  const target = anchorMap.get(h);
  if (!target) return false;
  selectTarget(target, false);
  return true;
}

function setupSearch() {
  const inp = byId("wtrl-search");
  const clr = byId("wtrl-search-clear");
  const dl = byId("wtrl-search-list");
  for (const e of WTRL_INDEX) {
    const o = document.createElement("option");
    o.value = e.label;
    dl.appendChild(o);
  }
  inp.addEventListener("input", () => {
    const q = inp.value.trim().toLowerCase();
    if (!q) {
      renderHitList(WTRL_INDEX);
      return;
    }
    const hit = WTRL_INDEX.filter(e => e.label.toLowerCase().includes(q));
    renderHitList(hit);
    const exact = WTRL_INDEX.find(e => e.label === inp.value);
    if (exact) {
      selectTarget(exact.target, true);
    }
  });
  if (clr) {
    clr.addEventListener("click", () => {
      inp.value = "";
      renderHitList(WTRL_INDEX);
      inp.focus();
    });
  }
}

window.addEventListener("hashchange", () => { handleHashNavigation(); });
window.addEventListener("DOMContentLoaded", () => {
  byId("wtrl-scope").textContent = String((WTRL_DATA.meta || {}).scope || "");
  byId("wtrl-flavour").textContent = String((WTRL_DATA.meta || {}).flavour || "");
  byId("wtrl-modules").textContent = ((WTRL_DATA.meta || {}).modules || []).join(", ");
  byId("wtrl-num-classes").textContent = String(Object.keys(WTRL_DATA.toc_classes || {}).length);
  byId("wtrl-num-callables").textContent = String(Object.keys(WTRL_DATA.toc_callables || {}).length);
  setupSearch();
  renderHitList(WTRL_INDEX);
  if (!handleHashNavigation()) {
    const first = WTRL_INDEX.find(e => e.kind === "mod") || WTRL_INDEX[0];
    if (first) selectTarget(first.target, true);
  }
});
"""

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
) -> str:
	merged, scope, flavour = _merge_docs_strict(input_paths)
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
