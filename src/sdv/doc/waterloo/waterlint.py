#!/usr/bin/env python3
"""
Command line tool for validating and analyzing Waterloo docstrings.
Implementation follows the normative specification in doc/source/tools.rst.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import io
import importlib.util
import importlib.resources as importlib_resources
import sys,inspect,os,re,shutil
import traceback
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

import json

from jsonpointer import JsonPointerException, resolve_pointer
from jsonschema import Draft202012Validator
#from jsonschema import JSONDecodeError
import jsonschema.exceptions

__version__ = "0.11.2"
# - 0.11.2 [2026-05-19]	Subcommand 'walk': Option --sort.
# - 0.11.1 [2026-05-18]	Pretty format for help text.
# - 0.11.0 [2026-05-18]	Subcommand 'walk' MVP
# - 0.10.0 [2026-05-15]	Major refactoring in docitem_helper.
# - 0.9.2 [2026-05-10]	Minor fixes/changes in subcommand render-html5.
# - 0.9.1 [2026-05-01]	Minor changes in static typing
# - 0.9.0 [2026-04-25]	Refactoring render-html5: freeform sections
# - 0.8.3 [2026-04-24]	Subcommand render-html5: --css and --additional-css are now independent options.
#			Subcommand extract: diagnostics now aligned with other subcommands.
# - 0.8.2 [2026-04-22]	Options --header-html und --additional-css for subcommand render-html5.
# - 0.8.1 [2026-04-18]	Unique $id in add-example-json; MD5 replaced by SHA256 in JSON-artifacts.
# - 0.8.0 [2026-04-17]	JSON Schema for example references: this affects
#			waterlint add-example-json
#			waterlint validate-json
#			Automatic JSON Schema inference
# - 0.7.1 [2026-04-17]	Public_types/constants/variables are now rendered as free-form text.
# - 0.7.0 [2026-04-14]	Anchors for Definition Terms in render-html5.
# - 0.6.5 [2026-03-26]	Navigation buttons in render-html5
# - 0.6.4 [2026-03-20]	Analyze --ignore parameter upfront, no commas allowed.
# - 0.6.3 [2026-03-19]	Subcommand render-html5: Option --no-render-preamble
# - 0.6.2 [2026-03-19]	Subcommand render-html5: Types, Constants, Variables
# - 0.6.1 [2026-03-19]	Subcommand render-html5: JS-code separated and moved to special directory.
# - 0.6.0 [2026-03-18]	Subcommand add-example-json
# - 0.5.0 [2026-03-05]	__WTRL_SCOPES__ in JSON which allows future customization of scopes.
# - 0.4.0 [2026-02-22]	Subcommand render-json: Node "definition_inherited_from_module", see also sdv.doc.waterloo.docitem_convert.
# - 0.3.0 [2026-02-19]	Several refactorings concerning error handling, raw and JSON.
# - 0.2.4 [2026-02-12]	Subcommand render-json: traits, decorators, default output filename.
# - 0.9.1 [2026-04-27]	Subcommand version-json now prints JSON with all schema categories.
# - 0.2.3 [2026-02-12]	Subcommand version-json: prints only the JSON-schema version string.
# - 0.2.2 [2026-02-12]	Subcommand version: prints only the waterlint version string.
# - 0.2.1 [2026-02-12]	Subcommand validate-json: --schema is now optional; automatic detection applies.
# - 0.2.0 [2026-02-12]	Subcommand list-schemas
# - 0.1.0 [2026-02-12]	Versioning starts. Subcommands are "validate", "coverage", "extract", "validate-json", "render-json"

_debug = False

SOURCE_CODE_ERRORS = (AttributeError,IndexError,KeyError,NameError,AssertionError,NotImplementedError,SyntaxError)

# Import project modules while redirecting noisy stdout prints to stderr to
# satisfy the requirement that stdout stays clean unless explicitly written.
with contextlib.redirect_stdout(sys.stderr):
	import sdv.doc.waterloo.docitem as docitem
	import sdv.doc.waterloo.docitem_convert as cvrt
	import sdv.doc.waterloo.docitem_genutil as genutil
	import sdv.doc.waterloo.waterlint_render_html5 as rhtml5
	import sdv.doc.waterloo.docitem_tokenizer as tokenizer
	from sdv.doc.waterloo.docitem_helper import (
		tracer,
		get_obj_name,
		get_obj_fully_qualified_name,
		get_obj_path,
		RE_ANSI_SGR_COMPILED,
		ValidationError,
		ParseError,
		SectionNotFoundError,
		SubsectionNotFoundError,
		SCOPE_TAG_MAP,
	)

#===== Constants ==============================================#

#----- Schema versions, keep up to date -----------------------#
WTRL_JSON_SCHEMA_VERSION = "0.1.0"
WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION = "0.1.1"
WTRL_WALK_JSON_SCHEMA_VERSION = "0.0.0"

WTRL_DOCITEM_VERSION = docitem.__version__

WTRL_SCHEMA_URI_BASE = "https://sci-d-vis.com/schema"

WTRL_WALK_DEFAULT_SHOW_FIELDS = ("qualname", "kind", "scope", "file", "lineno", "included", "reason")
WTRL_WALK_ALLOWED_SHOW_FIELDS = set(WTRL_WALK_DEFAULT_SHOW_FIELDS)
WTRL_WALK_ALLOWED_SORT_FIELDS = set(WTRL_WALK_DEFAULT_SHOW_FIELDS)
WTRL_WALK_NUMERIC_SORT_FIELDS = frozenset({"lineno"})

#----- Add subcommands here -----------------------------------#
SUBCOMMANDS = (
	"validate",
	"coverage",
	"extract",
	"validate-json",
	"add-example-json",
	"gen-example-template-json",
	"render-json",
	"render-html5",
	"walk",
	"gen-minimal",
	"gen-full",
	"list-schemas",
	"version",
	"version-json",
)

#===== Helper =================================================#

def _add_traceback(tr: tracer) -> None:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	if exc_value is not None:
		tb_exc = traceback.TracebackException.from_exception(exc_value)
		for i, frame in enumerate(tb_exc.stack):
			line_txt = (frame.line or "").strip()
			frame_msg = f"#{i} \x1b[38;2;159;159;255m{frame.filename}\x1b[0m:\x1b[38;2;159;255;159m{frame.lineno}\x1b[0m in {frame.name}"
			if line_txt:
				frame_msg += f" | {line_txt}"
			tr.add_info(frame_msg, "tool")
	err_name = exc_type.__name__ if exc_type is not None else "Exception"
	err_msg = str(exc_value) if exc_value is not None else "unknown error"
	tr.add_error("TOOL-800","tool",f"{err_name}: {err_msg}")

def _emit_diagnostics(tr: tracer, dest: io.TextIOBase, strip_ansi: bool = False) -> None:
	severity = tr.Severity.DEBUG if _debug else tr.Severity.INFO
	txt = tr.str_by_severity(severity)
	if strip_ansi:
		txt = RE_ANSI_SGR_COMPILED.sub("", txt)
	dest.write(txt)

def _build_tracer_json_doc(tr: tracer) -> dict[str, Any]:
	doc: dict[str, Any] = {
		"$schema": f"{WTRL_SCHEMA_URI_BASE}/wtrl-tracer-json-{docitem.WTRL_TRACER_JSON_SCHEMA_VERSION}.schema.json",
		"$id": f"urn:waterlint:wtrl-tracer-json:{__version__}:{datetime.now().strftime('%Y%m%d%H%M%S')}",
		"__WTRL_VERSION__": {
			"waterloo": WTRL_DOCITEM_VERSION,
			"schema": docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		},
		"__WTRL_INFO__": [],
		"__WTRL_WARNING__": [],
		"__WTRL_ERROR__": [],
	}
	if _debug:
		doc["__WTRL_DEBUG__"] = []
#----- Debug notes --------------------------------------------#
	if _debug:
		for context,origin,msg in tr.gen_debug_notes():
			dentry: dict[str, Any] = {"kind": "debug", "origin": origin, "msg": msg}
			dentry["context"] = context
			cast(list[dict[str, Any]], doc["__WTRL_DEBUG__"]).append(dentry)
#----- Infos --------------------------------------------------#
	for context,origin,msg in tr.gen_infos():
		entry: dict[str, Any] = {"kind": "info", "origin": origin, "msg": msg}
		entry["context"] = context
		cast(list[dict[str, Any]], doc["__WTRL_INFO__"]).append(entry)
#----- Warnings -----------------------------------------------#
	for context,rule_id,origin,msg,details in tr.gen_warnings():
		entry = {"kind": "warning", "origin": origin, "rule-id": rule_id, "msg": msg}
		entry["context"] = context
		entry["details"] = details
		cast(list[dict[str, Any]], doc["__WTRL_WARNING__"]).append(entry)
#----- Errors -------------------------------------------------#
	for context,rule_id,origin,msg,details in tr.gen_errors():
		entry = {"kind": "error", "origin": origin, "rule-id": rule_id, "msg": msg}
		entry["context"] = context
		entry["details"] = details
		cast(list[dict[str, Any]], doc["__WTRL_ERROR__"]).append(entry)
	return doc

def _tokens_to_json_pointer(tokens: list[object]) -> str:
	if not tokens:
		return ""
	def _esc(seg: object) -> str:
		return str(seg).replace("~", "~0").replace("/", "~1")
	return "/" + "/".join(_esc(t) for t in tokens)


def _final_exit_code(base_code: int, tr: tracer, fail_on_warning: bool) -> int:
	code = base_code
	if tr.has_errors():
		code = 1
	if code == 0 and fail_on_warning and tr.has_warnings():
		code = 1
	return code


def _emit_tracer(tr: tracer, out_path: str | None, out_json_path: str | None = None) -> None:
	if out_path:
		with open(out_path, "w", encoding="utf-8") as fh:
			_emit_diagnostics(tr, fh, strip_ansi=True)
	else:
		severity = tr.Severity.DEBUG if _debug else tr.Severity.INFO
		print(tr.str_by_severity(severity),file=sys.stderr,end="")
	if out_json_path:
		doc = _build_tracer_json_doc(tr)
		with open(out_json_path, "w", encoding="utf-8") as fh:
			json.dump(doc, fh, indent=4)
			fh.write("\n")

def _load_json(path: str | None) -> cvrt.WtrlJsonNode_t:
	if path:
		with open(path, "r", encoding="utf-8") as fh:
			return cast(cvrt.WtrlJsonNode_t, json.load(fh))
	return cast(cvrt.WtrlJsonNode_t, json.load(sys.stdin))


def _safe_module_docstring(modname: str) -> str | None:
	try:
		spec = importlib.util.find_spec(modname)
		if spec is None or spec.origin is None or spec.origin == "built-in":
			return None
		path = Path(spec.origin)
		if not path.is_file():
			return None
		src = path.read_text(encoding="utf-8")
		mod_ast = ast.parse(src)
		return ast.get_docstring(mod_ast)
	except Exception:
		return None


def _validate_json_against_schema(tr: tracer, doc: cvrt.WtrlJsonNode_t, schema_path: str) -> None:
	schema = _load_json(schema_path)
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
	for e in errors:
		path_tokens = list(e.path)
		schema_path_tokens = list(e.schema_path)
		if isinstance(e,jsonschema.exceptions.ValidationError):
			details = {
				"validator": e.validator,
				"path": path_tokens,
				"schema_path": schema_path_tokens,
				"path_pointer": _tokens_to_json_pointer(path_tokens),
				"schema_path_pointer": _tokens_to_json_pointer(schema_path_tokens),
			}
			tr.add_error("JSCH-005", "tool",  "[" + docitem.get_obj_fully_qualified_name(e) + "] " + e.message,details)
		else:
			tr.add_error("JSCH-800", "tool",  "[" + docitem.get_obj_fully_qualified_name(e) + "] " + e.message,{})


def _validate_example_refs_map_against_schema(tr: tracer, ex_map: cvrt.WtrlJsonNode_t) -> bool:
	"""Validate --examples mapping JSON against the dedicated example-refs schema.

	Schema path is inferred from __WTRL_VERSION__.schema to match the mapping document.
	"""
	try:
		if not isinstance(ex_map, dict):
			tr.add_error("AXMPL-006", "tool", "Mapping JSON must be an object.")
			return False
		version_obj_raw = ex_map["__WTRL_VERSION__"]
		if not isinstance(version_obj_raw, dict) or "schema" not in version_obj_raw:
			raise KeyError
		schema_version = str(version_obj_raw["schema"])
		schema_path = Path(__file__).resolve().parent / "schema" / f"wtrl-example-refs-json-{schema_version}.schema.json"
	except Exception as exc:
		tr.add_error("AXMPL-006", "tool", "[" + docitem.get_obj_fully_qualified_name(exc) + "] Cannot infer example-refs schema path; __WTRL_VERSION__.schema missing or malformed.")
		return False
	try:
		schema = _load_json(str(schema_path))
		validator = Draft202012Validator(schema)
		errors = sorted(validator.iter_errors(ex_map), key=lambda e: list(e.path))
		for e in errors:
			path_tokens = list(e.path)
			ptr = _tokens_to_json_pointer(path_tokens) or "/"
			tr.add_error("AXMPL-006", "tool", f"[{ptr}] {e.message}")
		return len(errors) == 0
	except OSError as exc:
		tr.add_error("AXMPL-006", "tool", f"Cannot load example-refs schema: {exc}")
		return False
	except Exception as exc:
		tr.add_error("AXMPL-006", "tool", f"Example-refs schema validation failed: {exc}")
		return False


def _check_toc_pointers_json(tr: tracer, doc: cvrt.WtrlJsonNode_t, toc_key: str, rule_id: str) -> None:
	if not isinstance(doc, dict):
		tr.add_error(rule_id, "tool", f"document is not a dict, so cannot be valid.")
		return
	toc = doc.get(toc_key, {})
	if not isinstance(toc, dict):
		tr.add_error(rule_id, "tool", f"{toc_key} is not an object")
		return
	for name, ptr in toc.items():
		if not isinstance(ptr, str):
			tr.add_error(rule_id, "tool", f"{toc_key}.{name}: pointer is not a string")
			continue
		try:
			resolve_pointer(doc, ptr)
		except JsonPointerException as exc:
			tr.add_error(rule_id, "tool", f"{toc_key}.{name}: {ptr} -> {exc}")


def _validate_examples_consistency_json(tr: tracer, doc: cvrt.WtrlJsonNode_t) -> None:
	"""Validate n:m consistency between __WTRL_OBJECTS__.examples and __WTRL_EXAMPLES__.referenced_by."""
	if not isinstance(doc, dict):
		return
	objects_raw = doc.get("__WTRL_OBJECTS__", {})
	examples_raw = doc.get("__WTRL_EXAMPLES__", {})
	if not isinstance(objects_raw, dict):
		return
	if not isinstance(examples_raw, dict):
		return

	obj_qids = set(objects_raw.keys())
	ex_ptr_set = {f"/__WTRL_EXAMPLES__/{k}" for k in examples_raw.keys()}

#----- object -> examples -------------------------------------#
	for obj_qid, obj_node in objects_raw.items():
		if not isinstance(obj_node, dict):
			continue
		ex_list = obj_node.get("examples", None)
		if ex_list is None:
			continue
		if not isinstance(ex_list, list):
			tr.add_error("JSCH-006", "tool", f"__WTRL_OBJECTS__.{obj_qid}.examples is not a list.")
			continue
		for ptr in ex_list:
			if not isinstance(ptr, str):
				tr.add_error("JSCH-006", "tool", f"__WTRL_OBJECTS__.{obj_qid}.examples contains non-string pointer.")
				continue
			if ptr not in ex_ptr_set:
				tr.add_error("JSCH-006", "tool", f"__WTRL_OBJECTS__.{obj_qid}.examples contains missing pointer: {ptr}")
				continue
			ex_key = ptr.rsplit("/", 1)[-1]
			ex_node = examples_raw.get(ex_key, {})
			if not isinstance(ex_node, dict):
				continue
			ref_by = ex_node.get("referenced_by", [])
			if not isinstance(ref_by, list):
				tr.add_error("JSCH-008", "tool", f"__WTRL_EXAMPLES__.{ex_key}.referenced_by is not a list.")
				continue
			if obj_qid not in ref_by:
				tr.add_error("JSCH-008", "tool", f"{ptr} does not reference back to object: {obj_qid}")

#----- examples -> object -------------------------------------#
	for ex_key, ex_node in examples_raw.items():
		if not isinstance(ex_node, dict):
			continue
		ref_by = ex_node.get("referenced_by", [])
		if not isinstance(ref_by, list):
			tr.add_error("JSCH-007", "tool", f"__WTRL_EXAMPLES__.{ex_key}.referenced_by is not a list.")
			continue
		ptr = f"/__WTRL_EXAMPLES__/{ex_key}"
		for obj_qid_2 in ref_by:
			if not isinstance(obj_qid_2, str):
				tr.add_error("JSCH-007", "tool", f"__WTRL_EXAMPLES__.{ex_key}.referenced_by contains non-string identifier.")
				continue
			if obj_qid_2 not in obj_qids:
				tr.add_error("JSCH-007", "tool", f"__WTRL_EXAMPLES__.{ex_key}.referenced_by contains unknown object: {obj_qid_2}")
				continue
			obj_node = objects_raw.get(obj_qid_2, {})
			if not isinstance(obj_node, dict):
				continue
			ex_list = obj_node.get("examples", [])
			if not isinstance(ex_list, list):
				tr.add_error("JSCH-009", "tool", f"__WTRL_OBJECTS__.{obj_qid_2}.examples is not a list.")
				continue
			if ptr not in ex_list:
				tr.add_error("JSCH-009", "tool", f"Object {obj_qid_2} does not reference example: {ptr}")


def _compute_example_path_for_json(path_abs: Path, basedir_abs: Path | None) -> str:
	"""Compute path for JSON output (prefer basedir-relative, fallback absolute)."""
	if basedir_abs is not None:
		try:
			rel = path_abs.relative_to(basedir_abs)
			return "./" + str(rel)
		except ValueError:
			pass
	return str(path_abs)

def _render_example_refs_template(tr: tracer, org_or_project: str = "none", domain: str = "local") -> dict[str,Any]:
	nodes: dict[str, Any] = {}
	nodes["$schema"] = f"{WTRL_SCHEMA_URI_BASE}/wtrl-example-refs-json-{WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION}.schema.json"
	nodes["$id"] = f"urn:{org_or_project}:{domain}:wtrl-example-refs-json:{WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION}"
	nodes["__WTRL_VERSION__"] = {
		"waterloo": WTRL_DOCITEM_VERSION,
		"waterlint_min": __version__,
		"schema": WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION
		}
	nodes["__WTRL_EXAMPLE_REFS__"] = {}
	return nodes

def _gen_example_template_json_command(args: argparse.Namespace) -> int:
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)
	try:
		org_or_project = str(getattr(args, "org_or_project", "none"))
		domain = str(getattr(args, "domain", "local"))
		nodes = _render_example_refs_template(tr, org_or_project=org_or_project, domain=domain)
		out_file = getattr(args, "out_file", None)
		if out_file:
			with open(out_file, "w", encoding="utf-8") as fh:
				json.dump(nodes, fh, indent=4)
				fh.write("\n")
			tr.add_info(f"Example refs template written to: {out_file}", "tool")
		else:
			json.dump(nodes, sys.stdout, indent=4)
			sys.stdout.write("\n")
	except OSError as exc:
		tr.add_error("AXMPL-004", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:
		tr.add_error("AXMPL-000", "tool", f"[{docitem.get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

def _add_example_json_command(args: argparse.Namespace) -> int:
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)

	try:
		in_path = getattr(args, "input_file", None)
		examples_map_path = getattr(args, "examples_file", None)
		if not in_path:
			raise RuntimeError("--in is required.")
		if not examples_map_path:
			raise RuntimeError("--examples is required.")

		doc =_load_json(in_path)
		ex_map = _load_json(examples_map_path)
		if not isinstance(doc, dict):
			tr.add_error("AXMPL-001", "tool", "Input JSON must be an object.")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		if not isinstance(ex_map, dict):
			tr.add_error("AXMPL-001", "tool", "Mapping JSON must be an object.")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		if not _validate_example_refs_map_against_schema(tr, ex_map):
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1

		# In order to set $id we need to extract scope and flavour from the input document,
		# but we don't want to fail with an exception if they are missing or malformed,
		# as we can still add examples and update $id based on the content hash.
		# We will just use empty strings for scope and flavour in that case.
		meta = doc.get("__WTRL_META__", {})
		# We assume that the input document is valid
		if not isinstance(meta,dict):
			tr.add_error("AXMPL-000", "tool", "Input must be a valid document (__WTRL_META__ is not an object).")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		scope = str(meta.get("scope", ""))
		flavour = str(meta.get("flavour", ""))

		ex_refs = ex_map.get("__WTRL_EXAMPLE_REFS__", {})
		if not isinstance(ex_refs, dict):
			tr.add_error("AXMPL-001", "tool", "__WTRL_EXAMPLE_REFS__ is missing or not an object.")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1

		objects = doc.get("__WTRL_OBJECTS__", {})
		if not isinstance(objects, dict):
			tr.add_error("AXMPL-001", "tool", "__WTRL_OBJECTS__ is missing or not an object.")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1

		examples = doc.get("__WTRL_EXAMPLES__", {})
		if not isinstance(examples, dict):
			tr.add_error("AXMPL-001", "tool", "__WTRL_EXAMPLES__ exists but is not an object.")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		doc["__WTRL_EXAMPLES__"] = examples
		version_obj = doc.get("__WTRL_VERSION__")
		if isinstance(version_obj, dict):
			version_obj["schema"] = WTRL_JSON_SCHEMA_VERSION

			basedir_abs: Path | None = None
			if getattr(args, "basedir", None):
				basedir_abs = Path(str(args.basedir)).resolve()
				if not basedir_abs.is_dir():
					tr.add_error("AXMPL-004", "tool", f"basedir is not a directory: {args.basedir}")
					_emit_tracer(tr, out_diag, out_diag_json)
					return 1

			for obj_qid, files_any in ex_refs.items():
# Ruled out by typechecking. We know ex_refs is a JSON object and a dict, so th ekey is a string.
#				if not isinstance(obj_qid, str):
#					tr.add_error("AXMPL-002", "tool", "Mapping contains non-string object key.")
#					continue
				if obj_qid not in objects:
					tr.add_error("AXMPL-002", "tool", f"Unknown object: {obj_qid}")
					continue
				if not isinstance(files_any, list):
					tr.add_error("AXMPL-003", "tool", f"Mapping value for {obj_qid} must be a list.")
					continue

				obj_node = objects.get(obj_qid)
				if not isinstance(obj_node, dict):
					tr.add_error("AXMPL-001", "tool", f"Object node must be object: __WTRL_OBJECTS__.{obj_qid}")
					continue
				obj_examples = obj_node.get("examples", [])
				if not isinstance(obj_examples, list):
					obj_examples = []
				obj_node["examples"] = obj_examples

				for file_any in files_any:
					if not isinstance(file_any, str):
						tr.add_error("AXMPL-003", "tool", f"Example path for {obj_qid} is not a string.")
						continue
					file_raw = Path(file_any)
					if file_raw.is_absolute():
						file_abs = file_raw
					elif basedir_abs is not None:
						file_abs = (basedir_abs / file_raw).resolve()
					else:
						file_abs = file_raw.resolve()
					if not file_abs.is_file():
						tr.add_error("AXMPL-004", "tool", f"Example file does not exist: {file_any}")
						continue

					code_bytes = file_abs.read_bytes()
					hash_hex = hashlib.sha256(code_bytes).hexdigest()
					ex_key = f"sha256_{hash_hex}"
					ex_ptr = f"/__WTRL_EXAMPLES__/{ex_key}"
					try:
						code_txt = code_bytes.decode("utf-8")
					except UnicodeDecodeError:
						tr.add_error("AXMPL-004", "tool", f"Example file is not valid UTF-8: {file_abs}")
						continue

					ex_node = examples.get(ex_key)
					if ex_node is None:
						ex_node = {
							"lang": "python",
							"hash": hash_hex,
							"code": code_txt,
							"referenced_by": [],
						}
						examples[ex_key] = ex_node
					if not isinstance(ex_node, dict):
						tr.add_error("AXMPL-001", "tool", f"Example entry must be object: __WTRL_EXAMPLES__.{ex_key}")
						continue
					ref_by = ex_node.get("referenced_by", [])
					if not isinstance(ref_by, list):
						ref_by = []
					ex_node["referenced_by"] = ref_by
					ex_node["lang"] = "python"
					ex_node["hash"] = hash_hex
					ex_node["code"] = code_txt
					if getattr(args, "allow_local_paths", False):
						ex_node["path"] = _compute_example_path_for_json(file_abs, basedir_abs)
					else:
						ex_node.pop("path", None)

					if obj_qid not in ref_by:
						ref_by.append(obj_qid)
					if ex_ptr not in obj_examples:
						obj_examples.append(ex_ptr)

		for ex_any in examples.values():
			if isinstance(ex_any, dict):
				ref_by = ex_any.get("referenced_by")
				if isinstance(ref_by, list):
					# cast: a list of strings is a JSON node.
					ex_any["referenced_by"] = cast(cvrt.WtrlJsonNode_t,sorted({str(x) for x in ref_by}))
		for obj_any in objects.values():
			if isinstance(obj_any, dict):
				ex_list = obj_any.get("examples")
				if isinstance(ex_list, list):
					# cast: a list of strings is a JSON node.
					obj_any["examples"] = cast(cvrt.WtrlJsonNode_t,sorted({str(x) for x in ex_list}))

		_validate_examples_consistency_json(tr, doc)
		if tr.has_errors():
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1

		out_file = getattr(args, "out_file", None)
		out_dir = getattr(args, "out_dir", None)
		if (out_file is None and out_dir is None) or (out_file is not None and out_dir is not None):
			raise RuntimeError("exactly one of --out or --out-dir must be provided")
		if out_file is None:
			od = Path(str(out_dir))
			if not od.exists():
				raise RuntimeError(f"output directory does not exist: {out_dir}")
			if not od.is_dir():
				raise RuntimeError(f"output path is not a directory: {out_dir}")
			out_file = str(od / Path(str(in_path)).name)
		# Set a new $id from the canonical final document (without existing $id).
		doc_for_digest = {k: v for k, v in doc.items() if k != "$id"}
		canonical_doc = json.dumps(
			doc_for_digest,
			sort_keys=True,
			separators=(",", ":"),
			ensure_ascii=False,
		).encode("utf-8")
		digest = hashlib.sha256(canonical_doc).hexdigest()
		doc["$id"] = f"urn:waterlint:wtrl-json:{__version__}:{scope}:{flavour}:{digest}"
		with open(str(out_file), "w", encoding="utf-8") as fh:
			json.dump(doc, fh, indent=4)
			fh.write("\n")
		tr.add_info(f"JSON with examples written to: {out_file}")
	except SOURCE_CODE_ERRORS:
		if not out_diag:
			_add_traceback(tr)
			_emit_tracer(tr, out_diag)
			return 1
		raise
	except OSError as exc:
		tr.add_error("AXMPL-004", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except json.decoder.JSONDecodeError as exc:
		tr.add_error("AXMPL-005", "tool", f"[{docitem.get_obj_fully_qualified_name(exc)}] Input is not JSON: {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:
		tr.add_error("AXMPL-000", "tool", f"[{docitem.get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)


def _read_docstring_from_file(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def _read_docstring_from_stdin() -> str:
	return sys.stdin.read()


def _resolve_object(qname: str) -> object:
	# current_obj is not needed for fully qualified names; use None as context.
	obj, _ = docitem.resolve_object(qname, None)
	return obj


def _apply_basedir(basedir: str | None, qname: str | None) -> None:
	if not qname:
		return
# No basedir passed? Done.
	if not basedir:
		return
# Resolve basedir to absolute path.
	base_abs = basedir if basedir.startswith("/") else str((Path.cwd() / basedir).resolve())
# Not a dir? Error.
	if not Path(base_abs).is_dir():
		raise RuntimeError(f"basedir is not a directory: {basedir}")
# Update sys.path with basedir, so that we have a chance to find the module.
	if base_abs not in sys.path:
		sys.path.insert(0, base_abs)

# Yet we need more tricks...
# The main problem is to enforce that qname is really imported
# from the path specified in basedir, not from a local installation
# in ~/.local or from a system installation in /usr/local.
	parts = qname.split(".")
	prefixes: list[str] = []
	for i in range(1, len(parts) + 1):
		pfx = ".".join(parts[:i])
		pfx_path = Path(base_abs, *parts[:i])
		if pfx_path.is_dir():
			prefixes.append(pfx)
		else:
			break
# Example: For --obj sdv.doc.waterloo.docitem, prefixes is ['sdv', 'sdv.doc', 'sdv.doc.waterloo']

# Iterate over the prefixes.
	for pfx in prefixes:
# Combine with the basedir and make a path from the prefixes.
		pfx_path = Path(base_abs, *pfx.split("."))
		if pfx in sys.modules:
			mod = sys.modules[pfx]
			if hasattr(mod, "__path__"):
				paths = list(mod.__path__)
				if str(pfx_path) not in paths:
					paths.insert(0, str(pfx_path))
					mod.__path__ = paths
			continue
		spec = importlib.util.spec_from_loader(pfx, loader=None, origin="namespace")
		if spec is None:
			continue
		mod = importlib.util.module_from_spec(spec)
		mod.__path__ = [str(pfx_path)]
		sys.modules[pfx] = mod

#===== Validate ===============================================#

def _validate_command(args: argparse.Namespace) -> int:
	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#
	if getattr(args, "ignore", None):
		if "," in args.ignore:
			print(f"Commas are not allowed in --ignore; expect a single rule or a space-separated list of rules, e.g \"VLII-001 SEE-006\"")
			return 2
		for rule in args.ignore.split():
			try:
				tr.add_ignore_rule(rule)
			except RuntimeError as exc:
				print(f"Error: {exc}", file=sys.stderr)
				return 2
	try:
		if args.obj:
			_apply_basedir(getattr(args, "basedir", None), args.obj)
			obj = _resolve_object(args.obj)
# We have an object, so let's use the tracer!
			with docitem.traced_section(tr, get_obj_fully_qualified_name(obj)):
				docitem.validate_docstring(tr, obj, None, None)
		else:
# Read from file or stdin.
			if args.input_file:
				doc_txt = _read_docstring_from_file(args.input_file)
			else:
				doc_txt = _read_docstring_from_stdin()

# Structural check only: parse docstring; semantic validation needs --obj.
			di_node : docitem.docitem_base = docitem.make_docitem_tree(tr,doc_txt)
			print(
				"Note: no --obj provided, performed structural parse only.",
				file=sys.stderr,
			)
# Check these first, otherwise RuntimeError will shadow some of them.
	except SOURCE_CODE_ERRORS:
# Implementation error
		if not out_diag:
			_add_traceback(tr)
			_emit_tracer(tr, out_diag)
			return 1
		else:
			raise
	except ImportError as e:
		tr.add_error("TOOL-001","tool",str(e))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
#		raise
	except ValidationError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except ParseError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except RuntimeError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Coverage ===============================================#

def _coverage_command(args: argparse.Namespace) -> int:
	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#
	if getattr(args, "ignore", None):
		for rule in args.ignore.split():
			try:
				tr.add_ignore_rule(rule)
			except RuntimeError as exc:
				print(f"Error: {exc}", file=sys.stderr)
				return 2
	if not args.obj:
		print("Error: --obj is required for coverage.", file=sys.stderr)
		return 2
	try:
		_apply_basedir(getattr(args, "basedir", None), args.obj)
		obj = _resolve_object(args.obj)
# We have an object, so let's use the tracer!
		with docitem.traced_section(tr, get_obj_name(obj)):
			if isinstance(obj, ModuleType):
				docitem.validate_module_coverage(tr, obj)
			elif isinstance(obj, type):
				docitem.validate_class_coverage(tr, obj)
			elif callable(obj):
				print("Error: coverage for callables is not supported.", file=sys.stderr)
				return 1
			else:
				print("Error: --obj must resolve to module or class for coverage.", file=sys.stderr)
				return 1
# Check these first, otherwise RuntimeError will shadow some of them.
	except SOURCE_CODE_ERRORS:
# Implementation error
		if not out_diag:
			_add_traceback(tr)
			_emit_tracer(tr, out_diag)
			return 1
		else:
			raise
	except ImportError as e:
		tr.add_error("TOOL-001","tool",str(e))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
#		raise
	except ValidationError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except ParseError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except RuntimeError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
#		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		raise

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Extract ================================================#

def _extract_command(args: argparse.Namespace) -> int:
	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#
	try:
		if args.subsection and not args.section:
			tr.add_error("TOOL-002", "tool", "Option --subsection requires --section.")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		if args.obj:
			_apply_basedir(getattr(args, "basedir", None), args.obj)
			obj = _resolve_object(args.obj)
			doc_txt = docitem.get_obj_docstring(obj)
			if not isinstance(doc_txt, str) or not doc_txt.strip():
				tr.add_error("TOOL-003", "tool", "Resolved object has no docstring.")
				_emit_tracer(tr, out_diag, out_diag_json)
				return 1
		elif args.input_file:
			doc_txt = _read_docstring_from_file(args.input_file)
		else:
			doc_txt = _read_docstring_from_stdin()

		tree = tokenizer.parse_indent_docstring(tr, doc_txt)
# Extract section or subsection if requested, otherwise use the whole tree.
		if args.section:
			if args.subsection:
				subtree = tokenizer.get_tree_of_subsection(tr, tree, args.section, args.subsection)
				out = tokenizer.to_string_tree(subtree)
			else:
				subtree = tokenizer.get_tree_of_section(tr, tree, args.section)
				out = tokenizer.to_string_tree(subtree)
		else:
			out = tokenizer.to_string_tree(tree)

		if getattr(args, "out_file", None):
			with open(args.out_file, "w", encoding="utf-8") as fh:
				fh.write(out)
		else:
			sys.stdout.write(out)
	except SectionNotFoundError as exc:
		tr.add_error("TOOL-004", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except SubsectionNotFoundError as exc:
		tr.add_error("TOOL-005", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except ImportError as exc:
		tr.add_error("TOOL-001", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except ValidationError as exc:
		tr.add_error("TOOL-007", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except ParseError as exc:
		tr.add_error("TOOL-006", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except RuntimeError as exc:
		tr.add_error("TOOL-001", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error("TOOL-800", "tool", f"[{docitem.get_obj_fully_qualified_name(exc)}] Unexpected failure in extract command: {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Validate JSON ==========================================#

def _infer_json_doc_category(doc: cvrt.WtrlJsonNode_t) -> str:
	"""Infer JSON document category from structural __WTRL_*__ markers."""
	if not isinstance(doc, dict):
		raise ValueError("Input JSON must be an object.")
	matches: list[str] = []
	if "__WTRL_OBJECTS__" in doc and "__WTRL_SUMMARY__" in doc:
		matches.append("wtrl-walk-json")
	elif "__WTRL_OBJECTS__" in doc:
		matches.append("wtrl-json")
	if any(k in doc for k in ("__WTRL_INFO__", "__WTRL_WARNING__", "__WTRL_ERROR__", "__WTRL_DEBUG__")):
		matches.append("wtrl-tracer-json")
	if "__WTRL_EXAMPLE_REFS__" in doc:
		matches.append("wtrl-example-refs-json")
	if len(matches) == 0:
		raise ValueError("Cannot infer JSON category from structural __WTRL_*__ keys.")
	if len(matches) > 1:
		raise ValueError("Ambiguous JSON category: multiple structural __WTRL_*__ marker sets detected.")
	return matches[0]


def _infer_schema_path_from_doc(doc: cvrt.WtrlJsonNode_t) -> tuple[Path, str]:
	"""Infer local schema path from category markers + __WTRL_VERSION__.schema and cross-check metadata."""
	category = _infer_json_doc_category(doc)
	if not isinstance(doc, dict):
		raise ValueError("Input JSON must be an object.")
	schema_version: str | None = None
	version_obj_raw = doc.get("__WTRL_VERSION__")
	if isinstance(version_obj_raw, dict) and ("schema" in version_obj_raw):
		schema_version = str(version_obj_raw["schema"])
	else:
		declared_schema_fallback = doc.get("$schema")
		if isinstance(declared_schema_fallback, str):
			m = re.search(r"(wtrl-(?:json|walk-json|tracer-json|example-refs-json))-([0-9]+(?:\.[0-9]+)*)\.schema\.json", declared_schema_fallback)
			if m is not None:
				category_from_schema = m.group(1)
				schema_version = m.group(2)
				if category_from_schema != category:
					raise ValueError(f"$schema conflicts with inferred category ({category}).")
	if schema_version is None:
		raise KeyError("__WTRL_VERSION__.schema missing or malformed (and $schema fallback unavailable).")
	schema_basename = f"{category}-{schema_version}.schema.json"
	schema_path = Path(__file__).resolve().parent / "schema" / schema_basename

	declared_schema = doc.get("$schema")
	if isinstance(declared_schema, str) and (schema_basename not in declared_schema):
		raise ValueError(f"$schema conflicts with inferred category/version ({category}, {schema_version}).")
	declared_id = doc.get("$id")
	if isinstance(declared_id, str) and (category not in declared_id):
		raise ValueError(f"$id conflicts with inferred category ({category}).")
	return schema_path, category

def _validate_json_command(args: argparse.Namespace) -> int:
	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#
	try:
		doc: Dict[str,cvrt.WtrlJsonNode_t] = cast(Dict[str,cvrt.WtrlJsonNode_t],_load_json(getattr(args, "input_file", None)))
		doc_category: str | None = None
# Try schema path from argparse.
		schema_path = args.schema
		if not schema_path:
			try:
# Determine schema path from mixed strategy:
# 1) category from structural __WTRL_*__ keys
# 2) version from __WTRL_VERSION__.schema
# 3) metadata consistency checks against $schema/$id
				schema_path, doc_category = _infer_schema_path_from_doc(doc)
			except Exception as exc:
				tr.add_error("JSCH-003", "tool", "[" + docitem.get_obj_fully_qualified_name(exc) + "] " + f"Cannot infer schema path automatically: {exc}")
				_emit_tracer(tr, out_diag, out_diag_json)
				return _final_exit_code(1, tr, args.fail_on_warning)
		if doc_category is None:
			try:
				doc_category = _infer_json_doc_category(doc)
			except Exception:
				doc_category = None
		_validate_json_against_schema(tr, doc, str(schema_path))
		if doc_category == "wtrl-json":
			_check_toc_pointers_json(tr, doc, "__WTRL_TOC_MODULES__", "JPTR-001")
			_check_toc_pointers_json(tr, doc, "__WTRL_TOC_CLASSES__", "JPTR-002")
			_check_toc_pointers_json(tr, doc, "__WTRL_TOC_CALLABLES__", "JPTR-003")
			_validate_examples_consistency_json(tr, doc)
	except (IndexError, NameError, AssertionError, NotImplementedError, AttributeError):
		raise
	except OSError as exc:  # pragma: no cover - defensive
		tr.add_error("JSCH-002", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except json.decoder.JSONDecodeError as exc:  # pragma: no cover - defensive
		tr.add_error("JSCH-004", "tool", "[" + docitem.get_obj_fully_qualified_name(exc) + "] Input is not JSON: " + str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error("JSCH-000", "tool", "[" + docitem.get_obj_fully_qualified_name(exc) + "] " + str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Render JSON ============================================#

def _render_json_command(args: argparse.Namespace) -> int:
	def _collect_public_members(tree: docitem.docitem_base,label: str) -> list[str]:
		"""Extract unqualified type names from Public_types section (if present)."""
		try:
			if not tree.has_item(label):
				return []
			node = tree.item(label)
			items = [str(it).strip() for it in node.items() if str(it).strip()]
			return items
		except Exception as e:
			return []

	def _collect_traits_for_callable(obj: object) -> list[cvrt.WtrlJsonNode_t]:
		"""Collect machine-readable traits for callable-like objects."""
		traits: list[cvrt.WtrlJsonNode_t] = []
		try:
			if inspect.iscoroutinefunction(obj):
				traits.append("coroutine")
		except Exception:
			pass
		try:
			if inspect.isgeneratorfunction(obj):
				traits.append("generator")
		except Exception:
			pass
		try:
			if inspect.isasyncgenfunction(obj):
				traits.append("asyncgenerator")
		except Exception:
			pass
# Special decorators but not property.
		decorator_lines = docitem.get_obj_decorators(obj)
		for line in decorator_lines:
			if line in ("@staticmethod","@classmethod"):
				traits.append(line.strip()[1:])
		if any(line in ("@abstractmethod", "@abc.abstractmethod") for line in decorator_lines):
			traits.append("abstractmethod")
		elif bool(getattr(obj, "__isabstractmethod__", False)):
			traits.append("abstractmethod")
		return traits

	def _collect_decorators_for_callable(obj: object) -> list[cvrt.WtrlJsonNode_t]:
		return cast(list[cvrt.WtrlJsonNode_t],docitem.get_obj_decorators(obj))

	def _apply_definitions_inherited_source(doc_node: cvrt.WtrlJsonNode_t, obj: object) -> None:
		"""
		Fill `doc.definitions_inherited_from_module.source` as JSON pointer.
		The converter emits the node shape; render-json resolves the source pointer.
		"""
		if not isinstance(doc_node, dict):
			return
		inh = doc_node.get("definitions_inherited_from_module")
		if not isinstance(inh, dict):
			return
		if isinstance(obj, ModuleType):
			return
		modname = getattr(obj, "__module__", None)
		if isinstance(modname, str) and modname:
			inh["source"] = f"/__WTRL_OBJECTS__/{modname}"

	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#

#----- Security note: local paths -----------------------------#
	if getattr(args, "allow_local_paths", True):
		tr.add_info("Result JSON contains local filesystem paths; disable with --no-allow-local-paths.")
	try:
		flavour_str = args.flavour
		flavour = cvrt.flavour_tag_map.get(flavour_str)
		if flavour is None:
			flavour = cvrt.Flavour.RFC_2119
# Build a flat list of object qualified names from the --obj arguments, which may be repeated and/or grouped.
# This is related to argparse's handling of nargs='+' with multiple occurrences, which results in a list of lists.
		obj_qnames: list[str] = []
		if args.obj:
			for grp in args.obj:
				if isinstance(grp, list):
					obj_qnames.extend(grp)
				else:
					obj_qnames.append(str(grp))
		if not obj_qnames:
			print("Error: --obj is required for render-json.", file=sys.stderr)
			return 2
# Each qualified name must resolve to a module, and we need the module objects for traversal, so resolve them all upfront.
		modules: list[ModuleType] = []
		for qname in obj_qnames:
			_apply_basedir(getattr(args, "basedir", None), qname)
			mod_obj = _resolve_object(qname)
			if not isinstance(mod_obj, ModuleType):
				print(f"Error: --obj must resolve to modules for render-json (got {qname}).", file=sys.stderr)
				return 2
			modules.append(mod_obj)

#----- Object traversal and config ----------------------------#
		config = docitem.ConfigTraversal()
		if args.include_imported:
			config.enable_include_imported()
		config.disable_walk_packages()
#----- Filter by scope ----------------------------------------#
		objs: list[object] = []
		for mod in modules:
			objs.extend(docitem.gen_documentable_objects(mod, config))
# Use from argparse if available, otherwise fall back to "core" (maximimum output).
		scope_str: str = args.scope
		scope_val = SCOPE_TAG_MAP.get(scope_str, SCOPE_TAG_MAP["core"])
		scopes_filter = set([scope_val])

#----- Build version, legend and table of contents ------------#
		tree_full: dict[str, Any] = {}
		tree_full["$schema"] = f"{WTRL_SCHEMA_URI_BASE}/wtrl-json-{WTRL_JSON_SCHEMA_VERSION}.schema.json"
		tree_full["$id"] = ""
		
#..... VERSION ................................................#
		tree_full["__WTRL_VERSION__"] = {
			"waterloo": WTRL_DOCITEM_VERSION,
			"schema": WTRL_JSON_SCHEMA_VERSION,
			}
#..... META ...................................................#
		now = datetime.now().astimezone()
		date_time: str = now.isoformat(timespec='seconds')
		tree_full["__WTRL_META__"] = {
			"generated_at": date_time,
			"generator": "waterlint",
			"scope":scope_str,
			"flavour":flavour_str
			}
#..... Content ................................................#
		tree_full["__WTRL_ROLES__"] = cvrt.to_node_legend_json()
		tree_full["__WTRL_SCOPES__"] = {
			k: {"value": int(v), "description": ""} for k, v in SCOPE_TAG_MAP.items()
		}
		tree_full["__WTRL_TOC_MODULES__"] = {}
		tree_full["__WTRL_TOC_CLASSES__"] = {}
		tree_full["__WTRL_TOC_CALLABLES__"] = {}
		tree_full["__WTRL_TOC_TYPES__"] = {}
		tree_full["__WTRL_TOC_VARIABLES__"] = {}
		tree_full["__WTRL_TOC_CONSTANTS__"] = {}
		tree_full["__WTRL_OBJECTS__"] = {}

		nonaggregate_member_sections: list[Tuple[str,str]] = [
			("Public_types","__WTRL_TOC_TYPES__"),
			("Public_variables","__WTRL_TOC_VARIABLES__"),
			("Public_constants","__WTRL_TOC_CONSTANTS__")
			]
# Statistics
		num_modules_skipped_no_doc = 0
		num_modules_skipped_invalid = 0
		num_classes_skipped_no_doc = 0
		num_classes_skipped_invalid = 0
		num_callables_skipped_no_doc = 0
		num_callables_skipped_invalid = 0
		num_unknown_skipped_no_doc = 0
		num_unknown_skipped_invalid = 0
		num_modules_rendered = 0
		num_classes_rendered = 0
		num_callables_rendered = 0
		num_nonaggregate_rendered: Dict[str,int] = {
			"__WTRL_TOC_TYPES__":0,
			"__WTRL_TOC_VARIABLES__":0,
			"__WTRL_TOC_CONSTANTS__":0
			}
#----- Seen, counted, visited ---------------------------------#
		objects_counted: set[str] = set()
		modules_used: set[str] = set()
		modules_rendered: set[str] = set()
		public_members_rendered: set[str] = set()

#----- Iterate over scope-filtered objects --------------------#
		for o in objs:
			doc_txt = docitem.get_obj_docstring(o)
			name_key = get_obj_fully_qualified_name(o)
			if not doc_txt or not str(doc_txt).strip():
# No docstring or empty docstring. Count safely.
				if name_key not in objects_counted:
					if cvrt.is_obj_module(o):
						num_modules_skipped_no_doc += 1
					elif cvrt.is_obj_class(o):
						num_classes_skipped_no_doc += 1
					elif cvrt.is_obj_function(o):
						num_callables_skipped_no_doc += 1
					else:
						num_unknown_skipped_no_doc += 1
					objects_counted.add(name_key)
				continue
# Build a distinct tracer for parsing in order
# to keep the subcommand robust against malformed docstrings.
			tr_obj = tracer()
			with docitem.traced_section(tr_obj,name_key):
				try:
# Build docstring tree from docstring.
					tree_parsed = docitem.parse_indent_docstring(tr_obj, doc_txt)
					tree = docitem.make_docitem_tree_from_docstring_tree(tr_obj, tree_parsed)
# It is the caller's responsability to provide clean docstrings,
# but we can at least log problems as warnings. This helps a lot
# detecting missing a literal qualifier like r"""
					tr.append_and_defuse(tr_obj)
				except docitem.ParseError:
