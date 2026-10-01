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
		|Must| provide the extract-authoring-json waterlint subcommand.
		|Must| extract Authoring JSON only from a Waterloo-valid documented object.
		|Must_not| modify the inspected object or its source file.
Public_functions:
	extract_authoring_json_command, build_parser
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

from sdv.doc.waterloo import docitem
from sdv.doc.waterloo import docitem_convert as cvrt
from sdv.doc.waterloo import waterlint_authoring as authoring
from sdv.doc.waterloo import waterlint_authoring_extract as extract
from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo.docitem_helper import ResolveObjectError, get_obj_fully_qualified_name, tracer
from sdv.doc.waterloo.docitem_tracer import traced_section


_AUTHORING_CATEGORY = "wtrl-authoring-object-json"


def _build_tracer_json_doc(tr: tracer, waterlint_version: str) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=wl_common.WTRL_WATERLOO_VERSION,
		id_prefix=f"urn:waterlint:wtrl-tracer-json:{waterlint_version}",
	)


def _emit_tracer(tr: tracer, args: argparse.Namespace, waterlint_version: str) -> None:
	wl_common.emit_tracer(
		tr,
		getattr(args, "out_diag", None),
		getattr(args, "out_diag_json", None),
		debug=bool(getattr(args, "debug", False)),
		callback_build_json_doc=lambda current: _build_tracer_json_doc(current, waterlint_version),
	)


def _validate_extracted_document(tr: tracer, document: dict[str, object]) -> bool:
	"""Defend the extraction boundary with the public Authoring JSON schema."""
	schema_path = Path(__file__).resolve().parent / "schema" / (
		f"{_AUTHORING_CATEGORY}-{wl_common.WTRL_AUTHORING_OBJECT_JSON_SCHEMA_VERSION}.schema.json"
	)
	wl_common.validate_json_against_schema(
		tr, cast(cvrt.WtrlJsonNode_t, document), str(schema_path), "JIDO-003", "JIDO-000",
	)
	if tr.has_errors():
		return False
	loaded = authoring.load_authoring_document(document)
	for issue in authoring.validate_authoring_document(loaded):
		details: dict[str, str | list[str]] = {"path": issue.path, "issue": issue.code}
		if issue.severity == "warning":
			tr.add_warning("JIDO-001", "tool", issue.message, details)
		else:
			tr.add_error("JIDO-001", "tool", issue.message, details)
	return not tr.has_errors()


def extract_authoring_json_command(args: argparse.Namespace, waterlint_version: str) -> int:
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
			|Must| resolve, validate, and convert one documented object into Authoring JSON.
			|Must_not| write output unless source validation and Authoring JSON validation both succeed.
	Parameters:
		args:
			Parsed options containing |attr|`obj`, optional |attr|`basedir`, and an optional output target.
		waterlint_version:
			Version used in structured tracer diagnostics.
	Returns:
		|Must| return zero after writing valid Authoring JSON and non-zero after a reported error.
	Raises:
	"""
	tr = tracer()
	session = docitem.DocSession()
	try:
		wl_common._apply_basedir(getattr(args, "basedir", None), args.obj)
		obj = wl_common._resolve_object(args.obj)
		if not docitem.is_obj_documentable(obj):
			tr.add_error("TOOL-001", "tool", f"Object '{args.obj}' is not documentable.")
			_emit_tracer(tr, args, waterlint_version)
			return 1
		with traced_section(tr, get_obj_fully_qualified_name(obj)):
			tr.add_info(f"extracting Authoring JSON from '{get_obj_fully_qualified_name(obj)}'")
			doc = docitem.validate_docstring(tr, obj, None, session)
		if tr.has_errors():
			_emit_tracer(tr, args, waterlint_version)
			return 1
		document = extract.build_authoring_json_from_docstring(obj, doc)
		if not _validate_extracted_document(tr, document):
			_emit_tracer(tr, args, waterlint_version)
			return 1
		wl_common.write_json_output(
			cast(cvrt.WtrlJsonNode_t, document), getattr(args, "out_file", None), ensure_ascii=False,
		)
	except ResolveObjectError as exc:
		tr.add_error("TOOL-001", "tool", str(exc), exc.to_details())
		_emit_tracer(tr, args, waterlint_version)
		return 1
	except (ImportError, OSError) as exc:
		tr.add_error("TOOL-001", "tool", str(exc))
		_emit_tracer(tr, args, waterlint_version)
		return 1
	except (TypeError, ValueError, RuntimeError) as exc:
		tr.add_error("JIDO-003", "tool", str(exc))
		_emit_tracer(tr, args, waterlint_version)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error("JIDO-000", "tool", f"[{get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, args, waterlint_version)
		return 1
	_emit_tracer(tr, args, waterlint_version)
	return 0


def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
) -> argparse.ArgumentParser:
	"""Build the extract-authoring-json parser using waterlint's shared options."""
	parser = subparsers.add_parser(
		"extract-authoring-json",
		help="Extract canonical Authoring JSON from one Waterloo-valid documented object.",
		parents=[parser_parts["global_opts"], parser_parts["basedir_group"]],
		formatter_class=parser_parts["formatter_class"],
	)
	parser.add_argument("--obj", required=True, metavar="QUALNAME", help="Exactly one qualified documented object name.")
	parser.add_argument(
		"--out", dest="out_file", metavar="FILE|@STDOUT",
		help="Write Authoring JSON to FILE or @STDOUT (default: stdout).",
	)
	parser.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return parser
