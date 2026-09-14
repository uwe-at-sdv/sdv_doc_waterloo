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
		|Must| generate editable Waterloo Authoring JSON documents from one resolved Python object.
		|Must_not| modify source files or existing docstrings.
Public_functions:
	build_authoring_json, gen_minimal_authoring_json_command,
	gen_full_authoring_json_command, build_parser
"""

from __future__ import annotations

import argparse
import inspect
from pathlib import Path
from typing import Any, Callable, Literal, cast

from sdv.doc.waterloo import docitem
from sdv.doc.waterloo import docitem_convert as cvrt
from sdv.doc.waterloo import docitem_genutil as genutil
from sdv.doc.waterloo import waterlint_authoring as authoring
from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo.docitem_helper import (
	Profile_t,
	ResolveObjectError,
	SECTION_PROPERTIES,
	get_allowed_sections_for_profile,
	get_obj_fully_qualified_name,
	tracer,
)


AuthoringMode_t = Literal["minimal", "full"]
_AUTHORING_CATEGORY = "wtrl-authoring-object-json"


def _build_tracer_json_doc(tr: tracer, waterlint_version: str) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=wl_common.WTRL_DOCITEM_VERSION,
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


def _parameter_names(obj: object, profile: Profile_t) -> tuple[str, ...]:
	if profile not in {"function", "method"}:
		return ()
	parameters = list(inspect.signature(cast(Callable[..., Any], obj)).parameters)
	if profile == "method" and parameters and parameters[0] in {"self", "cls", "mcls"}:
		parameters.pop(0)
	return tuple(parameters)


def _required_normative_sections(sections: dict[str, object]) -> list[str]:
	return [
		label
		for label in sections
		if label != "Preamble" and SECTION_PROPERTIES[label]["normativity"] == "normative"
	]


def _text_block(text: str) -> list[dict[str, str]]:
	return [{"paragraph": text}]


def _build_minimal_sections(profile: Profile_t, parameter_names: tuple[str, ...]) -> dict[str, object]:
	sections: dict[str, object] = {
		"Contract": {"general": ["|Must| describe the externally visible behavior."]},
	}
	contract = cast(dict[str, object], sections["Contract"])
	if profile == "class":
		contract["constructor"] = ["|Must| describe construction requirements and guarantees."]
	if profile in {"function", "method"}:
		sections["Parameters"] = {
			name: _text_block(f"TODO: describe |var|`{name}`.")
			for name in parameter_names
		}
		sections["Returns"] = _text_block("TODO: describe the return value.")
		sections["Raises"] = {}
	return sections


def _add_full_sections(profile: Profile_t, sections: dict[str, object]) -> None:
	for label in get_allowed_sections_for_profile(profile):
		if label in sections:
			continue
		category = SECTION_PROPERTIES[label]["category"]
		if label == "Description":
			sections[label] = _text_block("TODO: provide an informative description.")
		elif category == "STRUCTURE":
			sections[label] = {}
		# List-based sections need a meaningful source-derived item. Do not emit
		# fictional qualified identifiers merely to make an empty section visible.


def build_authoring_json(obj: object, mode: AuthoringMode_t) -> dict[str, object]:
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
			|Must| create one schema-shaped Authoring JSON document for |var|`obj`.
			|Must| infer the profile, qualified name, signature, and callable parameter labels from |var|`obj`.
			|Must_not| inspect or reuse an existing docstring.
	Parameters:
		obj:
			One documentable Python object.
		mode:
			Either |value|`minimal` or |value|`full`.
	Returns:
		|Must| return a schema-shaped Authoring JSON object.
	Raises:
		RuntimeError:
			|May| raise if the object's profile cannot be inferred or is not supported by this generator.
	"""
	profile = genutil.infer_docstring_profile(obj)
	if profile == "inherited_method":
		raise RuntimeError("Authoring JSON generation for inherited_method requires explicit base-method context.")
	qualified_name = get_obj_fully_qualified_name(obj)
	sections = _build_minimal_sections(profile, _parameter_names(obj, profile))
	if mode == "full":
		_add_full_sections(profile, sections)
	preamble = {
		"profile": profile,
		"normative_sections": _required_normative_sections(sections),
	}
	# Calculate Preamble last, but expose it first for human and agent editing.
	sections = {"Preamble": preamble, **sections}
	document: dict[str, object] = {
		"$schema": f"{wl_common.WTRL_SCHEMA_URI_BASE}/{_AUTHORING_CATEGORY}-{wl_common.WTRL_AUTHORING_OBJECT_JSON_SCHEMA_VERSION}.schema.json",
		"$id": f"urn:waterlint:{_AUTHORING_CATEGORY}:{qualified_name}",
		"__WTRL_CATEGORY__": _AUTHORING_CATEGORY,
		"__WTRL_VERSION__": {"schema": wl_common.WTRL_AUTHORING_OBJECT_JSON_SCHEMA_VERSION},
		"qualified_name": qualified_name,
		"profile": profile,
		"doc": sections,
	}
	if profile in {"function", "method"}:
		document["signature"] = str(inspect.signature(cast(Callable[..., Any], obj)))
	return document