# Invalid docstring -> skip. Count safely.
					if name_key not in objects_counted:
						if cvrt.is_obj_module(o):
							num_modules_skipped_invalid += 1
						elif cvrt.is_obj_class(o):
							num_classes_skipped_invalid += 1
						elif cvrt.is_obj_function(o):
							num_callables_skipped_invalid += 1
						else:
							num_unknown_skipped_invalid += 1
						objects_counted.add(name_key)
					continue
# Filter by scope.
			if not cast(Any, tree).is_visible(scopes_filter):
				continue
# All entries are based on the qualified name, which is delivered by our helper.
			qname = name_key
# Collect nonaggregate public members for this object (module or class).
			for sec_label,toc_label in nonaggregate_member_sections:
				for mem_name in _collect_public_members(tree,sec_label):
					mem_qname = f"{qname}.{mem_name}"
					if mem_qname not in public_members_rendered:
						public_members_rendered.add(mem_qname)
						tree_full[toc_label][mem_qname] = f"/__WTRL_OBJECTS__/{mem_qname}"
# Count nonaggregate safely.
						if mem_qname not in objects_counted:
							num_nonaggregate_rendered[toc_label] += 1
							objects_counted.add(mem_qname)
# The docstring subsection of a type is an array of logical lines. We render them as a list in JSON.
						mem_doc = tree.item(sec_label).item(mem_name).items()
						mem_entry = cast(dict[str, Any], tree_full["__WTRL_OBJECTS__"].setdefault(mem_qname, {"doc": {}}))
						mem_entry["doc"] = {}
						mem_entry["doc_lines"] = mem_doc
