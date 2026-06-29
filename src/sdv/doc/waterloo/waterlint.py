#!/usr/bin/env python3
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
		|Must| be the main entry point for the waterlint command-line tool.
		|Must| dispatch to subcommands implemented in other modules.
		|Must| provide shared helper functions for subcommands, if needed.
Public_functions:
	add_example_json_command,
	validate_command,
	coverage_command,
	extract_command,
	validate_json_command,
	render_json_command,
	version_command,
	version_json_command
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import io
import importlib.util
import importlib.resources as importlib_resources
import typing
import sys, inspect, os, re,shutil, traceback
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, cast
from sdv.doc.waterloo.waterlint_common import (
	WTRL_DOCITEM_VERSION,
	WTRL_JSON_SCHEMA_VERSION,
	WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION,
	WTRL_WALK_JSON_SCHEMA_VERSION,
	WTRL_SCHEMA_URI_BASE,
	_apply_basedir,
	_resolve_object,
	add_traceback
	)
import sdv.doc.waterloo.mcp
from python_waterloo_lexer import __version__ as WTRL_PYTHON_WATERLOO_LEXER_VERSION


import json

from jsonpointer import JsonPointerException, resolve_pointer
from jsonschema import Draft202012Validator
#from jsonschema import JSONDecodeError
import jsonschema.exceptions

try:
	from pygments import format as pygments_format
	from pygments.formatters import Terminal256Formatter
	from pygments.styles import get_all_styles
	from python_waterloo_lexer import PythonWaterlooLexer
	_HAS_PYGMENTS = True
except Exception:
	_HAS_PYGMENTS = False

__version__ = "0.19.3"
# - 0.19.3 [2026-06-29]	Bugfix: CPVAR-005 and MPVAR-005 now allow annotated but uninstantiated variables, e.g. `x: int` without `x = 0`.
# - 0.19.2 [2026-06-28] Refactoring for detailed parsing and validation messages complete
# - 0.19.1 [2026-06-26] Add docstrings for version-commands; added wtrl_mcp-Version to version-json output.
# - 0.19.0 [2026-06-25] Subcommand 'extract' now with syntaax highlighting in terminal output; option --syntax-hl-style to select a Pygments style.
# - 0.18.0 [2026-06-25] Subcommand 'render-json': Validation and propagation of errors as standardized warning;
#			Option --ignore (as in validate and coverage) to ignore certain warning codes.
# - 0.17.0 [2026-06-22] Enhanced JSON output for types, constants, variables;
#			Improved html5-rendering for these categories.
# - 0.16.3 [2026-06-18] Bugfix which caused a missing error message in case of non-existing path for --basedir.
# - 0.16.2 [2026-06-15]	More details in error message (complete);bugfixes in validation.
# - 0.16.1 [2026-06-11]	More details in error message (in progress)
# - 0.16.0 [2026-06-10]	More details in error message (in progress)
# - 0.15.0 [2026-06-05]	Subcommand 'render-docker'
# - 0.14.1 [2026-05-26]	Subcommand 'render-html5': Entries in Public_* and *_overview sections are now links.
# - 0.14.0 [2026-05-25]	Subcommand `carve` now final, including exhaustive pytests.
# - 0.13.3 [2026-05-24]	Subcommands `gen-full` and `gen-minimal` moved to waterlint_generate_common.py, waterlint_gen_minimal.py and waterlint_gen_full.py.
#			Documentation in waterlint_gen_full.py and waterlint_gen_minimal.py
#			Updated waterlint_render_html5.py.
# - 0.13.2 [2026-05-23]	Subcommand `walk` moved to waterlint_walk.py; more functions in waterlint_common.py
# - 0.13.1 [2026-05-22]	Moved common functions from waterlint.py and waterlint_carve.py to waterlint_common.py;
#			bugfix in docitem.py.
#			documentation in waterlint_carve.py and waterlint_render_html5.py
# - 0.13.0 [2026-05-21]	Subcommand 'carve': Options --in, --out, --out-diag, --out-diag-json, --simplify,.--recompute
# - 0.12.0 [2026-05-20]	Subcommand 'render-json': Option --in.
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
	import sdv.doc.waterloo.waterlint_carve as carve
	import sdv.doc.waterloo.waterlint_common as wl_common
	import sdv.doc.waterloo.waterlint_gen_full as gfull
	import sdv.doc.waterloo.waterlint_gen_minimal as gmin
	import sdv.doc.waterloo.waterlint_gen_example_template_json as gext
	import sdv.doc.waterloo.waterlint_render_docker as rdocker
	import sdv.doc.waterloo.waterlint_render_html5 as rhtml5
	import sdv.doc.waterloo.waterlint_explain_section as exsec
	import sdv.doc.waterloo.waterlint_explain_subsection as exsub
	import sdv.doc.waterloo.waterlint_walk as wlk
	import sdv.doc.waterloo.docitem_tokenizer as tokenizer
	from sdv.doc.waterloo.docitem_helper import (
		tracer,
		Documentable,
		get_obj_name,
		get_obj_fully_qualified_name,
		get_obj_path,
		RE_ANSI_SGR_COMPILED,
		RE_WTRL_JSON_SCHEMA_NAME_COMPILED,
		ResolveObjectError,
		ValidationError,
		ParseError,
		SectionNotFoundError,
		SubsectionNotFoundError,
		SCOPE_TAG_MAP,
	)