def _validate_generated_document(tr: tracer, document: dict[str, object]) -> bool:
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


def _generate_authoring_json_command(
	args: argparse.Namespace,
	mode: AuthoringMode_t,
	waterlint_version: str,
) -> int:
	tr = tracer()
	try:
		wl_common._apply_basedir(getattr(args, "basedir", None), args.obj)
		obj = wl_common._resolve_object(args.obj)
		if not docitem.is_obj_documentable(obj):
			tr.add_error("TOOL-001", "tool", f"Object '{args.obj}' is not documentable.")
			_emit_tracer(tr, args, waterlint_version)
			return 1
		document = build_authoring_json(obj, mode)
		if not _validate_generated_document(tr, document):
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


def gen_minimal_authoring_json_command(args: argparse.Namespace, waterlint_version: str) -> int:
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
			|Must| generate one minimal Authoring JSON document from the object named by |var|`args`.
	Parameters:
		args:
			Parsed command line options including one qualified object name.
		waterlint_version:
			Version string used for structured tracer diagnostics.
	Returns:
		|Must| return zero on success and a non-zero status after a reported error.
	Raises:
		RuntimeError:
			|May| raise only after an unexpected internal failure.
	"""
	return _generate_authoring_json_command(args, "minimal", waterlint_version)


def gen_full_authoring_json_command(args: argparse.Namespace, waterlint_version: str) -> int:
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
			|Must| generate one full Authoring JSON document from the object named by |var|`args`.
	Parameters:
		args:
			Parsed command line options including one qualified object name.
		waterlint_version:
			Version string used for structured tracer diagnostics.
	Returns:
		|Must| return zero on success and a non-zero status after a reported error.
	Raises:
		RuntimeError:
			|May| raise only after an unexpected internal failure.
	"""
	return _generate_authoring_json_command(args, "full", waterlint_version)


def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
	command_name: Literal["gen-minimal-authoring-json", "gen-full-authoring-json"],
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
			|Must| construct and return one single-object Authoring JSON generator subparser.
	Parameters:
		subparsers:
			The argparse subparser registry provided by waterlint.
		parser_parts:
			Shared parser components provided by waterlint.
		command_name:
			The minimal or full Authoring JSON generator command name.
	Returns:
		|Must| return the configured subparser.
	Raises:
	"""
	parser = subparsers.add_parser(
		command_name,
		help=f"Generate one {command_name.removeprefix('gen-').removesuffix('-json')} document.",
		parents=[parser_parts["global_opts"], parser_parts["basedir_group"]],
		formatter_class=parser_parts["formatter_class"],
	)
	parser.add_argument("--obj", required=True, metavar="QUALNAME", help="Exactly one qualified documentable object name.")
	parser.add_argument("--out", dest="out_file", metavar="FILE", help="Write Authoring JSON to FILE instead of stdout.")
	parser.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return parser