#..... begin properties .......................................#
# We're still in the nonaggregate case! Properties fall in this category.
# Extract and check if it is a property
						prop_obj = inspect.getattr_static(o, mem_name)
						if isinstance(prop_obj, property):
# Extract method objects
							objs_meth_prop: list[Tuple[Callable[...,Any],str]] = []
# Check for existence, just to be sure. Insert only if it is a method object.
							for attr_name in ("fget", "fset", "fdel"):
								meth = getattr(prop_obj, attr_name)
								if meth is not None:
									objs_meth_prop.append((meth,qname + "." + mem_name + "." + attr_name))
# Iterate over {fget, fset, fdel}, if available.
							for obj_prop_meth,qname_prop_meth in objs_meth_prop:
								doc_prop_meth = docitem.get_obj_docstring(obj_prop_meth)
								if not doc_prop_meth or not str(doc_prop_meth).strip():
# No docstring or empty docstring. Count safely.
									if qname_prop_meth not in objects_counted:
										num_callables_skipped_no_doc += 1
										objects_counted.add(qname_prop_meth)
								tr_prop_meth_obj = tracer()
								try:
# Build docstring tree from docstring.
									tree_prop_meth = docitem.parse_indent_docstring(tr_prop_meth_obj, doc_prop_meth)
									node_prop_meth = docitem.make_docitem_tree_from_docstring_tree(tr_prop_meth_obj, tree_parsed)
								except docitem.ParseError:
