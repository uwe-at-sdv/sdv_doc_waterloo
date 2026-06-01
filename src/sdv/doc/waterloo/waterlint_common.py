#!/usr/bin/env python3
r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions, Public_types
	scope:
		extension
Contract:
	general:
		|Must| provide common utilities for loading JSON, validating against schemas, and emitting diagnostics in both text and structured JSON form.
Public_classes:
	ParserParts_t
Public_functions:
	tokens_to_json_pointer, load_json, emit_diagnostics, validate_json_against_schema,
	recompute_walk_summary, build_tracer_json_doc, emit_tracer
Function_overview:
	tokens_to_json_pointer:
		Convert a list of tokens to a JSON Pointer string according to RFC 6901.
	load_json:
		Load JSON data from a file or standard input.
	emit_diagnostics:
		Emit diagnostics from a tracer to a text output stream, with options for including debug messages and stripping ANSI codes.
	validate_json_against_schema:
		Validate a JSON document against a JSON Schema and report issues into the tracer.
	recompute_walk_summary:
		Recompute summary statistics for a list of diagnostic entries.
	build_tracer_json_doc:
		Build a structured JSON document from the contents of a tracer.
	emit_tracer:
		Emit tracer diagnostics as text and/or JSON depending on the specified output arguments.
Public_types:
	WtrlJsonNode_t:
		Type alias for JSON data structures used in this module.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import traceback
import importlib.util
import importlib.resources as importlib_resources
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, cast, Dict, List, TypeAlias, TypedDict

import jsonschema.exceptions
from jsonschema import Draft202012Validator

import sdv.doc.waterloo.docitem as docitem

from sdv.doc.waterloo.docitem_helper import (
	RE_ANSI_SGR_COMPILED,
	get_obj_fully_qualified_name,
	tracer,
	)

#===== Type Checking ==========================================#
WtrlJsonNode_t: TypeAlias = Dict[str, "WtrlJsonNode_t"] | List["WtrlJsonNode_t"] | str | int | float | bool | None

class ParserParts_t(TypedDict):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
		status:
			stable
		scope:
			extension
	Contract:
		general:
			|Must| represent reusable argparse components for plugin command-line interfaces.
			|Must| keep the documented keys stable for existing plugins.
			Future keys may be added, but existing keys will not be removed or renamed.
		constructor:
			|Must| be instantiated with the following fields:
			- formatter_class: A class derived from argparse.HelpFormatter for consistent help message formatting.
			- global_opts: An argparse.ArgumentParser instance containing global options applicable to all subcommands.
			- basedir_group: An argparse.ArgumentParser instance or argument group for handling basedir-related options.
	Notes:
		General note:
			Plugins may consume only the parts they need. This class is a TypedDict
			that packages the reusable parser pieces passed from the main program to
			subcommands.
	"""
	formatter_class: type[argparse.HelpFormatter]
	global_opts: argparse.ArgumentParser
	basedir_group: argparse.ArgumentParser
#==============================================================#

#===== Constants ==============================================#
WTRL_DOCITEM_VERSION = docitem.__version__

#----- Schema versions, keep up to date -----------------------#
WTRL_JSON_SCHEMA_VERSION = "0.1.0"
WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION = "0.1.1"
WTRL_WALK_JSON_SCHEMA_VERSION = "0.0.1"

WTRL_SCHEMA_URI_BASE = "https://sci-d-vis.com/schema"
#==============================================================#

def add_traceback(tr: tracer) -> None:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
		status:
			stable
	Contract:
		general:
			|Must| capture the current exception traceback and add it to the tracer as info and error notes, if an exception is active.
	Parameters:
		tr:
			|Must| be a tracer instance where the traceback information will be added.
	Returns:
		|Must| return |None|.
	Raises:
	"""
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
	base_root = Path(base_abs)
# Not a dir? Error.
	if not base_root.is_dir():
		raise RuntimeError(f"basedir is not a directory: {basedir}")
# Update sys.path with basedir, so that we have a chance to find the module.
	if base_abs not in sys.path:
		sys.path.insert(0, base_abs)

# If a local file/module matches qname exactly, prefer it over any already
# imported foreign module with the same bare name.
	if "." not in qname:
		local_mod_file = base_root / f"{qname}.py"
		local_pkg_init = base_root / qname / "__init__.py"
		if local_mod_file.is_file() or local_pkg_init.is_file():
			existing = sys.modules.get(qname)
			if existing is not None:
				existing_file = getattr(existing, "__file__", None)
				existing_paths = getattr(existing, "__path__", None)
				is_local = False
				if isinstance(existing_file, str):
					try:
						is_local = Path(existing_file).resolve().is_relative_to(base_root)
					except Exception:
						is_local = False
				if not is_local and existing_paths is not None:
					for pth in existing_paths:
						try:
							if Path(str(pth)).resolve().is_relative_to(base_root):
								is_local = True
								break
						except Exception:
							continue
				if not is_local:
					del sys.modules[qname]

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

