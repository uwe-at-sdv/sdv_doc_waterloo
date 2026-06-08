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
		|Must| edit Waterloo walk JSON documents in a small, self-contained command module.
Public_functions:
	carve_qname_matches_expression, carve_command, build_parser
Function_overview:
	carve_qname_matches_expression:
		Determine whether a qualified name matches a segment-aware expression with Unix shell-style wildcards.
	carve_command:
		Execute the carve command by loading exactly one validated walk JSON file,
		optionally simplifying it to included entries, optionally applying a
		segment-aware expression-based drop/keep chain, optionally recomputing the summary
		statistics, and then writing the resulting document back out.
	build_parser:
		Construct the carve subcommand parser and connect it to the global CLI.
Notes:
	General note:
		The first implementation step is intentionally small.
		Later carve-specific helpers can still move here without bloating waterlint.py further.
"""

from __future__ import annotations

import argparse
import fnmatch
import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from sdv.doc.waterloo import docitem
from sdv.doc.waterloo.docitem_helper import (
	tracer,
	get_obj_fully_qualified_name,
	WTRL_TRACER_JSON_SCHEMA_VERSION,
)
from sdv.doc.waterloo import waterlint_common as wl_common

# Not relevant yet, but in case we set up a plugin concept,
# vendors should be encouraged to follow semantic versioning
# for their plugins.
__version__ = "0.1.0"

WTRL_SCHEMA_URI_BASE = "https://sci-d-vis.com/schema"
WTRL_WALK_JSON_SCHEMA_VERSION = "0.0.1"


class _DropKeepAction(argparse.Action):
	def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any, option_string: str | None = None) -> None:
		chain = getattr(namespace, self.dest, None)
		if not isinstance(chain, list):
			chain = []
		op = "drop" if option_string == "--drop" else "keep"
		for value in values:
			prefix = str(value).strip()
			if not prefix:
				raise argparse.ArgumentError(self, "empty prefix is not allowed")
			chain.append((op, prefix))
		setattr(namespace, self.dest, chain)


def _carve_normalize_path(path_text: str | None) -> Path | None:
	if not path_text:
		return None
	try:
		return Path(path_text).expanduser().resolve()
	except Exception:
		try:
			return Path(Path(path_text).expanduser().absolute())
		except Exception:
			return None


def _carve_path_is_under(path: Path, prefix: Path) -> bool:
	try:
		return path == prefix or path.is_relative_to(prefix)
	except Exception:
		return False


def carve_qname_matches_expression(qname: str, expression: str) -> bool:
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
			|Must| determine whether the given qualified name matches the given segment-aware expression.\
			The expression supports Unix shell-style wildcards and is matched against the qualified name as a whole,\
			the last segment (tail), and each individual segment.
			|Must| strip leading and trailing whitespace from the expression before processing.
			|Must| fail to match if the stripped expression is empty.
			|Must| use |mod|`fnmatch`-style matching for expressions containing wildcard characters |lit|`*?[]`.
	Parameters:
		qname:
			The qualified name to test, typically of a function, class, or module.
		expression:
			The segment-aware expression to match against.
	Returns:
		|True| if the qualified name matches the expression, |False| otherwise.
	Raises:
	Notes:
		Todo:
			The contract needs to be finalized and the implementation may need to be adjusted accordingly.
			The current approach is a best effort to support flexible patterns while being intuitive for common cases.
			We are sure though about the requirement to strip whitespace and reject empty expressions,
			as well as the general idea of matching against the whole qualified name, the tail segment, and each individual segment.
		Examples:
			- Expression "mypackage.*" matches "mypackage.module", "mypackage.sub.module", but not "otherpackage.module".
			- Expression "*.helper" matches "mypackage.helper", "otherpackage.helper", but not "mypackage.util".
			- Expression "*util*" matches "mypackage.util", "mypackage.helper.util", but not "mypackage.helper".
			- Expression "helper" matches "mypackage.helper", "helper", but not "mypackage.util".
	"""
	expression = expression.strip()
	# An empty expression is not a valid match for anything.
	if not expression:
		return False
	# If the expression contains any wildcard characters, we apply fnmatch-style matching against the whole qualified name,
	# the tail segment, and each individual segment. This allows for flexible patterns like "mypackage.*", "*.helper", or "*util*".
	if any(ch in expression for ch in "*?[]"):
		if fnmatch.fnmatchcase(qname, expression):
			return True
		tail = qname.split(".")[-1]
		if fnmatch.fnmatchcase(tail, expression):
			return True
		return any(fnmatch.fnmatchcase(part, expression) for part in qname.split("."))
	# If there are no wildcard characters, we check for exact matches against
	# the whole qualified name, the tail segment, and each individual segment.
	# This allows for simple patterns like "mypackage.module" or "helper".
	if qname == expression or qname.startswith(f"{expression}."):
		return True
	# A final check for the tail segment is needed to allow matching the last segment
	# without a trailing dot, e.g. "helper" should match "mypackage.helper".
	if qname.endswith(f".{expression}"):
		return True
	# A final check for the tail segment alone allows matching the last segment
	# without a dot, e.g. "helper" should match "mypackage.helper".
	return qname.split(".")[-1] == expression