# Invalid docstring -> skip. Count safely.
									if qname_prop_meth not in objects_counted:
										num_callables_skipped_invalid += 1
										objects_counted.add(qname_prop_meth)
									continue

								tree_full["__WTRL_TOC_CALLABLES__"][qname_prop_meth] = f"/__WTRL_OBJECTS__/{qname_prop_meth}"
								tree_sig_prop_meth = cvrt.to_node_signature_json(obj_prop_meth)
# Traits
								traits_prop_meth = _collect_traits_for_callable(obj_prop_meth)
# Decorators
								decorators_prop_meth = _collect_decorators_for_callable(obj_prop_meth)
# Count callable safely as rendered.
								if qname_prop_meth not in objects_counted:
									num_callables_rendered += 1
									objects_counted.add(qname_prop_meth)
# Docstring handling: same for modules, classes, and callables.
								tree_doc = cvrt.to_node_docstring_tree_json(tree_prop_meth, flavour)
								_apply_definitions_inherited_source(tree_doc, obj_prop_meth)
								entry_prop_meth = dict(tree_sig_prop_meth)
# Traits
								if traits_prop_meth:
									entry_prop_meth["traits"] = traits_prop_meth
# Decorators
								if decorators_prop_meth:
									entry_prop_meth["decorators"] = decorators_prop_meth
								entry_prop_meth["doc"] = tree_doc
								tree_full["__WTRL_OBJECTS__"][qname_prop_meth] = entry_prop_meth
