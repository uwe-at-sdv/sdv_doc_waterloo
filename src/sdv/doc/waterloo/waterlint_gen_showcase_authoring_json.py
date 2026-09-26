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
		|Must| provide the gen-showcase-authoring-json waterlint subcommand.
		|Must| copy a profile-specific packaged Authoring JSON showcase without modifying it.
Public_functions:
	gen_showcase_authoring_json_command, build_parser
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Final, cast

from sdv.doc.waterloo import docitem
from sdv.doc.waterloo import docitem_convert as cvrt
from sdv.doc.waterloo import waterlint_authoring as authoring
from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo.docitem_helper import tracer
from sdv.doc.waterloo.docitem_types import Profile_t


_AUTHORING_CATEGORY: Final[str] = "wtrl-authoring-object-json"
_TEMPLATE_NAMES: Final[dict[Profile_t, str]] = {
	"module": "showcase-authoring-module.json",
	"class": "showcase-authoring-class.json",
	"function": "showcase-authoring-function.json",
	"method": "showcase-authoring-method.json",
	"inherited_method": "showcase-authoring-inherited-method.json",
}


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


def _validate_template(tr: tracer, document: dict[str, object]) -> bool:
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
		tr.add_error("JIDO-001", "tool", issue.message, {"path": issue.path, "issue": issue.code})
	return not tr.has_errors()


def gen_showcase_authoring_json_command(args: argparse.Namespace, waterlint_version: str) -> int:
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
			|Must| copy one packaged Authoring JSON showcase selected by |var|`args.profile`.
			|Must| validate the packaged document before writing it.
	Parameters:
		args:
			Parsed command line options including a required Waterloo profile and an optional output target.
		waterlint_version:
			Version string used for structured tracer diagnostics.
	Returns:
		|Must| return zero on success and a non-zero status after a reported error.
	Raises:
		OSError:
			|May| be raised if the packaged template cannot be read or the output target cannot be written.
	"""
	tr = tracer()
	try:
		profile = cast(Profile_t, args.profile)
		template_path = Path(__file__).resolve().parent / "templates" / _TEMPLATE_NAMES[profile]
		template_text = template_path.read_text(encoding="utf-8")
		document = json.loads(template_text)
		if not isinstance(document, dict):
			raise ValueError("Packaged Authoring JSON showcase must contain one object.")
		if not _validate_template(tr, cast(dict[str, object], document)):
			_emit_tracer(tr, args, waterlint_version)
			return 1
		wl_common.write_text_output(template_text, getattr(args, "out_file", None))
	except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
		tr.add_error("JIDO-003", "tool", str(exc))
		_emit_tracer(tr, args, waterlint_version)
		return 1
	_emit_tracer(tr, args, waterlint_version)
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
			|Must| construct and return the gen-showcase-authoring-json subparser.
	Parameters:
		subparsers:
			The argparse subparser registry provided by waterlint.
		parser_parts:
			Shared parser components provided by the main program.
	Returns:
		|Must| return a parser requiring |opt|`--profile` and accepting an optional |opt|`--out` target.
	Raises:
	"""
	parser = subparsers.add_parser(
		"gen-showcase-authoring-json",
		help="Write a profile-specific Waterloo Authoring JSON showcase.",
		parents=[parser_parts["global_opts"]],
		formatter_class=parser_parts["formatter_class"],
	)
	parser.add_argument(
		"--profile", required=True, choices=tuple(_TEMPLATE_NAMES), metavar="PROFILE",
		help="Profile demonstrated by the showcase template.",
	)
	parser.add_argument(
		"--out", dest="out_file", metavar="FILE|@STDOUT",
		help="Write the showcase to FILE or @STDOUT (default: stdout).",
	)
	parser.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return parser