def _carve_apply_drop_keep_filters(entries: list[dict[str, Any]], chain: list[tuple[str, str]]) -> list[dict[str, Any]]:
	if not chain:
		return entries
	keep_state = chain[0][0] == "drop"
	out: list[dict[str, Any]] = []
	for entry in entries:
		qname = str(entry.get("qualname", ""))
		state = keep_state
		for op, expression in chain:
			if carve_qname_matches_expression(qname, expression):
				state = op == "keep"
		if state:
			out.append(entry)
	return out


def _carve_drop_non_basedir(tr: tracer, entries: list[dict[str, Any]], basedir_text: str | None) -> list[dict[str, Any]]:
	basedir_path = _carve_normalize_path(basedir_text)
	if basedir_path is None:
		tr.add_error("CARVE-003", "tool", "Walk input does not define a usable basedir for --drop-non-basedir.")
		return entries
	out: list[dict[str, Any]] = []
	for entry in entries:
		file_txt = entry.get("file")
		file_path = _carve_normalize_path(file_txt if isinstance(file_txt, str) else None)
		if file_path is None:
			out.append(entry)
			continue
		if _carve_path_is_under(file_path, basedir_path):
			out.append(entry)
	return out


def _emit_diagnostics(tr: tracer, dest: io.TextIOBase, strip_ansi: bool = False, debug: bool = False) -> None:
	wl_common.emit_diagnostics(tr, dest, debug=debug, strip_ansi=strip_ansi)


def _build_tracer_json_doc(tr: tracer, include_debug: bool = False) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=docitem.__version__,
		id_prefix="urn:waterlint:wtrl-tracer-json:carve",
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


def _load_and_validate_walk_input(tr: tracer, path: str) -> dict[str, Any] | None:
	doc = wl_common.load_json(path)
	if not isinstance(doc, dict):
		tr.add_error("CARVE-001", "tool", f"Walk input must be a JSON object: {path}")
		return None
	schema_path = Path(__file__).resolve().parent / "schema" / f"wtrl-walk-json-{WTRL_WALK_JSON_SCHEMA_VERSION}.schema.json"
	wl_common.validate_json_against_schema(tr, doc, str(schema_path), "CARVE-001", "CARVE-800")
	if tr.has_errors():
		return None
	return doc