#..... end properties .........................................#


			# toc + signature
			tree_sig: dict[str, cvrt.WtrlJsonNode_t] = {}
			tree_traits: list[cvrt.WtrlJsonNode_t] = []
			tree_decorators: list[cvrt.WtrlJsonNode_t] = []
# Regular cases for the object from traversal
			if cvrt.is_obj_module(o):
				modules_used.add(docitem.get_obj_name(o))
				tree_full["__WTRL_TOC_MODULES__"][qname] = f"/__WTRL_OBJECTS__/{qname}"
# Store path if we allow this (security issue b/c local file system structure is unveiled).
				tree_full["__WTRL_OBJECTS__"][qname] = {"path": docitem.get_obj_path(o)} if args.allow_local_paths else {}
# Count module safely as rendered.
				if qname not in modules_rendered:
					modules_rendered.add(qname)
				if qname not in objects_counted:
					num_modules_rendered += 1
					objects_counted.add(qname)
			elif cvrt.is_obj_class(o):
				tree_full["__WTRL_TOC_CLASSES__"][qname] = f"/__WTRL_OBJECTS__/{qname}"
				ctor = getattr(o, "__init__", None)
				if callable(ctor):
					tree_sig = cvrt.to_node_signature_json(cast(Callable[..., Any], ctor))
# Traits
					tree_traits = _collect_traits_for_callable(ctor)
# Decorators
					tree_decorators = _collect_decorators_for_callable(ctor)
# Count class safely as rendered.
				if qname not in objects_counted:
					num_classes_rendered += 1
					objects_counted.add(qname)
			elif cvrt.is_obj_function(o):
				tree_full["__WTRL_TOC_CALLABLES__"][qname] = f"/__WTRL_OBJECTS__/{qname}"
				tree_sig = cvrt.to_node_signature_json(o)
# Traits
				tree_traits = _collect_traits_for_callable(o)
# Decorators
				tree_decorators = _collect_decorators_for_callable(o)
# Count callable safely as rendered.
				if qname not in objects_counted:
					num_callables_rendered += 1
					objects_counted.add(qname)
			else:
				continue
# Docstring handling: same for modules, classes, and callables.
			tree_doc = cvrt.to_node_docstring_tree_json(tree_parsed, flavour)
			_apply_definitions_inherited_source(tree_doc, o)
			entry = dict(tree_sig)
# Traits
			if tree_traits:
				entry["traits"] = tree_traits
# Decorators
			if tree_decorators:
				entry["decorators"] = tree_decorators
			entry["doc"] = tree_doc
# Path
			if args.allow_local_paths and isinstance(o, ModuleType):
				entry = {"path": docitem.get_obj_path(o)} | entry
			tree_full["__WTRL_OBJECTS__"][qname] = entry

#----- begin modules referred to by objects from traversal ----#
# We would like to see each module referred to by any of the rendered objects
# in the module TOC ans __WTRL_OBJECTS__ section. So, extract module and keep in mind.
			modname = docitem.get_obj_name(o) if isinstance(o, ModuleType) else getattr(o, "__module__", None)
			if modname:
				modules_used.add(modname)
# Add referred module name to TOC.
				jsnode_toc_modules:dict[str, cvrt.WtrlJsonNode_t] = tree_full["__WTRL_TOC_MODULES__"]
				if modname not in jsnode_toc_modules:
					jsnode_toc_modules[modname] = f"/__WTRL_OBJECTS__/{modname}"
# Add referred module name to __WTRL_OBJECTS__, with empty "doc" node.
				if modname not in tree_full["__WTRL_OBJECTS__"]:
					entry_stub: dict[str, cvrt.WtrlJsonNode_t] = {}
# We already know the path to the module.
					if args.allow_local_paths:
						entry_stub["path"] = docitem.get_obj_path(sys.modules.get(modname))
# Leave empty, fill later after AST analysis.
					entry_stub["doc"] = {}
					tree_full["__WTRL_OBJECTS__"][modname] = entry_stub
#----- end modules referred to by objects from traversal ------#
# End of object loop.

#----- begin modules referred to by objects from traversal ----#
		# ensure all referenced modules appear in TOC/OBJECTS
		for modname in sorted(modules_used):
			if modname not in modules_rendered:
				entry2: dict[str, cvrt.WtrlJsonNode_t] = cast(dict[str, cvrt.WtrlJsonNode_t],tree_full["__WTRL_OBJECTS__"].get(modname, {}))
				if args.allow_local_paths and "path" not in entry2:
					entry2["path"] = docitem.get_obj_path(sys.modules.get(modname))
# Various attempts to get the module docstring.
				mod_doc = None
				mod_obj = sys.modules.get(modname)
				if mod_obj is not None:
					mod_doc = docitem.get_obj_docstring(mod_obj)
# Scan python AST in order to get module docstring!
				if not mod_doc:
					mod_doc = _safe_module_docstring(modname)
				if mod_doc:
					try:
						tr_tmp = tracer()
						mod_tree_parsed = docitem.parse_indent_docstring(tr_tmp, mod_doc)
						mod_tree = docitem.make_docitem_tree_from_docstring_tree(tr_tmp, mod_tree_parsed)
# Render module docstring if the module is visible for the given scope; otherwise render stub.
						if cast(Any, mod_tree).is_visible(scopes_filter):
							entry2["doc"] = cvrt.to_node_docstring_tree_json(mod_tree_parsed, flavour)
						else:
							entry2["doc"] = {}
# In both cases consider module as done.
						if modname not in modules_rendered:
							modules_rendered.add(modname)
# Count referenced module safely as rendered.
							if modname not in objects_counted:
								num_modules_rendered += 1
								objects_counted.add(modname)
# Collect nonaggregate public members for this object (module).
						for sec_label,toc_label in nonaggregate_member_sections:
							for mem_name in _collect_public_members(mod_tree,sec_label):
# The qualified name is constructed from the module name and the member name.
								mem_qname = f"{modname}.{mem_name}"
								if mem_qname not in public_members_rendered:
									public_members_rendered.add(mem_qname)
									toc_map = cast(dict[str, Any], tree_full[toc_label])
									toc_map[mem_qname] = f"/__WTRL_OBJECTS__/{mem_qname}"
# Count nonaggregate safely.
									if mem_qname not in objects_counted:
										num_nonaggregate_rendered[toc_label] += 1
										objects_counted.add(mem_qname)
# The docstring subsection of a type is an array of logical lines. We render them as a list in JSON.
									mem_doc = mod_tree.item(sec_label).item(mem_name).items()
									mem_entry = cast(dict[str, Any], tree_full["__WTRL_OBJECTS__"].setdefault(mem_qname, {"doc": {}}))
									mem_entry["doc"] = {}
									mem_entry["doc_lines"] = mem_doc
					except Exception:
						entry2["doc"] = {}
				else:
					entry2["doc"] = {}
				tree_full["__WTRL_OBJECTS__"][modname] = entry2
#----- end modules referred to by objects from traversal ------#

#----- Build deterministic document id ------------------------#
		qnames_rendered = sorted(cast(dict[str, Any], tree_full["__WTRL_OBJECTS__"]).keys())
		qnames_blob = "\n".join(qnames_rendered).encode("utf-8")
		render_hash = hashlib.sha256(qnames_blob).hexdigest()
		tree_full["$id"] = f"urn:waterlint:wtrl-json:{__version__}:{scope_str}:{flavour_str}:{render_hash}"

#----- Store diagnostics. Don't change without updating pytest #
		tr.add_info(f"Num modules skipped (no docstring / invalid)  : {num_modules_skipped_no_doc} / {num_modules_skipped_invalid}.")
		tr.add_info(f"Num classes skipped (no docstring / invalid)  : {num_classes_skipped_no_doc} / {num_classes_skipped_invalid}.")
		tr.add_info(f"Num callables skipped (no docstring / invalid): {num_callables_skipped_no_doc} / {num_callables_skipped_invalid}.")
		tr.add_info(f"Num <unknown> skipped (no docstring / invalid): {num_unknown_skipped_no_doc} / {num_unknown_skipped_invalid}.")
		tr.add_info(f"Num modules rendered  : {num_modules_rendered}.")
		tr.add_info(f"Num classes rendered  : {num_classes_rendered}.")
		tr.add_info(f"Num callables rendered: {num_callables_rendered}.")
		tr.add_info(f"Num types rendered    : {num_nonaggregate_rendered['__WTRL_TOC_TYPES__']}.")
		tr.add_info(f"Num variables rendered: {num_nonaggregate_rendered['__WTRL_TOC_VARIABLES__']}.")
		tr.add_info(f"Num constants rendered: {num_nonaggregate_rendered['__WTRL_TOC_CONSTANTS__']}.")

#----- Dump JSON result ---------------------------------------#
		if getattr(args, "out_prefix", None) and not getattr(args, "out_dir", None):
			raise RuntimeError("--out-prefix requires --out-dir.")
		if args.out_file:
# --out is given? Dump to file.
			with open(args.out_file, "w", encoding="utf-8") as fh:
				json.dump(tree_full, fh, indent=4)
		elif getattr(args, "out_dir", None):
# If --out-dir is specified, we construct the filename by a strict pattern,
# which contains scope and flavour as segments.
			out_dir = Path(args.out_dir)
			if not out_dir.exists():
				raise RuntimeError(f"output directory does not exist: {args.out_dir}")
			if not out_dir.is_dir():
				raise RuntimeError(f"output path is not a directory: {args.out_dir}")
			if len(obj_qnames) > 1 and not getattr(args, "out_prefix", None):
				raise RuntimeError("--out-prefix is required with --out-dir when multiple --obj are given.")
# The user can still set the filename prefix without impact on the pattern.
			if getattr(args, "out_prefix", None):
				base_name = str(args.out_prefix)
			else:
				base_name = str(obj_qnames[0])
# The pattern:
			out_name = f"{base_name}.wtrl.{scope_str}.{flavour_str}.json"
			out_path = out_dir / out_name
			with open(out_path, "w", encoding="utf-8") as fh:
				json.dump(tree_full, fh, indent=4)
		else:
			json.dump(tree_full, sys.stdout, indent=4)
			sys.stdout.write("\n")
#----- Catch implementation bugs ------------------------------#
	except (IndexError, NameError, AssertionError, NotImplementedError, AttributeError, TypeError):
		raise