def tokens_to_json_pointer(tokens: list[object]) -> str:
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
			|Must| convert a list of tokens to a JSON Pointer string according to RFC 6901.
	Parameters:
		tokens:
			|Must| be a list of objects representing the path tokens.
	Returns:
		|Must| return a string representing the JSON Pointer.
	Raises:
		TypeError:
			|May| raise if any token is not convertible to a string.
	Notes:
		General note:
			* The JSON Pointer syntax requires that "~" is escaped as "~0" and "/" is escaped as "~1" in the tokens.
			* An empty list of tokens corresponds to the JSON Pointer "" which points to the whole document.
	"""
	if not tokens:
		return ""
	def _esc(seg: object) -> str:
		return str(seg).replace("~", "~0").replace("/", "~1")
	return "/" + "/".join(_esc(t) for t in tokens)


def load_json(path: str | None) -> WtrlJsonNode_t:
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
			|Must| load JSON data from the specified file path or from standard input if the path is |None|.
	Parameters:
		path:
			|Must| be a string representing the path to the JSON file. If |None|, JSON is read from standard input.
	Returns:
		|Must| return the loaded JSON object.
	Raises:
		json.JSONDecodeError:
			|May| raise if the input is not valid JSON.
		FileNotFoundError:
			|May| raise if the specified file does not exist.
	Notes:
		General note:
			If |var|`path` is |None|, the JSON is read from standard input.
	"""
	if path:
		with open(path, "r", encoding="utf-8") as fh:
			return cast(WtrlJsonNode_t, json.load(fh))
	return cast(WtrlJsonNode_t, json.load(sys.stdin))


def emit_diagnostics(tr: tracer, dest: io.TextIOBase, debug: bool = False, strip_ansi: bool = False) -> None:
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
			|Must| emit diagnostics from the tracer to the specified text output stream, optionally including debug messages and stripping ANSI escape codes.
			|Must| include debug messages if |var|`debug` is set to |True|, otherwise only info, warning, and error messages are included.
			|Must| strip ANSI escape codes from the output if |var|`strip_ansi` is set to |True|.
	Parameters:
		tr:
			A tracer instance containing the diagnostics to emit.
		dest:
			A text output stream where the diagnostics will be written.
		debug:
			Include debug messages in the output if |var|`debug` is set to |True|. By default, only info, warning, and error messages are included.
		strip_ansi:
			Flag indicating whether to strip ANSI escape codes from the output. If |var|`strip_ansi` is set to |True|, all ANSI escape codes will be removed from the emitted diagnostics. By default, ANSI codes are included in the output.
	Returns:
		|Must| return |None|.
	Raises:
		OSError:
			|May| raise if |var|`dest.write()` fails because the output stream is closed, broken, or otherwise unavailable.
		ValueError:
			|May| raise if |var|`dest` is in an invalid state for writing.
	"""
	severity = tr.Severity.DEBUG if debug else tr.Severity.INFO
	txt = tr.str_by_severity(severity)
	if strip_ansi:
		txt = RE_ANSI_SGR_COMPILED.sub("", txt)
	dest.write(txt)


def validate_json_against_schema(
	tr: tracer,
	doc: WtrlJsonNode_t,
	schema_path: str,
	rule_id_validation: str,
	rule_id_fallback: str,
) -> None:
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
			|Must| validate a JSON document against the JSON Schema loaded from the specified file path and report validation issues into the tracer.
	Parameters:
		tr:
			Tracer instance receiving any validation diagnostics.
		doc:
			JSON document to validate.
		schema_path:
			Path to the JSON Schema document that defines the expected structure.
		rule_id_validation:
			Rule identifier used for schema validation failures reported as JSON Schema validation errors.
		rule_id_fallback:
			Rule identifier used for fallback errors that are not classified as JSON Schema validation errors.
	Returns:
		|Must| return |None|.
	Raises:
		FileNotFoundError:
			|May| raise if the schema file cannot be opened.
		json.JSONDecodeError:
			|May| raise if the schema file is not valid JSON.
		jsonschema.exceptions.SchemaError:
			|May| raise if the loaded schema is not a valid JSON Schema document.
	"""
	schema = load_json(schema_path)
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
	for e in errors:
		path_tokens = list(e.path)
		schema_path_tokens = list(e.schema_path)
		if isinstance(e, jsonschema.exceptions.ValidationError):
			details = {
				"validator": e.validator,
				"path": path_tokens,
				"schema_path": schema_path_tokens,
				"path_pointer": tokens_to_json_pointer(path_tokens),
				"schema_path_pointer": tokens_to_json_pointer(schema_path_tokens),
			}
			tr.add_error(rule_id_validation, "tool", "[" + get_obj_fully_qualified_name(e) + "] " + e.message, details)
		else:
			tr.add_error(rule_id_fallback, "tool", "[" + get_obj_fully_qualified_name(e) + "] " + e.message, {})


