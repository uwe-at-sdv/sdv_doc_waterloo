#!/usr/bin/env python3
"""Edit Waterloo walk JSON documents.

The first implementation step is intentionally small:
- read one validated walk JSON file
- optionally simplify it to included entries
- optionally recompute summary/statistics
- write the result back out

The module stays self-contained so that later carve-specific helpers can
move here without bloating waterlint.py further.
"""

from __future__ import annotations

import argparse
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

WTRL_SCHEMA_URI_BASE = "https://sci-d-vis.com/schema"
WTRL_WALK_JSON_SCHEMA_VERSION = "0.0.1"


def _emit_diagnostics(tr: tracer, dest: io.TextIOBase, strip_ansi: bool = False) -> None:
	wl_common.emit_diagnostics(tr, dest, debug=True, strip_ansi=strip_ansi)


def _build_tracer_json_doc(tr: tracer) -> dict[str, Any]:
	doc: dict[str, Any] = {
		"$schema": f"{WTRL_SCHEMA_URI_BASE}/wtrl-tracer-json-{WTRL_TRACER_JSON_SCHEMA_VERSION}.schema.json",
		"$id": f"urn:waterlint:wtrl-tracer-json:carve:{datetime.now().strftime('%Y%m%d%H%M%S')}",
		"__WTRL_VERSION__": {
			"waterloo": docitem.__version__,
			"schema": WTRL_TRACER_JSON_SCHEMA_VERSION,
		},
		"__WTRL_INFO__": [],
		"__WTRL_WARNING__": [],
		"__WTRL_ERROR__": [],
	}
	for context, origin, msg in tr.gen_infos():
		entry: dict[str, Any] = {"kind": "info", "origin": origin, "msg": msg, "context": context}
		cast(list[dict[str, Any]], doc["__WTRL_INFO__"]).append(entry)
	for context, rule_id, origin, msg, details in tr.gen_warnings():
		entry = {"kind": "warning", "origin": origin, "rule-id": rule_id, "msg": msg, "context": context, "details": details}
		cast(list[dict[str, Any]], doc["__WTRL_WARNING__"]).append(entry)
	for context, rule_id, origin, msg, details in tr.gen_errors():
		entry = {"kind": "error", "origin": origin, "rule-id": rule_id, "msg": msg, "context": context, "details": details}
		cast(list[dict[str, Any]], doc["__WTRL_ERROR__"]).append(entry)
	return doc


def _emit_tracer(tr: tracer, out_path: str | None, out_json_path: str | None = None) -> None:
	if out_path:
		with open(out_path, "w", encoding="utf-8") as fh:
			_emit_diagnostics(tr, fh, strip_ansi=True)
	else:
		print(tr.str_by_severity(tr.Severity.DEBUG), file=sys.stderr, end="")
	if out_json_path:
		doc = _build_tracer_json_doc(tr)
		with open(out_json_path, "w", encoding="utf-8") as fh:
			json.dump(doc, fh, indent=4)
			fh.write("\n")


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
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)
	try:
		in_file = getattr(args, "in_file", None)
		if not in_file:
			print("Error: --in is required for carve.", file=sys.stderr)
			return 2
		doc = _load_and_validate_walk_input(tr, in_file)
		if doc is None:
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		entries_raw = doc.get("__WTRL_OBJECTS__", [])
		if not isinstance(entries_raw, list):
			tr.add_error("CARVE-002", "tool", "__WTRL_OBJECTS__ is not an array.")
			_emit_tracer(tr, out_diag, out_diag_json)
			return 1
		entries = [cast(dict[str, Any], entry) for entry in entries_raw if isinstance(entry, dict)]
		simplify = bool(getattr(args, "simplify", False))
		recompute = bool(getattr(args, "recompute", False)) or simplify
		if simplify:
			entries = [entry for entry in entries if bool(entry.get("included", False))]
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
		if getattr(args, "out_file", None):
			with open(args.out_file, "w", encoding="utf-8") as fh:
				json.dump(doc, fh, indent=4)
				fh.write("\n")
		else:
			json.dump(doc, sys.stdout, indent=4)
			sys.stdout.write("\n")
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error("CARVE-800", "tool", f"[{get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, out_diag, out_diag_json)
		return 1

	_emit_tracer(tr, out_diag, out_diag_json)
	return 0


def build_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser], formatter_class: type[argparse.HelpFormatter], global_opts: argparse.ArgumentParser) -> argparse.ArgumentParser:
	carve = subparsers.add_parser(
		"carve",
		help="Edit walk JSON documents",
		parents=[global_opts],
		formatter_class=formatter_class,
	)
	carve.add_argument("--in", dest="in_file", required=True, metavar="FILE", help="Read exactly one walk JSON file.")
	carve.add_argument("--out", dest="out_file", metavar="FILE", help="Write walk JSON to FILE instead of stdout.")
	carve.add_argument("--simplify", action="store_true", help="Keep only included==true entries and recompute summary.")
	carve.add_argument("--recompute", action="store_true", help="Recompute summary/statistics from current entries.")
	carve.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return carve