#----- Catch errors from rendering JSON -----------------------#
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error("JSCH-700", "tool", "[" + docitem.get_obj_fully_qualified_name(exc) + "] " + str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Render HTML5 ===========================================#

def _render_html5_command(args: argparse.Namespace) -> int:
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
		out_path = rhtml5.render_html5(
			tr,
			input_paths=in_files,
			out_file=getattr(args, "out_file", None),
			out_dir=getattr(args, "out_dir", None),
			css_path=getattr(args, "css_file", None),
			additional_css_path=getattr(args, "additional_css_file", None),
			header_html_path=getattr(args, "header_html_file", None),
			pygments_theme=getattr(args, "pygments_theme", None),
			no_render_preamble=getattr(args, "no_render_preamble", False),
			allow_raw_object_node=getattr(args, "allow_raw_object_node", True),
		)
		if not out_path:
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		tr.add_info(f"HTML5 documentation written to: {out_path}")
	except SOURCE_CODE_ERRORS:
		if not out_diag:
			_add_traceback(tr)
			_emit_tracer(tr, out_diag)
			return 1
		raise
	except Exception as exc:
		tr.add_error("RHTM-001", "tool", f"[{docitem.get_obj_fully_qualified_name(exc)}] Unexpected failure in render-html5 command: {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Generate ===============================================#

def _leading_ws_width(s: str) -> int:
	width = 0
	for ch in s:
		if ch == "\t" or ch == " ":
			width += 1
		else:
			break
	return width


def _retab_docstring(doc: str, indent_mode: str) -> str:
	if indent_mode == "tab":
		return doc
	indent_unit = "    "
	lines = doc.splitlines()
	out_lines: list[str] = []
	for line in lines:
		if not line:
			out_lines.append(line)
			continue
		wsw = _leading_ws_width(line)
		if wsw == 0:
			out_lines.append(line)
			continue
		stripped = line.lstrip("\t ")
		out_lines.append((indent_unit * wsw) + stripped)
	return "\n".join(out_lines) + ("\n" if doc.endswith("\n") else "")


def _collect_generation_targets(
	tr: tracer,
	obj_qnames: list[str],
	basedir: str | None,
	recursive: bool,
	missing_only: bool,
) -> list[object]:
	seen_qnames: set[str] = set()
	targets: list[object] = []
	cfg = docitem.ConfigTraversal()
	for qname in obj_qnames:
		_apply_basedir(basedir, qname)
# Maybe the cast is not good here.
		obj = _resolve_object(qname)
		if not docitem.is_obj_documentable(obj):
			continue
		root = obj
		candidates: list[object]
		if recursive:
			candidates = list(docitem.gen_documentable_objects(root, cfg))
		else:
			candidates = [root]
		for cand in candidates:
			fqname = get_obj_fully_qualified_name(cand)
			if fqname in seen_qnames:
				continue
			if missing_only:
				doc_txt = docitem.get_obj_docstring(cand)
				if isinstance(doc_txt, str) and doc_txt.strip():
					continue
			seen_qnames.add(fqname)
			targets.append(cand)
	return targets


def _render_generation_json(
	mode: str,
	recursive: bool,
	missing_only: bool,
	targets: list[object],
	indent_mode: str,
) -> dict[str, Any]:
	nodes: list[dict[str, Any]] = []
	for obj in targets:
		profile = genutil.infer_docstring_profile(obj)
		if mode == "minimal":
			doc = genutil.generate_minimal_docstring(obj, profile=profile)
		else:
			doc = genutil.generate_full_docstring(obj, profile=profile)
		nodes.append(
			{
				"qualified_identifier": get_obj_fully_qualified_name(obj),
				"kind": profile,
				"docstring": _retab_docstring(doc, indent_mode),
			}
		)
	return {
		"mode": mode,
		"recursive": recursive,
		"missing_only": missing_only,
		"count": len(nodes),
		"objects": nodes,
	}


def _generate_command(args: argparse.Namespace, mode: str) -> int:
	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#
	try:
		obj_qnames: list[str] = []
		if args.obj:
			for grp in args.obj:
				if isinstance(grp, list):
					obj_qnames.extend(grp)
				else:
					obj_qnames.append(str(grp))
		if not obj_qnames:
			print("Error: --obj is required.", file=sys.stderr)
			return 2
		fmt = args.format
		if fmt is None:
			fmt = "json" if args.recursive else "raw"
		targets = _collect_generation_targets(
			tr,
			obj_qnames=obj_qnames,
			basedir=getattr(args, "basedir", None),
			recursive=bool(args.recursive),
			missing_only=bool(args.missing_only),
		)
		if fmt == "raw":
			if len(targets) != 1:
				tr.add_error(
					"TOOL-820",
					"tool",
					f"--format raw requires exactly one target object, got {len(targets)}.",
				)
				_emit_tracer(tr, out_diag, out_diag_json)
				return 2
			profile = genutil.infer_docstring_profile(targets[0])
			if mode == "minimal":
				doc = genutil.generate_minimal_docstring(targets[0], profile=profile)
			else:
				doc = genutil.generate_full_docstring(targets[0], profile=profile)
			doc = _retab_docstring(doc, args.indent)
			if args.out_file:
				with open(args.out_file, "w", encoding="utf-8") as fh:
					fh.write(doc)
			else:
				sys.stdout.write(doc)
		else:
			doc_json = _render_generation_json(
				mode=mode,
				recursive=bool(args.recursive),
				missing_only=bool(args.missing_only),
				targets=targets,
				indent_mode=args.indent,
			)
			if args.out_file:
				with open(args.out_file, "w", encoding="utf-8") as fh:
					json.dump(doc_json, fh, indent=2)
					fh.write("\n")
			else:
				json.dump(doc_json, sys.stdout, indent=2)
				sys.stdout.write("\n")
	except SOURCE_CODE_ERRORS:
		if not out_diag:
			_add_traceback(tr)
			_emit_tracer(tr, out_diag)
			return 1
		raise
	except Exception as exc:
		tr.add_error("TOOL-821", "tool", f"[{docitem.get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Walk ===================================================#

def _walk_normalize_path(path_text: str | None) -> Path | None:
	if not path_text:
		return None
	try:
		return Path(path_text).expanduser().resolve()
	except Exception:
		try:
			return Path(os.path.abspath(os.path.expanduser(path_text)))
		except Exception:
			return None


def _walk_path_is_under(path: Path, prefix: Path) -> bool:
	try:
		return path == prefix or path.is_relative_to(prefix)
	except Exception:
		return False


def _walk_build_path_labels(entries: list[dict[str, Any]], basedir: str | None) -> list[tuple[str, Path]]:
	basedir_path = _walk_normalize_path(basedir)
	candidate_dirs: list[Path] = []
	seen_candidates: set[str] = set()
	for entry in entries:
		file_txt = entry.get("file")
		if not isinstance(file_txt, str) or not file_txt:
			continue
		file_path = _walk_normalize_path(file_txt)
		if file_path is None:
			continue
		if basedir_path is not None and _walk_path_is_under(file_path, basedir_path):
			continue
		parent = file_path.parent
		key = str(parent)
		if key in seen_candidates:
			continue
		seen_candidates.add(key)
		candidate_dirs.append(parent)
	candidate_dirs.sort(key=lambda p: (len(p.parts), str(p)))
	selected_dirs: list[Path] = []
	for candidate in candidate_dirs:
		if any(_walk_path_is_under(candidate, existing) for existing in selected_dirs):
			continue
		selected_dirs.append(candidate)
	selected_dirs.sort(key=lambda p: (len(p.parts), str(p)))
	labels: list[tuple[str, Path]] = []
	if basedir_path is not None:
		labels.append(("BASEDIR", basedir_path))
	for idx, prefix in enumerate(selected_dirs):
		labels.append((f"PATH{idx}", prefix))
	return labels


def _walk_compress_path(path_text: str | None, path_labels: list[tuple[str, Path]]) -> str | None:
	if not isinstance(path_text, str) or not path_text:
		return path_text
	path = _walk_normalize_path(path_text)
	if path is None:
		return path_text
	best_label: str | None = None
	best_prefix: Path | None = None
	for label, prefix in path_labels:
		if not _walk_path_is_under(path, prefix):
			continue
		if best_prefix is None or len(prefix.parts) > len(best_prefix.parts):
			best_label = label
			best_prefix = prefix
	if best_label is None or best_prefix is None:
		return str(path)
	try:
		rel = path.relative_to(best_prefix)
	except Exception:
		return str(path)
	rel_txt = str(rel)
	if not rel_txt or rel_txt == ".":
		return f"{{{best_label}}}"
	return f"{{{best_label}}}/{rel_txt}"


def _walk_sort_text(text: object) -> str:
	txt = str(text).casefold()
	return "".join(ch for ch in txt if ch != "_")


def _walk_sort_key_for_field(entry: dict[str, Any], field: str) -> tuple[int, object]:
	value = entry.get(field)
	if value is None:
		if field in WTRL_WALK_NUMERIC_SORT_FIELDS:
			return (0, 0)
		return (0, "")
	if field in WTRL_WALK_NUMERIC_SORT_FIELDS:
		try:
			return (1, int(value))
		except Exception:
			try:
				return (1, int(str(value).strip()))
			except Exception:
				return (1, 0)
	if isinstance(value, bool):
		return (1, _walk_sort_text("true" if value else "false"))
	return (1, _walk_sort_text(value))


def _walk_sort_entries(entries: list[dict[str, Any]], sort_fields: list[str]) -> None:
	for field in reversed(sort_fields):
		entries.sort(key=lambda entry, field=field: _walk_sort_key_for_field(entry, field))


def _walk_kind(obj: object) -> str:
	if docitem.is_obj_module(obj):
		return "module"
	if docitem.is_obj_class(obj):
		return "class"
	if isinstance(obj, property):
		return "property"
	if docitem.is_obj_method_like(obj):
		return "method"
	if docitem.is_obj_function(obj):
		return "function"
	return "unknown"


def _walk_lineno(obj: object) -> int | None:
	target: object = obj
	if isinstance(obj, property):
		for accessor in (obj.fget, obj.fset, obj.fdel):
			if accessor is not None:
				target = accessor
				break
	try:
		_, lineno = inspect.getsourcelines(target)
		return lineno
	except Exception:
		return None


def _walk_scope_text(doc_tree: object) -> str:
	try:
		scopes = cast(Any, doc_tree).scopes()
	except Exception:
		return "unknown"
	if not scopes:
		return "unknown"
	try:
		items = []
		for sc in sorted(scopes, key=lambda s: getattr(s, "value", 0)):
			name = getattr(sc, "name", None)
			items.append(str(name).lower() if isinstance(name, str) else str(sc).lower())
		return ",".join(items) if items else "unknown"
	except Exception:
		return "unknown"

# Analyze for reason, included, scope
def _walk_analyze_object(obj: object) -> tuple[str, bool, str]:
	doc_txt = docitem.get_obj_docstring(obj)
	if not doc_txt:
		return ("no_doc", False, "unknown")
	tmp_tr = tracer()
	try:
		tree = docitem.make_docitem_tree(tmp_tr, doc_txt)
	except Exception:
		return ("invalid", False, "unknown")
	if tmp_tr.has_errors():
		return ("invalid", False, "unknown")
	return ("included", True, _walk_scope_text(tree))

# Standardized representation for boolean and None
def _walk_format_table_value(val: object) -> str:
	if isinstance(val, bool):
		return "true" if val else "false"
	if val is None:
		return "null"
	return str(val)


def _walk_render_text(entries: list[dict[str, Any]], show_fields: list[str], path_labels: list[tuple[str, Path]] | None = None) -> str:
	lines: list[str] = []
	rows: list[list[str]] = []
# Legend: Label representing the path prefix and the path prefix itself.
	if path_labels and "file" in show_fields:
		for label, prefix in path_labels:
			lines.append(f"{label}: {prefix}")
		if entries:
			lines.append("")
# Entries:
	for entry in entries:
		row: list[str] = []
		for field in show_fields:
			value = entry.get(field)
# For field 'file' compress the path.
			if field == "file":
				value = _walk_compress_path(cast(str | None, value), path_labels or [])
			row.append(_walk_format_table_value(value))
		rows.append(row)
	if show_fields:
# For pretty printing, measure the maximum required size for each column.
# First the header (elements in show fields), then the entries.
		widths = [len(field) for field in show_fields]
		for row in rows:
			for idx, cell in enumerate(row):
				widths[idx] = max(widths[idx], len(cell))
# Build list of lines. Make sure there are at least
# two white spaces between the columns.
		lines.append("  ".join(field.ljust(widths[idx]) for idx, field in enumerate(show_fields)))
		for row in rows:
			lines.append("  ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row)))
	return "\n".join(lines) + ("\n" if lines else "")


def _walk_build_json_doc(
	entries: list[dict[str, Any]],
	basedir: str | None,
	obj_qname: str,
	include_imported: bool,
	show_fields: list[str],
) -> dict[str, Any]:
	count_by_kind: dict[str, int] = {}
	count_by_scope: dict[str, int] = {}
	count_by_reason: dict[str, int] = {}
	included_count = 0
	for entry in entries:
		kind = str(entry.get("kind", "unknown"))
		scope = str(entry.get("scope", "unknown"))
		reason = str(entry.get("reason", "unknown"))
		count_by_kind[kind] = count_by_kind.get(kind, 0) + 1
		count_by_scope[scope] = count_by_scope.get(scope, 0) + 1
		count_by_reason[reason] = count_by_reason.get(reason, 0) + 1
		if bool(entry.get("included", False)):
			included_count += 1
	doc: dict[str, Any] = {
		"$schema": f"{WTRL_SCHEMA_URI_BASE}/wtrl-walk-json-{WTRL_WALK_JSON_SCHEMA_VERSION}.schema.json",
		"$id": f"urn:waterlint:wtrl-walk-json:{__version__}:{datetime.now().strftime('%Y%m%d%H%M%S')}",
		"__WTRL_VERSION__": {
			"waterloo": WTRL_DOCITEM_VERSION,
			"schema": WTRL_WALK_JSON_SCHEMA_VERSION,
		},
		"__WTRL_META__": {
			"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
			"generator": "waterlint.walk",
			"basedir": basedir,
			"obj": obj_qname,
			"include_imported": include_imported,
			"show": show_fields,
		},
		"__WTRL_SUMMARY__": {
			"total": len(entries),
			"included": included_count,
			"excluded": len(entries) - included_count,
			"by_kind": count_by_kind,
			"by_scope": count_by_scope,
			"by_reason": count_by_reason,
		},
		"__WTRL_OBJECTS__": entries,
	}
	return doc


def _walk_command(args: argparse.Namespace) -> int:
	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	= getattr(args, "out_diag", None)
	out_diag_json	= getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#
	try:
		show_raw = getattr(args, "show", None)
		if show_raw:
			show_fields = [p.strip() for p in str(show_raw).split(",") if p.strip()]
		else:
			show_fields = list(WTRL_WALK_DEFAULT_SHOW_FIELDS)
		invalid_show = [f for f in show_fields if f not in WTRL_WALK_ALLOWED_SHOW_FIELDS]
		if invalid_show:
			print(f"Error: unsupported --show field(s): {', '.join(invalid_show)}", file=sys.stderr)
			return 2

		sort_raw = getattr(args, "sort", None)
		if sort_raw:
			sort_fields = [p.strip() for p in str(sort_raw).split(",") if p.strip()]
		else:
			sort_fields = []
		invalid_sort = [f for f in sort_fields if f not in WTRL_WALK_ALLOWED_SORT_FIELDS]
		if invalid_sort:
			print(f"Error: unsupported --sort field(s): {', '.join(invalid_sort)}", file=sys.stderr)
			return 2

		obj_qname = getattr(args, "obj", None)
		if not isinstance(obj_qname, str) or not obj_qname.strip():
			print("Error: --obj is required for walk.", file=sys.stderr)
			return 2
		obj_qname = obj_qname.strip()
		_apply_basedir(getattr(args, "basedir", None), obj_qname)
		obj = _resolve_object(obj_qname)
		#----- Object traversal and config ----------------------------#
		config = docitem.ConfigTraversal()
		if getattr(args, "include_imported", True):
			config.enable_include_imported()
		config.disable_walk_packages()
		#----- Walk and build list of entries -------------------------#
		entries: list[dict[str, Any]] = []
		for o in docitem.gen_documentable_objects(obj, config):
			reason, included, scope_text = _walk_analyze_object(o)
			entry: dict[str, Any] = {
				"qualname": get_obj_fully_qualified_name(o),
				"kind": _walk_kind(o),
				"scope": scope_text,
				"file": get_obj_path(o),
				"lineno": _walk_lineno(o),
				"included": included,
				"reason": reason,
			}
			entries.append(entry)
		if sort_fields:
			_walk_sort_entries(entries, sort_fields)
		#----- Prepare path compression for better readability --------#
		path_labels = _walk_build_path_labels(entries, getattr(args, "basedir", None))

		out_json = getattr(args, "out_json", None)
		out_file = getattr(args, "out_file", None)
		if out_json:
			# Render JSON
			doc = _walk_build_json_doc(entries, getattr(args, "basedir", None), obj_qname, getattr(args, "include_imported", True), show_fields)
			with open(out_json, "w", encoding="utf-8") as fh:
				json.dump(doc, fh, indent=4)
				fh.write("\n")
		else:
			# Render human readable text, apply labels from path compression.
			txt = _walk_render_text(entries, show_fields, path_labels)
			if out_file:
				with open(out_file, "w", encoding="utf-8") as fh:
					fh.write(txt)
			else:
				sys.stdout.write(txt)
		# Write summary to tracer.
		tr.add_info(f"Num objects traversed: {len(entries)}.", "tool")
		tr.add_info(f"Num objects included: {sum(1 for e in entries if e.get('included'))}.", "tool")
		tr.add_info(f"Num objects excluded: {sum(1 for e in entries if not e.get('included'))}.", "tool")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 0
	except Exception:
		_add_traceback(tr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

#===== Help topic  ============================================#

def _help_validate() -> None:
	print("Validate a docstring.")

def _help_coverage() -> None:
	print("Check for documentation coverage of a module or class.")

def _help_extract() -> None:
	print("Extract some portion of a docstring.")

def _help_validate_json() -> None:
	print("Validate a Waterloo JSON document against the published JSON Schema.")

def _help_add_example_json() -> None:
	print("Add/update __WTRL_EXAMPLES__ and object-level examples pointers in Waterloo JSON.")

def _help_gen_example_template_json() -> None:
	print("Generate template JSON for __WTRL_EXAMPLE_REFS__ mappings.")

def _help_render_json() -> None:
	print("Render Waterloo objects (module) to Waterloo JSON.")

def _help_render_html5() -> None:
	print("Render Waterloo JSON documents into one bundled HTML5 file.")

def _help_gen_minimal() -> None:
	print("Generate minimal Waterloo docstring skeletons.")

def _help_gen_full() -> None:
	print("Generate full Waterloo docstring skeletons.")

def _help_list_schemas() -> None:
	print("List available Waterloo JSON Schema files.")

def _help_version() -> None:
	print(f"Print waterlint version string only, e.g. {__version__}.")

def _help_version_json() -> None:
	print("Print JSON with waterlint and Waterloo JSON Schema versions.")

def _help_topic_command(args: argparse.Namespace) -> int:
	global parser
	assert parser._subparsers is not None
	for action in parser._subparsers._actions:
		if isinstance(action, argparse._SubParsersAction):
			for cmd, subp in action.choices.items():
				if cmd == args.topic:
					print(f"\nSubcommand '{cmd}':")
					subp.print_help()
#----- Add subcommands here -----------------------------------#
					if cmd == "validate":
						_help_validate()
					if cmd == "coverage":
						_help_coverage()
					if cmd == "extract":
						_help_extract()
					if cmd == "validate-json":
						_help_validate_json()
					if cmd == "add-example-json":
						_help_add_example_json()
					if cmd == "gen-example-template-json":
						_help_gen_example_template_json()
					if cmd == "render-json":
						_help_render_json()
					if cmd == "render-html5":
						_help_render_html5()
					if cmd == "gen-minimal":
						_help_gen_minimal()
					if cmd == "gen-full":
						_help_gen_full()
					if cmd == "list-schemas":
						_help_list_schemas()
					if cmd == "version":
						_help_version()
					if cmd == "version-json":
						_help_version_json()
					exit(0)
			allowed = "'" + "', '".join(SUBCOMMANDS) + "'"
			print(f"Command '{args.topic}' not found. Try one of {allowed}.",file=sys.stderr)
	return 0

#===== List schemas ==========================================#

def _list_schemas_command(args: argparse.Namespace) -> int:
	"""List available Waterloo JSON Schemas."""
	schema_dirs: list[Path] = []
	# 1) schema directory next to this script
	schema_dirs.append(Path(__file__).resolve().parent / "schema")
	# 2) installed package resource directory
	try:
		pkg_schema = importlib_resources.files("sdv.doc.waterloo") / "schema"
		schema_dirs.append(Path(str(pkg_schema)))
	except Exception:
		pass

	seen: set[Path] = set()
	for sdir in schema_dirs:
		sdir = sdir.resolve()
		if sdir in seen:
			continue
		seen.add(sdir)
		print(f"Schemas in {sdir}:")
		if not sdir.exists():
			print("  (directory not found)")
			continue
		files = sorted(p.name for p in sdir.glob("wtrl*.json") if p.is_file())
		if not files:
			print("  (none matching wtrl*.json)")
		else:
			for fname in files:
				print(f"  {fname}")
	return 0

def _version_command(args: argparse.Namespace) -> int:
	"""Print only the waterlint version string."""
	print(__version__)
	return 0

def _version_json_command(args: argparse.Namespace) -> int:
	"""Print JSON with waterlint and Waterloo JSON Schema versions."""
	doc = {
		"waterlint": __version__,
		"wtrl-json": WTRL_JSON_SCHEMA_VERSION,
		"wtrl-tracer-json": docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		"wtrl-example-refs-json": WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION,
		"wtrl-walk-json": WTRL_WALK_JSON_SCHEMA_VERSION,
	}
	json.dump(doc, sys.stdout, indent=2)
	sys.stdout.write("\n")
	return 0

parser: argparse.ArgumentParser

#===== Build parser ===========================================#

class CustomHelpFormatter(argparse.HelpFormatter):
	def __init__(self, prog):
		super().__init__(prog)
		self._max_help_position = 36
		self._indent_increment = 4
		terminal_width = shutil.get_terminal_size().columns
		self._width = min(100, terminal_width)

def _build_parser() -> argparse.ArgumentParser:
#----- Main parser --------------------------------------------#
	global parser
	parser = argparse.ArgumentParser(
		prog="waterlint",
		formatter_class=CustomHelpFormatter)
	subparsers = parser.add_subparsers(dest="command", required=True)
	parser.add_argument(
		"--help-all",
		action="store_true",
		help="Show help including subcommand details.",
		)

#----- Reusable parsers ---------------------------------------#
	global_opts = argparse.ArgumentParser(
		add_help=False,
		formatter_class=CustomHelpFormatter)
	global_opts.add_argument(
		"--fail-on-warning",
		action="store_true",
		help="Treat warnings as errors (affects exit code).",
	)
	global_opts.add_argument(
		"--out-diag",
		metavar="PATH",
		help="Write tracer diagnostics (errors/warnings) to PATH instead of stderr.",
	)
	global_opts.add_argument(
		"--out-diag-json",
		metavar="PATH",
		help="Write tracer diagnostics in machine-readable JSON format to PATH.",
	)

	common_validate_group = argparse.ArgumentParser(
		add_help=False,
		formatter_class=CustomHelpFormatter)
	common_validate_group.add_argument(
		"--basedir",
		metavar="DIR",
		help="Base directory for resolving objects passed to --obj.",
	)

#----- help-topic ---------------------------------------------#
	help_topic = subparsers.add_parser(
		"help",
		help="Help on specific topic, e.g. help --topic validate",
		formatter_class=parser.formatter_class)
	help_topic.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	help_topic.add_argument("--topic", dest="topic", metavar="TOPIC")

#----- validate -----------------------------------------------#
	validate = subparsers.add_parser(
		"validate",
		help="Validate docstrings",
		parents=[common_validate_group, global_opts],
		formatter_class=parser.formatter_class)
	vg = validate.add_mutually_exclusive_group()
	vg.add_argument("--obj", metavar="QUALNAME", help="Qualified identifier of module/class/function/method")
	vg.add_argument("--in", dest="input_file", metavar="FILE", help="Read docstring text from file")
	validate.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	validate.add_argument(
		"--ignore",
		metavar="RULES",
		help="Whitespace-separated list of Rule-IDs to ignore for warnings.",
	)

#----- coverage -----------------------------------------------#
	coverage = subparsers.add_parser(
		"coverage",
		help="Validate docstring coverage",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	coverage.add_argument(
		"--basedir",
		metavar="DIR",
		help="Base directory for resolving objects passed to --obj.",
	)
	coverage.add_argument("--obj", required=True, metavar="QUALNAME", help="Qualified identifier of module/class")
	coverage.add_argument(
		"--ignore",
		metavar="RULES",
		help="Whitespace-separated list of Rule-IDs to ignore for warnings.",
	)
	coverage.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- extract ------------------------------------------------#
	extract = subparsers.add_parser(
		"extract",
		help="Extract docstring sections",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	eg = extract.add_mutually_exclusive_group()
	eg.add_argument("--obj", metavar="QUALNAME", help="Qualified identifier of module/class/function/method")
	eg.add_argument("--in", dest="input_file", metavar="FILE", help="Read docstring text from file")
	extract.add_argument(
		"--basedir",
		metavar="DIR",
		help="Base directory for resolving objects passed to --obj.",
	)
	extract.add_argument("--out", dest="out_file", metavar="FILE", help="Write extracted text to FILE instead of stdout.")
	extract.add_argument("--section", metavar="SECTION", help="Section label to extract")
	extract.add_argument("--subsection", metavar="SUBSECTION", help="Subsection label to extract (requires --section)")
	extract.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- validate-json ------------------------------------------#
	validate_json = subparsers.add_parser(
		"validate-json",
		help="Validate Waterloo JSON output",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	validate_json.add_argument("--in", dest="input_file", metavar="FILE", help="Read JSON from file (default: stdin)")
	validate_json.add_argument(
		"--schema",
		required=False,
		metavar="FILE",
		help="Path to JSON Schema file. If omitted, waterlint infers category from __WTRL_*__ keys and version from __WTRL_VERSION__.schema.",
	)
	validate_json.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- add-example-json ---------------------------------------#
	add_example_json = subparsers.add_parser(
		"add-example-json",
		help="Add example code mapping to Waterloo JSON",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	add_example_json.add_argument("--in", dest="input_file", required=True, metavar="FILE", help="Input Waterloo JSON file.")
	add_example_json.add_argument("--examples", dest="examples_file", required=True, metavar="FILE", help="Mapping JSON with __WTRL_EXAMPLE_REFS__ (QID -> list of example files).")
	add_example_json.add_argument("--basedir", metavar="DIR", help="Base directory for resolving relative example file paths.")
	add_example_json.add_argument("--allow-local-paths", dest="allow_local_paths", action="store_true", default=False, help="Include local example path in __WTRL_EXAMPLES__.path.")
	add_example_json.add_argument("--no-allow-local-paths", dest="allow_local_paths", action="store_false", help="Do not include local path in __WTRL_EXAMPLES__.path (default).")
	aex_out = add_example_json.add_mutually_exclusive_group(required=True)
	aex_out.add_argument("--out", dest="out_file", metavar="FILE", help="Write updated JSON to FILE.")
	aex_out.add_argument("--out-dir", dest="out_dir", metavar="DIR", help="Write updated JSON to DIR using input filename.")
	add_example_json.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- gen-example-template-json ------------------------------#
	gen_example_template_json = subparsers.add_parser(
		"gen-example-template-json",
		help="Generate JSON template for __WTRL_EXAMPLE_REFS__ mappings",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	gen_example_template_json.add_argument(
		"--org-or-project",
		default="none",
		metavar="TEXT",
		help="Value for $id segment <org-or-project> (default: none).",
	)
	gen_example_template_json.add_argument(
		"--domain",
		default="local",
		metavar="TEXT",
		help="Value for $id segment <domain> (default: local).",
	)
	gen_example_template_json.add_argument(
		"--out",
		dest="out_file",
		metavar="FILE",
		help="Write template JSON to FILE instead of stdout.",
	)
	gen_example_template_json.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- render-json --------------------------------------------#
	render_json = subparsers.add_parser(
		"render-json",
		help="Render module to Waterloo JSON",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	render_json.add_argument(
		"--obj",
		required=True,
		nargs="+",
		action="append",
		metavar="MODULE",
		help="One or more qualified module names to render (merged). Option may be repeated.",
	)
	render_json.add_argument("--basedir", metavar="DIR", help="Base directory for resolving --obj.")
	rg_out = render_json.add_mutually_exclusive_group()
	rg_out.add_argument("--out", dest="out_file", metavar="FILE", help="Write JSON to FILE instead of stdout.")
	rg_out.add_argument("--out-dir", dest="out_dir", metavar="DIR", help="Write JSON into DIR using a generated filename.")
	render_json.add_argument("--out-prefix", dest="out_prefix", metavar="PREFIX", help="Filename prefix used with --out-dir, required when multiple --obj are given.")
	render_json.add_argument("--flavour", choices=["raw","rfc-2119","markdown"], default="rfc-2119", help="Normativity keyword flavour (default: rfc-2119).")
	render_json.add_argument(
		"--scope",
		choices=sorted(SCOPE_TAG_MAP.keys()),
		default="core",
		help="Render only objects visible in the given scope (default: core).",
	)
	render_json.add_argument("--include-imported", dest="include_imported", action="store_true", default=True, help="Include imported members and submodules (default).")
	render_json.add_argument("--no-include-imported", dest="include_imported", action="store_false", help="Do not include imported members/submodules.")
	render_json.add_argument("--allow-local-paths", dest="allow_local_paths", action="store_true", default=True, help="Include filesystem paths in JSON (default).")
	render_json.add_argument("--no-allow-local-paths", dest="allow_local_paths", action="store_false", help="Omit filesystem paths in JSON.")
	render_json.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- render-html5 -------------------------------------------#
	render_html5 = subparsers.add_parser(
		"render-html5",
		help="Render Waterloo JSON to bundled HTML5",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	render_html5.add_argument(
		"--in",
		dest="input_files",
		required=True,
		nargs="+",
		action="append",
		metavar="JSON",
		help="One or more Waterloo JSON files. Option may be repeated.",
	)
	rh_out = render_html5.add_mutually_exclusive_group(required=True)
	rh_out.add_argument("--out", dest="out_file", metavar="HTML", help="Write HTML to HTML.")
	rh_out.add_argument("--out-dir", dest="out_dir", metavar="DIR", help="Write HTML to DIR with generated filename.")
	render_html5.add_argument("--css", dest="css_file", metavar="FILE", help="Primary CSS file to embed instead of the built-in default CSS.")
	render_html5.add_argument("--additional-css", dest="additional_css_file", metavar="FILE", help="Additional CSS file to append after the primary CSS.")
	render_html5.add_argument("--header-html", dest="header_html_file", metavar="FILE", help="HTML fragment file used instead of the built-in header markup.")
	render_html5.add_argument("--pygments-theme", dest="pygments_theme", default="gruvbox-light", metavar="THEME", help="Pygments style name for rendered examples (default: gruvbox-light).")
	render_html5.add_argument("--no-render-preamble", dest="no_render_preamble", action="store_true", help="Do not render section 'Preamble' in HTML output.")
	render_html5.add_argument("--allow-raw-object-node", dest="allow_raw_object_node", action="store_true", default=True, help="Include collapsible section 'Raw object node' in HTML output (default).")
	render_html5.add_argument("--no-allow-raw-object-node", dest="allow_raw_object_node", action="store_false", help="Do not include section 'Raw object node' in HTML output.")
	render_html5.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- walk ---------------------------------------------------#
	walk = subparsers.add_parser(
		"walk",
		help="Walk documentable objects and analyze traversal",
		parents=[global_opts, common_validate_group],
		formatter_class=parser.formatter_class)
	walk.add_argument(
		"--obj",
		required=True,
		metavar="QUALNAME",
		help="Qualified identifier of a module/class/function/method to traverse.",
	)
	walk_out = walk.add_mutually_exclusive_group()
	walk_out.add_argument("--out", dest="out_file", metavar="FILE", help="Write walk text output to FILE instead of stdout.")
	walk_out.add_argument("--out-json", dest="out_json", metavar="FILE", help="Write walk JSON output to FILE.")
	walk.add_argument(
		"--show",
		metavar="FIELDS",
		help="Comma-separated list of fields to show in the text output (default: qualname,kind,scope,file,lineno,included,reason).",
	)
	walk.add_argument(
		"--sort",
		"--order",
		dest="sort",
		metavar="FIELDS",
		help="Comma-separated list of fields to sort by. The last field is applied first; sort is always ascending. Numeric fields sort numerically with null before 0; string and bool fields sort case-insensitively with underscores ignored.",
	)
	walk.add_argument("--include-imported", dest="include_imported", action="store_true", default=True, help="Include imported members and submodules (default).")
	walk.add_argument("--no-include-imported", dest="include_imported", action="store_false", help="Do not include imported members/submodules.")
	walk.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- gen-minimal --------------------------------------------#
	gen_minimal = subparsers.add_parser(
		"gen-minimal",
		help="Generate minimal Waterloo docstring skeleton",
		parents=[global_opts, common_validate_group],
		formatter_class=parser.formatter_class)
	gen_minimal.add_argument(
		"--obj",
		required=True,
		nargs="+",
		action="append",
		metavar="QUALNAME",
		help="One or more qualified objects to generate docstring skeletons for. Option may be repeated.",
	)
	gen_minimal.add_argument("--recursive", action="store_true", help="Recursively traverse documentable objects below each --obj.")
	gen_minimal.add_argument("--missing-only", action="store_true", help="Generate only for objects without docstring.")
	gen_minimal.add_argument("--format", choices=["raw", "json"], default=None, help="Output format. Default: raw, or json if --recursive is set.")
	gen_minimal.add_argument("--out", dest="out_file", metavar="FILE", help="Write output to FILE instead of stdout.")
	gen_minimal.add_argument("--indent", choices=["tab", "spc4"], default="spc4", help="Indent unit for generated docstring text (default: spc4).")
	gen_minimal.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- gen-full -----------------------------------------------#
	gen_full = subparsers.add_parser(
		"gen-full",
		help="Generate full Waterloo docstring skeleton",
		parents=[global_opts, common_validate_group],
		formatter_class=parser.formatter_class)
	gen_full.add_argument(
		"--obj",
		required=True,
		nargs="+",
		action="append",
		metavar="QUALNAME",
		help="One or more qualified objects to generate docstring skeletons for. Option may be repeated.",
	)
	gen_full.add_argument("--recursive", action="store_true", help="Recursively traverse documentable objects below each --obj.")
	gen_full.add_argument("--missing-only", action="store_true", help="Generate only for objects without docstring.")
	gen_full.add_argument("--format", choices=["raw", "json"], default=None, help="Output format. Default: raw, or json if --recursive is set.")
	gen_full.add_argument("--out", dest="out_file", metavar="FILE", help="Write output to FILE instead of stdout.")
	gen_full.add_argument("--indent", choices=["tab", "spc4"], default="spc4", help="Indent unit for generated docstring text (default: spc4).")
	gen_full.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- list-schemas -------------------------------------------#
	list_schemas = subparsers.add_parser(
		"list-schemas",
		help="List available Waterloo JSON Schemas",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	list_schemas.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- version ------------------------------------------------#
	version = subparsers.add_parser(
		"version",
		help="Print waterlint version string",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	version.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- version-json -------------------------------------------#
	version = subparsers.add_parser(
		"version-json",
		help="Print JSON with Waterloo schema versions",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	version.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

	return parser


def main(argv: Optional[list[str]] = None) -> int:
	parser = _build_parser()
	if argv is None:
		argv = sys.argv[1:]
	if "--help-all" in argv:
		parser.print_help()
		assert parser._subparsers is not None
		for action in parser._subparsers._actions:
			if isinstance(action, argparse._SubParsersAction):
				for cmd, subp in action.choices.items():
					print(f"\nSubcommand '{cmd}':")
					subp.print_help()
		return 0

	args = parser.parse_args(argv)
	global _debug
	_debug = args.debug

#----- Add subcommands here -----------------------------------#
	if args.command == "validate":
		return _validate_command(args)
	if args.command == "coverage":
		return _coverage_command(args)
	if args.command == "extract":
		return _extract_command(args)
	if args.command == "validate-json":
		return _validate_json_command(args)
	if args.command == "add-example-json":
		return _add_example_json_command(args)
	if args.command == "gen-example-template-json":
		return _gen_example_template_json_command(args)
	if args.command == "render-json":
		return _render_json_command(args)
	if args.command == "render-html5":
		return _render_html5_command(args)
	if args.command == "walk":
		return _walk_command(args)
	if args.command == "gen-minimal":
		return _generate_command(args, "minimal")
	if args.command == "gen-full":
		return _generate_command(args, "full")
	if args.command == "list-schemas":
		return _list_schemas_command(args)
	if args.command == "version":
		return _version_command(args)
	if args.command == "version-json":
		return _version_json_command(args)
	if args.command == "help":
		return _help_topic_command(args)
	return 1

if __name__ == "__main__":
	sys.exit(main())