def recompute_walk_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
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
			|Must| recompute summary statistics for a list of diagnostic entries, counting totals and categorizing by kind, scope, and reason.
	Parameters:
		entries:
			List of diagnostic entries to summarize.
	Returns:
		|Must| return a dictionary containing the summary statistics.
	Raises:
	"""
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
	return {
		"total": len(entries),
		"included": included_count,
		"excluded": len(entries) - included_count,
		"by_kind": count_by_kind,
		"by_scope": count_by_scope,
		"by_reason": count_by_reason,
	}


def build_tracer_json_doc(
	tr: tracer,
	*,
	schema_version: str,
	waterloo_version: str,
	id_prefix: str,
	include_debug: bool = False,
) -> dict[str, Any]:
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
			|Must| build a structured tracer JSON document from the current tracer contents.
	Parameters:
		tr:
			Tracer instance providing infos, warnings, errors, and optionally debug notes.
		schema_version:
			Version string of the tracer JSON schema.
		waterloo_version:
			Version string of the Waterloo implementation.
		id_prefix:
			Prefix used to build a unique document identifier.
		include_debug:
			|Must| include debug entries if |var|`True`.
	Returns:
		|Must| return a JSON-serializable dictionary representing the tracer document.
	Raises:
	Notes:
		General note:
			The resulting JSON document includes metadata such as schema version and Waterloo version,
			as well as arrays of diagnostic entries categorized by severity (info, warning, error)
			and optionally debug entries.
		"""
	doc: dict[str, Any] = {
		"$schema": f"{WTRL_SCHEMA_URI_BASE}/wtrl-tracer-json-{schema_version}.schema.json",
		"$id": f"{id_prefix}:{datetime.now().strftime('%Y%m%d%H%M%S')}",
		"__WTRL_VERSION__": {
			"waterloo": waterloo_version,
			"schema": schema_version,
		},
		"__WTRL_INFO__": [],
		"__WTRL_WARNING__": [],
		"__WTRL_ERROR__": [],
	}
	if include_debug:
		doc["__WTRL_DEBUG__"] = []
		for context, origin, msg in tr.gen_debug_notes():
			dentry: dict[str, Any] = {"kind": "debug", "origin": origin, "msg": msg}
			dentry["context"] = context
			cast(list[dict[str, Any]], doc["__WTRL_DEBUG__"]).append(dentry)
	for context, origin, msg in tr.gen_infos():
		entry: dict[str, Any] = {"kind": "info", "origin": origin, "msg": msg}
		entry["context"] = context
		cast(list[dict[str, Any]], doc["__WTRL_INFO__"]).append(entry)
	for context, rule_id, origin, msg, details in tr.gen_warnings():
		entry = {"kind": "warning", "origin": origin, "rule-id": rule_id, "msg": msg}
		entry["context"] = context
		entry["details"] = details
		cast(list[dict[str, Any]], doc["__WTRL_WARNING__"]).append(entry)
	for context, rule_id, origin, msg, details in tr.gen_errors():
		entry = {"kind": "error", "origin": origin, "rule-id": rule_id, "msg": msg}
		entry["context"] = context
		entry["details"] = details
		cast(list[dict[str, Any]], doc["__WTRL_ERROR__"]).append(entry)
	return doc


def emit_tracer(
	tr: tracer,
	out_path: str | None,
	out_json_path: str | None,
	*,
	debug: bool,
	callback_build_json_doc: Callable[[tracer], dict[str, Any]] | None,
) -> None:
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
			|Must| emit tracer diagnostics either as text, as JSON, or as both, depending on the output arguments.
			The JSON builder callback |must| be passed explicitly at the call site.
			Passing |None| is allowed and means that JSON output is disabled for this call.
	Parameters:
		tr:
			Tracer instance whose diagnostics are emitted.
		out_path:
			Optional path to a plain-text diagnostic output file.
		out_json_path:
			Optional path to a structured JSON diagnostic output file.
		debug:
			|Must| select debug-level diagnostics if |var|`True`, otherwise info-level diagnostics.
		callback_build_json_doc:
			Callable that builds the JSON diagnostic document from the tracer. May be |None| if no JSON output is requested.
	Returns:
		|Must| return |None|.
	Raises:
		RuntimeError:
			|May| raise if JSON output is requested but no JSON-builder callback was supplied.
		OSError:
			|May| raise if writing to one of the output streams fails.
		ValueError:
			|May| raise if one of the output streams is not in a writable state.
	"""
	if out_path:
		with open(out_path, "w", encoding="utf-8") as fh:
			emit_diagnostics(tr, fh, debug=debug, strip_ansi=True)
	else:
		severity = tr.Severity.DEBUG if debug else tr.Severity.INFO
		print(tr.str_by_severity(severity), file=sys.stderr, end="")
	if out_json_path:
		if callback_build_json_doc is None:
			raise RuntimeError("JSON tracer output requested but no JSON builder callback was provided.")
		doc = callback_build_json_doc(tr)
		with open(out_json_path, "w", encoding="utf-8") as fh:
			json.dump(doc, fh, indent=4)
			fh.write("\n")