def carve_command(args: argparse.Namespace) -> int:
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
			|Must| execute the carve command on exactly one validated walk JSON file and write the resulting document back out.
	Parameters:
		args:
			Namespace containing the parsed carve command line options.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	Notes:
		Parameters:
			The function is called from the carve subcommand with the parsed argparse Namespace.
		General note:
			The function intentionally keeps the first implementation step small and self-contained.
			Drop/keep filters are applied as an ordered segment-aware expression chain.
	"""
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)
	debug = bool(getattr(args, "debug", False))
	try:
		in_file = getattr(args, "in_file", None)
		if not in_file:
			print("Error: --in is required for carve.", file=sys.stderr)
			return 2
		doc = _load_and_validate_walk_input(tr, in_file)
		if doc is None:
			_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
			return 1
		entries_raw = doc.get("__WTRL_OBJECTS__", [])
		if not isinstance(entries_raw, list):
			tr.add_error("CARVE-002", "tool", "__WTRL_OBJECTS__ is not an array.")
			_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
			return 1
		entries = [cast(dict[str, Any], entry) for entry in entries_raw if isinstance(entry, dict)]
		tested = len(entries)
		simplify = bool(getattr(args, "simplify", False))
		drop_keep_chain = list(getattr(args, "drop_keep_chain", []) or [])
		drop_non_basedir = bool(getattr(args, "drop_non_basedir", False))
		recompute = bool(getattr(args, "recompute", False)) or simplify or bool(drop_keep_chain) or drop_non_basedir
		if simplify:
			entries = [entry for entry in entries if bool(entry.get("included", False))]
		if drop_keep_chain:
			entries = _carve_apply_drop_keep_filters(entries, drop_keep_chain)
		if drop_non_basedir:
			meta = doc.get("__WTRL_META__", {})
			basedir_text = meta.get("basedir") if isinstance(meta, dict) else None
			entries = _carve_drop_non_basedir(tr, entries, basedir_text if isinstance(basedir_text, str) else None)
			if tr.has_errors():
				_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
				return 1
		if recompute:
			doc["__WTRL_SUMMARY__"] = wl_common.recompute_walk_summary(entries)
		doc["__WTRL_OBJECTS__"] = entries
		meta = doc.get("__WTRL_META__", {})
		if not isinstance(meta, dict):
			meta = {}
			doc["__WTRL_META__"] = meta
		meta["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
		meta["generator"] = "waterlint.carve"
		doc["$id"] = f"urn:waterlint:wtrl-walk-json:carve:{datetime.now().strftime('%Y%m%d%H%M%S')}"
		kept = len(entries)
		dropped = tested - kept
		tr.add_info(f"Num entries tested: {tested}.")
		tr.add_info(f"Num entries kept: {kept}.")
		tr.add_info(f"Num entries dropped: {dropped}.")
		if getattr(args, "out_file", None):
			with open(args.out_file, "w", encoding="utf-8") as fh:
				json.dump(doc, fh, indent=4)
				fh.write("\n")
		else:
			json.dump(doc, sys.stdout, indent=4)
			sys.stdout.write("\n")
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error("CARVE-800", "tool", f"[{get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
	return 0


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
			|Must| construct and return the argparse subparser for the carve command.
	Parameters:
		subparsers:
			The argparse subparser registry of the main command line interface.
		parser_parts:
			Shared parser parts provided by the main program. Carve uses the formatter class and the global CLI options.
	Returns:
		|Must| return the configured carve subparser.
	Raises:
	"""
	prsr = subparsers.add_parser(
		"carve",
		help="Edit walk JSON documents",
		parents=[parser_parts["global_opts"]],
		formatter_class=parser_parts["formatter_class"],
	)
	prsr.add_argument("--in", dest="in_file", required=True, metavar="FILE", help="Read exactly one walk JSON file.")
	prsr.add_argument("--out", dest="out_file", metavar="FILE", help="Write walk JSON to FILE instead of stdout.")
	prsr.add_argument("--simplify", action="store_true", help="Keep only included==true entries and recompute summary.")
	prsr.add_argument("--drop", dest="drop_keep_chain", action=_DropKeepAction, nargs="+", metavar="QUALNAME", help="Drop entries whose qualified names match the given segment-aware expression chain. The first --drop begins with keep-all.")
	prsr.add_argument("--keep", dest="drop_keep_chain", action=_DropKeepAction, nargs="+", metavar="QUALNAME", help="Keep entries whose qualified names match the given segment-aware expression chain. The first --keep begins with drop-all.")
	prsr.add_argument("--drop-non-basedir", action="store_true", help="Drop entries whose file path is outside the input basedir.")
	prsr.add_argument("--recompute", action="store_true", help="Recompute summary/statistics from current entries.")
	prsr.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return prsr

if __name__ == "__main__":
	print(__version__)
	exit(0)