#===== Constants ==============================================#

#----- Schema versions, keep up to date -----------------------#

#----- Add subcommands here -----------------------------------#
SUBCOMMANDS = (
	"validate",
	"coverage",
	"extract",
	"validate-json",
	"add-example-json",
	"gen-example-template-json",
	"render-json",
	"carve",
	"render-html5",
	"explain-section",
	"explain-subsection",
	"walk",
	"gen-minimal",
	"gen-full",
	"render-docker",
	"list-schemas",
	"version",
	"version-json",
)

#===== Helper =================================================#

def _emit_diagnostics(tr: tracer, dest: io.TextIOBase, strip_ansi: bool = False) -> None:
	wl_common.emit_diagnostics(tr, dest, debug=_debug, strip_ansi=strip_ansi)

def _build_tracer_json_doc(tr: tracer) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=WTRL_DOCITEM_VERSION,
		id_prefix=f"urn:waterlint:wtrl-tracer-json:{__version__}",
		include_debug=_debug,
	)

def _tokens_to_json_pointer(tokens: list[object]) -> str:
	return wl_common.tokens_to_json_pointer(tokens)


def _final_exit_code(base_code: int, tr: tracer, fail_on_warning: bool) -> int:
	code = base_code
	if tr.has_errors():
		code = 1
	if code == 0 and fail_on_warning and tr.has_warnings():
		code = 1
	return code


def _emit_tracer(tr: tracer, out_path: str | None, out_json_path: str | None = None) -> None:
	wl_common.emit_tracer(
		tr,
		out_path,
		out_json_path,
		debug=_debug,
		callback_build_json_doc=_build_tracer_json_doc,
	)

def _load_json(path: str | None) -> cvrt.WtrlJsonNode_t:
	return wl_common.load_json(path)


def _load_walk_input(tr: tracer, path: str) -> dict[str, Any] | None:
	"""Load and validate a walk JSON file for render-json --in."""
	doc = _load_json(path)
	if not isinstance(doc, dict):
		tr.add_error("JSCH-700", "tool", f"Walk input must be a JSON object: {path}")
		return None
	schema_path = Path(__file__).resolve().parent / "schema" / f"wtrl-walk-json-{WTRL_WALK_JSON_SCHEMA_VERSION}.schema.json"
	_validate_json_against_schema(tr, doc, str(schema_path))
	if tr.has_errors():
		return None
	return doc


def _render_json_doc_lines(lines: list[str], flavour: cvrt.Flavour) -> list[str]:
	"""Render logical docstring lines for JSON output in the requested flavour."""
	return [cvrt._render_token(line, flavour) for line in lines]


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
	wl_common.validate_json_against_schema(tr, doc, schema_path, "JSCH-005", "JSCH-800")


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

def add_example_json_command(args: argparse.Namespace) -> int:
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
			|Must| add example references to a Waterloo JSON document and write the updated JSON output.
	Parameters:
		args:
			Parsed add-example-json command line options.
			|must| provide the attributes expected by this command:
			* |attr|`input_file` |must| name the Waterloo JSON input file.
			* |attr|`examples_file` |must| name the JSON file containing `__WTRL_EXAMPLE_REFS__`.
			* Exactly one of |attr|`out_file` or |attr|`out_dir` |must| be present and designate the output target.
			* |attr|`basedir` |may| be present to resolve relative example file paths.
			* |attr|`allow_local_paths` |may| be present to keep local source paths in the generated example records.
			* |attr|`out_diag`, |attr|`out_diag_json`, and |attr|`debug` |may| be present as global diagnostics controls.
			* |attr|`fail_on_warning` |must| be present because the exit code depends on it.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
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
			add_traceback(tr)
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


def _is_valid_pygments_style(style_name: str) -> bool:
	return style_name in set(get_all_styles())

def _render_terminal_highlighted_text(text: str, style_name: str | None, force_ansi: bool, enabled: bool) -> str:
	if not enabled:
		return text
	if not _HAS_PYGMENTS:
		return text
	if not force_ansi and not sys.stdout.isatty():
		return text
	try:
		lexer = PythonWaterlooLexer()
	except Exception:
		return text
	try:
		if style_name:
			formatter = Terminal256Formatter(style=style_name)
		else:
			formatter = Terminal256Formatter()
	except Exception:
		formatter = Terminal256Formatter()

	def token_stream() -> Iterable[tuple[object, str]]:
		for _, token_type, value in lexer.highlight_docstring(0, text):
			yield token_type, value

	return cast(str,pygments_format(token_stream(), formatter))

#===== Validate ===============================================#

