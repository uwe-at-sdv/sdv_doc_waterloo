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
		|Must| provide the walk command for previewing object traversal and JSON output.
Public_functions:
	walk_command, build_parser
Function_overview:
	walk_command:
		Execute the walk command by traversing documentable objects, collecting walk entries,
		and emitting either text or JSON output.
	build_parser:
		Construct and return the argparse subparser for the walk command.
"""

from __future__ import annotations

import argparse
import sys, os, inspect, json, re
import importlib.resources as importlib_resources

from datetime import datetime
from pathlib import Path
from typing import Any, cast, Dict, List, Literal, Protocol, Tuple, TypeAlias
from sdv.doc.waterloo.waterlint_common import (
	WTRL_DOCITEM_VERSION,
	WTRL_JSON_SCHEMA_VERSION,
	WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION,
	WTRL_WALK_JSON_SCHEMA_VERSION,
	WTRL_SCHEMA_URI_BASE,
	emit_tracer,
	add_traceback,
	_apply_basedir,
	_resolve_object
	)
from sdv.doc.waterloo import docitem

import sdv.doc.waterloo.waterlint_common as wl_common

from sdv.doc.waterloo.docitem_helper import (
	tracer,
	Documentable,
	get_obj_fully_qualified_name,
	get_obj_path,
	)

# Not relevant yet, but in case we set up a plugin concept,
# vendors should be encouraged to follow semantic versioning
# for their plugins.
__version__ = "0.1.0"

WTRL_WALK_DEFAULT_SHOW_FIELDS = ("qualname", "kind", "scope", "file", "lineno", "included", "reason")
WTRL_WALK_ALLOWED_SHOW_FIELDS = set(WTRL_WALK_DEFAULT_SHOW_FIELDS + ("reason_detail",))
WTRL_WALK_ALLOWED_SORT_FIELDS = set(WTRL_WALK_DEFAULT_SHOW_FIELDS + ("reason_detail",))
WTRL_WALK_NUMERIC_SORT_FIELDS = frozenset({"lineno"})

def _emit_tracer(tr: tracer, out_path: str | None, out_json_path: str | None = None, debug: bool = False) -> None:
	wl_common.emit_tracer(
		tr,
		out_path,
		out_json_path,
		debug=debug,
		callback_build_json_doc=lambda tr_: _build_tracer_json_doc(tr_, include_debug=debug),
	)

def _build_tracer_json_doc(tr: tracer, include_debug: bool = False) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=WTRL_DOCITEM_VERSION,
		id_prefix=f"urn:waterlint:wtrl-tracer-json:{__version__}",
		include_debug=include_debug,
	)

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
		def _sort_key(entry: dict[str, Any], field: str = field) -> tuple[int, Any]:
			return _walk_sort_key_for_field(entry, field)
		entries.sort(key=_sort_key)


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
		_, lineno = inspect.getsourcelines(cast(Any, target))
		return lineno
	except Exception:
		return None

# Analyze for reason, included, scope, reason_detail
def _walk_analyze_object(obj: object) -> tuple[str, bool, str, str]:
	doc_txt = docitem.get_obj_docstring(obj)
	if not doc_txt:
		return ("no_doc", False, "unknown", "no Waterloo docstring found")
	tmp_tr = tracer()
	try:
		tree = docitem.make_docitem_tree(tmp_tr, doc_txt)
	except Exception as exc:
		return ("invalid", False, "unknown", f"{type(exc).__name__}: {exc}")
	if tmp_tr.has_errors():
		for _context, rule_id, _origin, msg, _details in tmp_tr.gen_errors():
			return ("invalid", False, "unknown", f"{rule_id}: {msg}")
		return ("invalid", False, "unknown", "docstring validation failed")
	scope_text = tree.get_scope_text()
	return ("included", True, scope_text, f"waterloo docstring parsed successfully; scope={scope_text}")

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
	obj_qnames: list[str],
	include_imported: bool,
	show_fields: list[str],
) -> dict[str, Any]:
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
			"obj": obj_qnames[0] if len(obj_qnames) == 1 else ", ".join(obj_qnames),
			"objs": obj_qnames,
			"include_imported": include_imported,
			"show": show_fields,
		},
		"__WTRL_SUMMARY__": wl_common.recompute_walk_summary(entries),
		"__WTRL_OBJECTS__": entries,
	}
	return doc


def walk_command(args: argparse.Namespace) -> int:
	tr = tracer()
#----- output spec --------------------------------------------#
	out_diag	= getattr(args, "out_diag", None)
	out_diag_json	= getattr(args, "out_diag_json", None)
#--------------------------------------------------------------#
	try:
		show_raw = getattr(args, "show", None)
		if show_raw:
			show_fields = []
			for part in str(show_raw).split(","):
				field = part.strip()
				if not field:
					continue
				if field == "default":
					for default_field in WTRL_WALK_DEFAULT_SHOW_FIELDS:
						if default_field not in show_fields:
							show_fields.append(default_field)
					continue
				if field not in show_fields:
					show_fields.append(field)
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

		obj_raw = getattr(args, "obj", None)
		obj_qnames: list[str] = []
		if obj_raw:
			for grp in obj_raw:
				if isinstance(grp, list):
					obj_qnames.extend(str(item).strip() for item in grp if str(item).strip())
				else:
					item = str(grp).strip()
					if item:
						obj_qnames.append(item)
		if not obj_qnames:
			print("Error: --obj is required for walk.", file=sys.stderr)
			return 2
		#----- Object traversal and config ----------------------------#
		config = docitem.ConfigTraversal()
		if getattr(args, "include_imported", True):
			config.enable_include_imported()
		config.disable_walk_packages()
		#----- Walk and build list of entries -------------------------#
		entries: list[dict[str, Any]] = []
		seen_qnames: set[str] = set()
		for obj_qname in obj_qnames:
			_apply_basedir(getattr(args, "basedir", None), obj_qname)
			obj = _resolve_object(obj_qname)
			for o in docitem.gen_documentable_objects(cast(Documentable, obj), config):
				qname = get_obj_fully_qualified_name(o)
				if qname in seen_qnames:
					continue
				seen_qnames.add(qname)
				reason, included, scope_text, reason_detail = _walk_analyze_object(o)
				entry: dict[str, Any] = {
					"qualname": qname,
					"kind": _walk_kind(o),
					"scope": scope_text,
					"file": get_obj_path(o),
					"lineno": _walk_lineno(o),
					"included": included,
					"reason": reason,
					"reason_detail": reason_detail,
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
			doc = _walk_build_json_doc(entries, getattr(args, "basedir", None), obj_qnames, getattr(args, "include_imported", True), show_fields)
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
		add_traceback(tr)
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
) -> argparse.ArgumentParser:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| construct and return the argparse subparser for the walk command.
	Parameters:
		subparsers:
			The argparse subparser registry of the main command line interface.
		parser_parts:
			Shared parser parts provided by the main program. Walk uses the formatter class, the global CLI options, and the base-directory group.
	Returns:
		|Must| return the configured walk subparser.
	Raises:
	"""
	prsr = subparsers.add_parser(
		"walk",
		help="Walk documentable objects and preview traversal/filtering",
		parents=[parser_parts["global_opts"], parser_parts["basedir_group"]],
		formatter_class=parser_parts["formatter_class"])
	prsr.add_argument(
		"--obj",
		required=True,
		nargs="+",
		action="append",
		metavar="QUALNAME",
		help="One or more qualified identifiers of modules/classes/functions/methods to traverse. Option may be repeated and grouped. This is the preview input for walk JSON and later render-json replay.",
	)
	prsr_out = prsr.add_mutually_exclusive_group()
	prsr_out.add_argument("--out", dest="out_file", metavar="FILE", help="Write prsr text output to FILE instead of stdout.")
	prsr_out.add_argument("--out-json", dest="out_json", metavar="FILE", help="Write prsr JSON output to FILE.")
	prsr.add_argument(
		"--show",
		metavar="FIELDS",
		help="Comma-separated list of fields to show in the text output (default: qualname,kind,scope,file,lineno,included,reason,reason_detail). Use 'default' as an alias for that list. Text output only; JSON stays complete.",
	)
	prsr.add_argument(
		"--sort",
		"--order",
		dest="sort",
		metavar="FIELDS",
		help="Comma-separated list of fields to sort by. The last field is applied first; sort is always ascending. Numeric fields sort numerically with null before 0; string and bool fields sort case-insensitively with underscores ignored. Applies to both text and JSON output order.",
	)
	prsr.add_argument("--include-imported", dest="include_imported", action="store_true", default=True, help="Include imported members and submodules (default).")
	prsr.add_argument("--no-include-imported", dest="include_imported", action="store_false", help="Do not include imported members/submodules.")
	prsr.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return prsr

if __name__ == "__main__":
	print(__version__)
	exit(0)
