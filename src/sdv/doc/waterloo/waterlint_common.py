#!/usr/bin/env python3
"""Shared helpers for waterlint command implementations."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any, cast

import jsonschema.exceptions
from jsonschema import Draft202012Validator

from sdv.doc.waterloo.docitem_helper import (
	RE_ANSI_SGR_COMPILED,
	get_obj_fully_qualified_name,
	tracer,
)

WTRL_SCHEMA_URI_BASE = "https://sci-d-vis.com/schema"


def tokens_to_json_pointer(tokens: list[object]) -> str:
	if not tokens:
		return ""
	def _esc(seg: object) -> str:
		return str(seg).replace("~", "~0").replace("/", "~1")
	return "/" + "/".join(_esc(t) for t in tokens)


def load_json(path: str | None) -> Any:
	if path:
		with open(path, "r", encoding="utf-8") as fh:
			return cast(Any, json.load(fh))
	return cast(Any, json.load(sys.stdin))


def emit_diagnostics(tr: tracer, dest: io.TextIOBase, debug: bool = False, strip_ansi: bool = False) -> None:
	severity = tr.Severity.DEBUG if debug else tr.Severity.INFO
	txt = tr.str_by_severity(severity)
	if strip_ansi:
		txt = RE_ANSI_SGR_COMPILED.sub("", txt)
	dest.write(txt)


def validate_json_against_schema(
	tr: tracer,
	doc: Any,
	schema_path: str,
	rule_id_validation: str,
	rule_id_fallback: str,
) -> None:
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