def validate_command(args: argparse.Namespace) -> int:
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
			|Must| validate a Waterloo docstring or a documented object against Waterloo rules.
	Parameters:
		args:
			Parsed validate command line options.
			|must| provide the attributes expected by this command:
			* Exactly one of |attr|`obj` or |attr|`input_file` |must| be present; if neither is present, stdin is used.
			* |attr|`basedir` |may| be present to resolve |opt|`--obj` relative to a base directory.
			* |attr|`ignore` |may| be present as a whitespace-separated list of ignored rule IDs.
			* |attr|`out_diag`, |attr|`out_diag_json`, and |attr|`debug` |may| be present as global diagnostics controls.
			* |attr|`fail_on_warning` |must| be present because the exit code depends on it.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	tr = tracer()
	session = docitem.DocSession()
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
				docitem.validate_docstring(tr, obj, None, session)
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
			add_traceback(tr)
			_emit_tracer(tr, out_diag)
			return 1
		else:
			raise
	except ResolveObjectError as e:
		tr.add_error("TOOL-001","tool",str(e), e.to_details())
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except ResolveObjectError as e:
		tr.add_error("TOOL-001","tool",str(e), e.to_details())
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
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
		tr.add_error("TOOL-001", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Coverage ===============================================#

def coverage_command(args: argparse.Namespace) -> int:
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
			|Must| validate docstring coverage for one module or class.
	Parameters:
		args:
			Parsed coverage command line options.
			|must| provide the attributes expected by this command:
			* |attr|`obj` |must| be present and resolve to a module or class.
			* |attr|`basedir` |may| be present to resolve |opt|`--obj` relative to a base directory.
			* |attr|`ignore` |may| be present as a whitespace-separated list of ignored rule IDs.
			* |attr|`out_diag`, |attr|`out_diag_json`, and |attr|`debug` |may| be present as global diagnostics controls.
			* |attr|`fail_on_warning` |must| be present because the exit code depends on it.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	tr = tracer()
	session = docitem.DocSession()
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
			add_traceback(tr)
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
		tr.add_error("TOOL-001", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
#		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, out_diag, out_diag_json)
		raise

	_emit_tracer(tr, out_diag, out_diag_json)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Extract ================================================#

def extract_command(args: argparse.Namespace) -> int:
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
				|Must| extract a Waterloo docstring or a docstring subsection.
	Parameters:
		args:
			Parsed extract command line options.
			|must| provide the attributes expected by this command:
			* Exactly one of |attr|`obj`, |attr|`input_file`, or stdin input is used; if |attr|`obj` is present it |must| resolve to a documented object.
			* |attr|`basedir` |may| be present to resolve |opt|`--obj` relative to a base directory.
			* |attr|`section` and |attr|`subsection` |may| be present to extract only part of the docstring, and |attr|`subsection` |must| only be used together with |attr|`section`.
			* |attr|`out_file` |may| be present to write the extracted text to a file instead of stdout.
			* |attr|`syntax_hl`, |attr|`syntax_hl_style`, and |attr|`force_color` |may| be present to control Waterloo-aware terminal highlighting.
			* |attr|`out_diag`, |attr|`out_diag_json`, and |attr|`debug` |may| be present as global diagnostics controls.
			* |attr|`fail_on_warning` |must| be present because the exit code depends on it.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	tr = tracer()
	session = docitem.DocSession()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
	syntax_hl = bool(getattr(args, "syntax_hl", False))
	syntax_hl_style = getattr(args, "syntax_hl_style", None)
	force_color = bool(getattr(args, "force_color", False))
	if syntax_hl and syntax_hl_style and not _is_valid_pygments_style(syntax_hl_style):
		tr.add_error("TOOL-001", "tool", f"Unknown Pygments style: {syntax_hl_style!r}.")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1
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

		tree = tokenizer.parse_indent_docstring(tr, doc_txt, session)
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
		out = _render_terminal_highlighted_text(out, syntax_hl_style, force_color, syntax_hl)

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
	except ResolveObjectError as exc:
		tr.add_error("TOOL-001", "tool", str(exc), exc.to_details())
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

def validate_json_command(args: argparse.Namespace) -> int:
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
			|Must| validate a Waterloo JSON document against the inferred or explicit schema.
	Parameters:
		args:
			Parsed validate-json command line options.
			|must| provide the attributes expected by this command:
			* |attr|`input_file` |may| be present to read JSON from a file; if absent, stdin is used.
			* |attr|`schema` |may| be present to force a specific JSON Schema file.
			* |attr|`out_diag`, |attr|`out_diag_json`, and |attr|`debug` |may| be present as global diagnostics controls.
			* |attr|`fail_on_warning` |must| be present because the exit code depends on it.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	tr = tracer()
	session = docitem.DocSession()
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

def render_json_command(args: argparse.Namespace) -> int:
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
			|Must| render Waterloo JSON from source objects or replay a walk JSON document.
	Parameters:
		args:
			Parsed render-json command line options.
			|must| provide the attributes expected by this command:
			* Exactly one of |attr|`in_file` or direct |attr|`obj` mode |must| be used; when direct mode is used, |attr|`obj` may be repeated and grouped.
			* |attr|`basedir` |may| be present to resolve direct-mode objects relative to a base directory.
			* Exactly one of |attr|`out_file` or |attr|`out_dir` |must| be present.
			* If |attr|`out_dir` is used with multiple root objects, |attr|`out_prefix` |must| be present.
			* |attr|`flavour`, |attr|`scope`, |attr|`include_imported`, and |attr|`allow_local_paths` |may| be present as rendering controls.
			* |attr|`ignore` |may| be present as a whitespace-separated list of ignored warning rule IDs.
			* |attr|`out_diag`, |attr|`out_diag_json`, and |attr|`debug` |may| be present as global diagnostics controls.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
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

	def _format_annotation_text(ann: object) -> str:
		"""Render an annotation object as a compact, user-facing string."""
		if ann is None or ann is inspect.Signature.empty or ann is inspect.Parameter.empty:
			return ""
		text = ann if isinstance(ann, str) else (ann.__name__ if isinstance(ann, type) else str(ann))
		text = str(text).replace("typing_extensions.", "").replace("typing.", "")
		if text == "None":
			return ""
		return text

	def _member_annotation_text(obj: object, mem_name: str, ann: object) -> str:
		"""Render a member annotation, expanding plain type aliases to their value."""
		if ann is typing.TypeAlias or ann == "TypeAlias" or ann == "typing.TypeAlias":
			try:
				return _format_annotation_text(getattr(obj, mem_name))
			except Exception:
				return ""
		return _format_annotation_text(ann)

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

	def _warn_invalid_render_json_object(name_key: str, o: object, phase: str) -> None:
		if tr.should_ignore_rule("TOOL-009"):
			return
		kind = "unknown"
		if cvrt.is_obj_module(o):
			kind = "module"
		elif cvrt.is_obj_class(o):
			kind = "class"
		elif cvrt.is_obj_function(o):
			kind = "callable"
		phase_text = "parse" if phase == "parse" else "validation" if phase == "validation" else phase
		tr.add_warning(
			"TOOL-009",
			"tool",
			f"render-json skipped invalid object '{name_key}' during {phase_text}.",
			{"object": name_key, "kind": kind, "phase": phase},
		)

	tr = tracer()
	session = docitem.DocSession()
#----- output spec --------------------------------------------#
	out_diag	=  getattr(args, "out_diag", None)
	out_diag_json	=  getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#

#----- Security note: local paths -----------------------------#
	if getattr(args, "allow_local_paths", True):
		tr.add_info("Result JSON contains local filesystem paths; disable with --no-allow-local-paths.")
	if getattr(args, "ignore", None):
		if "," in args.ignore:
			print('Commas are not allowed in --ignore; expect a single rule or a space-separated list of rules, e.g "VLII-001 SEE-006"')
			return 2
		for rule in args.ignore.split():
			try:
				tr.add_ignore_rule(rule)
			except RuntimeError as exc:
				print(f"Error: {exc}", file=sys.stderr)
				return 2
	try:
		flavour_str = args.flavour
		flavour = cvrt.flavour_tag_map.get(flavour_str)
		if flavour is None:
			flavour = cvrt.Flavour.RFC_2119
		input_walk_doc: dict[str, Any] | None = None
		obj_qnames: list[str] = []
		include_imported = bool(getattr(args, "include_imported", True))
		walk_basedir: str | None = None
		walk_included_qnames: set[str] = set()
		if getattr(args, "in_file", None):
			if getattr(args, "basedir", None) or getattr(args, "obj", None):
				print("Error: --in is mutually exclusive with direct --basedir/--obj mode.", file=sys.stderr)
				return 2
			input_walk_doc = _load_walk_input(tr, str(getattr(args, "in_file")))
			if input_walk_doc is None:
				_emit_tracer(tr, out_diag, out_diag_json)
				return 1
			meta = input_walk_doc.get("__WTRL_META__", {})
			if not isinstance(meta, dict):
				print("Error: walk input __WTRL_META__ must be an object.", file=sys.stderr)
				return 2
			walk_basedir_val = meta.get("basedir")
			if isinstance(walk_basedir_val, str) and walk_basedir_val.strip():
				walk_basedir = walk_basedir_val.strip()
			entries_raw = input_walk_doc.get("__WTRL_OBJECTS__", [])
			if isinstance(entries_raw, list):
				for entry in entries_raw:
					if not isinstance(entry, dict):
						continue
					qname = entry.get("qualname")
					if isinstance(qname, str) and qname.strip() and bool(entry.get("included", False)):
						walk_included_qnames.add(qname.strip())
			# Prefer the new plural root list, but keep the singular field as a fallback.
			objs_raw = meta.get("objs", meta.get("obj", []))
			if isinstance(objs_raw, list):
				for item in objs_raw:
					if isinstance(item, str) and item.strip():
						obj_qnames.append(item.strip())
			elif isinstance(objs_raw, str) and objs_raw.strip():
				obj_qnames.append(objs_raw.strip())
			if not obj_qnames:
				print("Error: walk input does not contain any root objects.", file=sys.stderr)
				return 2
			if "include_imported" in meta:
				include_imported = bool(meta.get("include_imported"))
		else:
# Build a flat list of object qualified names from the --obj arguments, which may be repeated and/or grouped.
# This is related to argparse's handling of nargs='+' with multiple occurrences, which results in a list of lists.
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
		modules: list[Documentable] = []
		for qname in obj_qnames:
			if getattr(args, "in_file", None):
				_apply_basedir(walk_basedir, qname)
			else:
				_apply_basedir(getattr(args, "basedir", None), qname)
			mod_obj = _resolve_object(qname)
			if not getattr(args, "in_file", None) and not isinstance(mod_obj, ModuleType):
				print(f"Error: --obj must resolve to modules for render-json (got {qname}).", file=sys.stderr)
				return 2
			modules.append(cast(Documentable, mod_obj))

#----- Object traversal and config ----------------------------#
		config = docitem.ConfigTraversal()
		if include_imported:
			config.enable_include_imported()
		config.disable_walk_packages()
#----- Filter by scope ----------------------------------------#
		objs: list[object] = []
		included_roots: set[str] = set()
		for mod in modules:
			for cand in docitem.gen_documentable_objects(mod, config):
				qname = get_obj_fully_qualified_name(cand)
				if input_walk_doc is not None:
					if qname not in walk_included_qnames:
						continue
					included_roots.add(qname)
				objs.append(cand)
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
		invalid_objects_reported: set[str] = set()
		modules_used: set[str] = set()
		modules_rendered: set[str] = set()
		public_members_rendered: set[str] = set()

#----- Iterate over scope-filtered objects --------------------#
		for o in objs:
			name_key = get_obj_fully_qualified_name(o)
			if input_walk_doc is not None and name_key not in walk_included_qnames:
				continue
			doc_txt = docitem.get_obj_docstring(o)
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
					tree_parsed = docitem.parse_indent_docstring(tr_obj, doc_txt, session)
					tree = docitem.make_docitem_tree_from_docstring_tree(tr_obj, tree_parsed)
# Validate structurally parseable docstrings before rendering them.
					docitem.validate_docstring(tr_obj, o, tree, session)
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
					if name_key not in invalid_objects_reported:
						invalid_objects_reported.add(name_key)
						_warn_invalid_render_json_object(name_key, o, "parse")
					continue
				except docitem.ValidationError:
# Invalid Waterloo docstring -> skip. Count safely.
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
					if name_key not in invalid_objects_reported:
						invalid_objects_reported.add(name_key)
						_warn_invalid_render_json_object(name_key, o, "validation")
					continue
# Filter by scope.
			if not cast(Any, tree).is_visible(scopes_filter):
				continue
# All entries are based on the qualified name, which is delivered by our helper.
			qname = name_key
# Collect nonaggregate public members for this object (module or class).
			obj_annotations = docitem.get_obj_annotations(o)
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
							mem_doc = _render_json_doc_lines(list(tree.item(sec_label).item(mem_name).items()), flavour)
						mem_entry = cast(dict[str, Any], tree_full["__WTRL_OBJECTS__"].setdefault(mem_qname, {"doc": {}}))
						mem_entry["doc"] = {}
						mem_entry["doc_lines"] = mem_doc
						ann = _member_annotation_text(o, mem_name, obj_annotations.get(mem_name))
						if ann:
							mem_entry["annotation"] = ann
						if sec_label == "Public_types":
							mem_entry["doc_lines_kind"] = "type"
						elif sec_label == "Public_variables":
							mem_entry["doc_lines_kind"] = "variable"
						elif sec_label == "Public_constants":
							mem_entry["doc_lines_kind"] = "constant"
#..... begin properties .......................................#
# We're still in the nonaggregate case! Properties fall in this category.
# Extract and check if it is a property, but tolerate annotated fields/variables
# that exist only in __annotations__ and therefore have no runtime attribute.
						if hasattr(o, mem_name):
							prop_obj = inspect.getattr_static(o, mem_name)
						else:
							prop_obj = None
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
									tree_prop_meth = docitem.parse_indent_docstring(tr_prop_meth_obj, doc_prop_meth, session)
									node_prop_meth = docitem.make_docitem_tree_from_docstring_tree(tr_prop_meth_obj, tree_prop_meth)
									docitem.validate_docstring(tr_prop_meth_obj, obj_prop_meth, node_prop_meth, session)
								except docitem.ParseError:
# Invalid docstring -> skip. Count safely.
									if qname_prop_meth not in objects_counted:
										num_callables_skipped_invalid += 1
										objects_counted.add(qname_prop_meth)
									continue
								except docitem.ValidationError:
# Invalid Waterloo docstring -> skip. Count safely.
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
				mod_annotations: dict[str, Any] = {}
				mod_obj = sys.modules.get(modname)
				if mod_obj is not None:
					mod_doc = docitem.get_obj_docstring(mod_obj)
					mod_annotations = docitem.get_obj_annotations(mod_obj)
# Scan python AST in order to get module docstring!
				if not mod_doc:
					mod_doc = _safe_module_docstring(modname)
				if mod_doc:
					if input_walk_doc is not None and modname not in walk_included_qnames:
						entry2["doc"] = {}
						tree_full["__WTRL_OBJECTS__"][modname] = entry2
						continue
					try:
						tr_tmp = tracer()
						mod_tree_parsed = docitem.parse_indent_docstring(tr_tmp, mod_doc, session)
						mod_tree = docitem.make_docitem_tree_from_docstring_tree(tr_tmp, mod_tree_parsed)
						# Render module docstring if it is included in walk; otherwise render stub.
						if input_walk_doc is None and cast(Any, mod_tree).is_visible(scopes_filter):
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
										mem_doc = _render_json_doc_lines(list(mod_tree.item(sec_label).item(mem_name).items()), flavour)
									mem_entry = cast(dict[str, Any], tree_full["__WTRL_OBJECTS__"].setdefault(mem_qname, {"doc": {}}))
									mem_entry["doc"] = {}
									mem_entry["doc_lines"] = mem_doc
									ann = _member_annotation_text(mod_obj, mem_name, mod_annotations.get(mem_name))
									if ann:
										mem_entry["annotation"] = ann
									if sec_label == "Public_types":
										mem_entry["doc_lines_kind"] = "type"
									elif sec_label == "Public_variables":
										mem_entry["doc_lines_kind"] = "variable"
									elif sec_label == "Public_constants":
										mem_entry["doc_lines_kind"] = "constant"
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

#===== Generate ===============================================#
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
	print("Render Waterloo JSON from source or replay walk JSON.")

def _help_carve() -> None:
	print("Edit walk JSON documents.")

def _help_render_html5() -> None:
	print("Render Waterloo JSON documents into one bundled HTML5 file.")

def _help_explain_section() -> None:
	print("Explain the structure of a Waterloo section label.")

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
					if cmd == "carve":
						_help_carve()
					if cmd == "render-html5":
						_help_render_html5()
					if cmd == "explain-section":
						_help_explain_section()
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

def _schema_version_key(fname: str) -> tuple[str, tuple[int, ...], str]:
	m = re.match(r"^(wtrl-[A-Za-z0-9_-]+)-([0-9]+(?:\.[0-9]+)*)\.schema\.json$", fname)
	if m is None:
		return (fname, (), fname)
	version = tuple(int(part) for part in m.group(2).split("."))
	return (m.group(1), version, fname)

def _iter_schema_dirs() -> List[Path]:
	schema_dirs: list[Path] = []
	# 1) schema directory next to this script
	schema_dirs.append(Path(__file__).resolve().parent / "schema")
	# 2) installed package resource directory
	try:
		pkg_schema = importlib_resources.files("sdv.doc.waterloo") / "schema"
		schema_dirs.append(Path(str(pkg_schema)))
	except Exception:
		pass
	return schema_dirs

def _schema_inventory() -> List[tuple[Path, list[str]]]:
	"""Return schema directories together with semantically sorted Waterloo JSON Schema filenames."""
	schema_infos: list[tuple[Path, list[str]]] = []
	seen: set[Path] = set()
	for sdir in _iter_schema_dirs():
		sdir = sdir.resolve()
		if sdir in seen:
			continue
		seen.add(sdir)
		if not sdir.exists():
			schema_infos.append((sdir, []))
			continue
		files = sorted((p.name for p in sdir.glob("wtrl*.json") if p.is_file()), key=_schema_version_key)
		schema_infos.append((sdir, files))
	return schema_infos

def _list_schemas_command(args: argparse.Namespace) -> int:
	"""List available Waterloo JSON Schemas."""
	for sdir, files in _schema_inventory():
		print(f"Schemas in {sdir}:")
		if not sdir.exists():
			print("  (directory not found)")
			continue
		if not files:
			print("  (none matching wtrl*.json)")
		else:
			for fname in files:
				print(f"  {fname}")
	return 0

def version_command(args: argparse.Namespace) -> int:
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
			|Must| print the waterlint version string to stdout.
			|Must_not| print any other text to stdout.
	Parameters:
		args:
			An |var|`argparse.Namespace` object containing the command-line arguments.
			Not used in this function.
	Returns:
		Exit code |value|`0`.
	Raises:
	"""
	print(__version__)
	return 0

def version_json_command(args: argparse.Namespace) -> int:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		g eneral:
			|Must| print a JSON document to stdout where each key represents\
			a versioned component of the Waterloo toolchain,\
			and each value is a dictionary containing the keys |value|`kind` and |value|`version`.
			|Must| infer the version of the Waterloo JSON Schema from the\
			file system in case the version is not hard-coded in this source file.
			|Must| classify each versioned component as either |value|`executable`, |value|`schema`, |value|`module`, or |value|`package`.
	Parameters:
		args:
			An |var|`argparse.Namespace` object containing the command-line arguments.
			Not used in this function.
	Returns:
		Exit code |value|`0`.
	Raises:
	Notes:
		Antidrift:
			Keep this function in sync with the Waterloo JSON Schema versioning and the\
			Waterloo toolchain versioning. Add a new key whenever a new component is added\
			to the versioned set.
	"""

	WTRL_MCP_ABOUT_JSON_SCHEMA_VERSION="TBD"
	WTRL_MCP_ABOUT_TOPIC_JSON_SCHEMA_VERSION="TBD"
	WTRL_EXPLAIN_SECTION_JSON_SCHEMA_VERSION="TBD"
	WTRL_EXPLAIN_SUBSECTION_JSON_SCHEMA_VERSION="TBD"
	WTRL_MCP_VERSION = sdv.doc.waterloo.mcp.__version__

	for _, files in _schema_inventory():
		for f in files:
			if f.startswith("wtrl-mcp-about-json-") and f.endswith(".schema.json"):
				WTRL_MCP_ABOUT_JSON_SCHEMA_VERSION = f[len("wtrl-mcp-about-json-"):-len(".schema.json")]
			elif f.startswith("wtrl-mcp-about-topic-json-") and f.endswith(".schema.json"):
				WTRL_MCP_ABOUT_TOPIC_JSON_SCHEMA_VERSION = f[len("wtrl-mcp-about-topic-json-"):-len(".schema.json")]
			elif f.startswith("wtrl-explain-section-json-") and f.endswith(".schema.json"):
				WTRL_EXPLAIN_SECTION_JSON_SCHEMA_VERSION = f[len("wtrl-explain-section-json-"):-len(".schema.json")]
			elif f.startswith("wtrl-explain-subsection-json-") and f.endswith(".schema.json"):
				WTRL_EXPLAIN_SUBSECTION_JSON_SCHEMA_VERSION = f[len("wtrl-explain-subsection-json-"):-len(".schema.json")]

	doc = {
		"waterlint": {"kind": "executable", "version": __version__},
		"wtrl-json": {"kind": "schema", "version": WTRL_JSON_SCHEMA_VERSION},
		"wtrl-tracer-json": {"kind": "schema", "version": docitem.WTRL_TRACER_JSON_SCHEMA_VERSION},
		"wtrl-example-refs-json": {"kind": "schema", "version": WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION},
		"wtrl-explain-section-json": {"kind": "schema", "version": WTRL_EXPLAIN_SECTION_JSON_SCHEMA_VERSION},
		"wtrl-explain-subsection-json": {"kind": "schema", "version": WTRL_EXPLAIN_SUBSECTION_JSON_SCHEMA_VERSION},
		"wtrl-walk-json": {"kind": "schema", "version": WTRL_WALK_JSON_SCHEMA_VERSION},
		"wtrl-mcp-about-json": {"kind": "schema", "version": WTRL_MCP_ABOUT_JSON_SCHEMA_VERSION},
		"wtrl-mcp-about-topic-json": {"kind": "schema", "version": WTRL_MCP_ABOUT_TOPIC_JSON_SCHEMA_VERSION},
		"wtrl_mcp": {"kind": "package", "version": WTRL_MCP_VERSION},
		"python-waterloo-lexer": {"kind": "package", "version": WTRL_PYTHON_WATERLOO_LEXER_VERSION},
	}
	json.dump(doc, sys.stdout, indent=2)
	sys.stdout.write("\n")
	return 0

parser: argparse.ArgumentParser

#===== Build parser ===========================================#

class CustomHelpFormatter(argparse.HelpFormatter):
	def __init__(self, prog : Any):
		super().__init__(prog)
		self._max_help_position = 36
		self._indent_increment = 4
		terminal_width = shutil.get_terminal_size().columns
		self._width = min(100, terminal_width)

	def _format_action(self, action: argparse.Action) -> str:
		# Keep the help text anchored at a fixed column instead of letting the
		# longest option name push the start position further to the right.
		help_position = self._max_help_position
		help_width = max(self._width - help_position, 11)
		action_width = help_position - self._current_indent - 2
		action_header = self._format_action_invocation(action)
		assert(hasattr(self,'_decolor'))
		action_header_no_color = self._decolor(action_header)

		if not action.help:
			tup1 = self._current_indent, '', action_header
			action_header = '%*s%s\n' % tup1
		elif len(action_header_no_color) <= action_width:
			action_header_color = action_header
			tup2 = self._current_indent, '', action_width, action_header_no_color
			action_header = '%*s%-*s  ' % tup2
			action_header = action_header.replace(
				action_header_no_color, action_header_color
			)
			indent_first = 0
		else:
			tup3 = self._current_indent, '', action_header
			action_header = '%*s%s\n' % tup3
			indent_first = help_position

		parts = [action_header]

		if action.help and action.help.strip():
			help_text = self._expand_help(action)
			if help_text:
				help_lines = self._split_lines(help_text, help_width)
				parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
				for line in help_lines[1:]:
					parts.append('%*s%s\n' % (help_position, '', line))
		elif not action_header.endswith('\n'):
			parts.append('\n')

		for subaction in self._iter_indented_subactions(action):
			parts.append(self._format_action(subaction))

		return self._join_parts(parts)

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
		help=f"Write tracer diagnostics (errors/warnings) to PATH, {wl_common.DIAG_TARGET_STDOUT}, or {wl_common.DIAG_TARGET_STDERR} instead of stderr.",
	)
	global_opts.add_argument(
		"--out-diag-json",
		metavar="PATH",
		help=f"Write tracer diagnostics in machine-readable JSON format to PATH, {wl_common.DIAG_TARGET_STDOUT}, or {wl_common.DIAG_TARGET_STDERR}.",
	)

	parser_parts: wl_common.ParserParts_t = {
		"formatter_class": CustomHelpFormatter,
		"global_opts": global_opts,
		"basedir_group": argparse.ArgumentParser(
			add_help=False,
			formatter_class=CustomHelpFormatter,
		),
	}
	# parser_parts bundles the reusable parser building blocks shared with plugins.
	# The current keys are stable for existing plugins; future keys may be added
	# without removing or renaming the present ones.
	parser_parts["basedir_group"].add_argument(
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
		parents=[parser_parts["basedir_group"], global_opts],
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
	extract.add_argument("--syntax-hl", dest="syntax_hl", action="store_true", help="Enable Waterloo-aware syntax highlighting in terminal output.")
	extract.add_argument("--no-syntax-hl", dest="syntax_hl", action="store_false", help="Disable Waterloo-aware syntax highlighting in terminal output.")
	extract.set_defaults(syntax_hl=False)
	extract.add_argument("--syntax-hl-style", metavar="STYLE", help="Pygments style for terminal highlighting; uses the formatter default if omitted. Call `pygmentize -L` for a list of available styles.")
	color_group = extract.add_mutually_exclusive_group()
	color_group.add_argument("--color", dest="force_color", action="store_true", help="Force ANSI color output even when stdout is not a terminal.")
	color_group.add_argument("--no-color", dest="force_color", action="store_false", help="Disable ANSI color output.")
	extract.set_defaults(force_color=False)
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

#----- render-json --------------------------------------------#
	render_json = subparsers.add_parser(
		"render-json",
		help="Render Waterloo JSON from source or replay walk JSON; often used with --ignore TOOL-009 for invalid objects.",
		parents=[global_opts],
		formatter_class=parser.formatter_class)
	render_json.add_argument(
		"--in",
		dest="in_file",
		metavar="FILE",
		help="Read exactly one walk JSON file as input. Validates the schema and uses included=true as filter SSoT. Mutually exclusive with direct --basedir/--obj mode.",
	)
	render_json.add_argument(
		"--obj",
		nargs="+",
		action="append",
		metavar="MODULE",
		help="One or more qualified module names to render in direct mode (merged). Option may be repeated.",
	)
	render_json.add_argument("--basedir", metavar="DIR", help="Base directory for resolving --obj in direct mode.")
	render_json.add_argument(
		"--ignore",
		metavar="RULES",
		help="Whitespace-separated list of Rule-IDs to ignore for warnings; TOOL-009 is commonly ignored when invalid objects are expected.",
	)
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

#----- carve --------------------------------------------------#
	carve.build_parser(subparsers, parser_parts)

#----- render-html5 -------------------------------------------#
	rhtml5.build_parser(subparsers, parser_parts)

#----- explain-section ---------------------------------------#
	exsec.build_parser(subparsers, parser_parts)

#----- explain-subsection ------------------------------------#
	exsub.build_parser(subparsers, parser_parts)

#----- render-docker ------------------------------------------#
	rdocker.build_parser(subparsers, parser_parts)

#----- walk ---------------------------------------------------#
	wlk.build_parser(subparsers, parser_parts)

#----- gen-minimal --------------------------------------------#
	gmin.build_parser(subparsers, parser_parts)

#----- gen-full -----------------------------------------------#
	gfull.build_parser(subparsers, parser_parts)

#----- gen-example-template-json ------------------------------#
	gext.build_parser(subparsers, parser_parts)

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
					label = f"Subcommand: {cmd}"
					print(f"\n" + "─" * 10 + " " + label + " " + "─" * (80 - 2 - len(label)) + "\n")
					subp.print_help()
		return 0

	args = parser.parse_args(argv)
	global _debug
	_debug = args.debug

#----- Add subcommands here -----------------------------------#
	if args.command == "validate":
		return validate_command(args)
	if args.command == "coverage":
		return coverage_command(args)
	if args.command == "extract":
		return extract_command(args)
	if args.command == "validate-json":
		return validate_json_command(args)
	if args.command == "add-example-json":
		return add_example_json_command(args)
	if args.command == "gen-example-template-json":
		return gext.gen_example_template_json_command(args, __version__)
	if args.command == "render-json":
		return render_json_command(args)
	if args.command == "carve":
		return int(carve.carve_command(args))
	if args.command == "render-html5":
		return rhtml5.render_html5(args)
	if args.command == "explain-section":
		return exsec.explain_section_command(args)
	if args.command == "explain-subsection":
		return exsub.explain_subsection_command(args)
	if args.command == "render-docker":
		return rdocker.render_docker(args)
	if args.command == "walk":
		return wlk.walk_command(args)
	if args.command == "gen-minimal":
		return gmin.gen_minimal_command(args, __version__)
	if args.command == "gen-full":
		return gfull.gen_full_command(args, __version__)
	if args.command == "list-schemas":
		return _list_schemas_command(args)
	if args.command == "version":
		return version_command(args)
	if args.command == "version-json":
		return version_json_command(args)
	if args.command == "help":
		return _help_topic_command(args)
	return 1

if __name__ == "__main__":
	sys.exit(main())
