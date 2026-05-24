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
		|Must| provide shared implementation helpers for the gen-minimal and gen-full command family.
Public_functions:
	generate_command, build_parser
Function_overview:
	generate_command:
		Execute the shared generation workflow for either the minimal or full mode.
		The command-specific wrapper passes in the selected mode and the current waterlint version.
	build_parser:
		Construct and return the argparse subparser for a generate subcommand.
Notes:
	General note:
		The shared helpers keep the plugin wrappers small and make it easier to preserve a stable CLI shape.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Literal

from sdv.doc.waterloo import docitem
from sdv.doc.waterloo import docitem_genutil as genutil
from sdv.doc.waterloo.docitem_helper import (
	Documentable,
	get_obj_fully_qualified_name,
	tracer,
)
from sdv.doc.waterloo import waterlint_common as wl_common

SOURCE_CODE_ERRORS = (
	AttributeError,
	IndexError,
	KeyError,
	NameError,
	AssertionError,
	NotImplementedError,
	SyntaxError,
)


def _build_tracer_json_doc(tr: tracer, waterlint_version: str, include_debug: bool = False) -> dict[str, Any]:
	return wl_common.build_tracer_json_doc(
		tr,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=wl_common.WTRL_DOCITEM_VERSION,
		id_prefix=f"urn:waterlint:wtrl-tracer-json:{waterlint_version}",
		include_debug=include_debug,
	)


def _emit_tracer(
	tr: tracer,
	out_path: str | None,
	out_json_path: str | None,
	waterlint_version: str,
	debug: bool = False,
) -> None:
	wl_common.emit_tracer(
		tr,
		out_path,
		out_json_path,
		debug=debug,
		callback_build_json_doc=lambda tr_: _build_tracer_json_doc(tr_, waterlint_version, include_debug=debug),
	)


def _final_exit_code(base_code: int, tr: tracer, fail_on_warning: bool) -> int:
	code = base_code
	if tr.has_errors():
		code = 1
	if code == 0 and fail_on_warning and tr.has_warnings():
		code = 1
	return code


def _leading_ws_width(s: str) -> int:
	n = 0
	for ch in s:
		if ch == "\t" or ch == " ":
			n += 1
		else:
			break
	return n


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
		wl_common._apply_basedir(basedir, qname)
		obj = wl_common._resolve_object(qname)
		if not docitem.is_obj_documentable(obj):
			continue
		root: Documentable = obj
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


def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
	command_name: str,
	help_text: str,
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
			|Must| construct and return the argparse subparser for a generate command.
	Parameters:
		subparsers:
			The argparse subparser registry of the main command line interface.
		parser_parts:
			Shared parser parts provided by the main program.
		command_name:
			Subcommand name, such as |lit|`gen-minimal` or |lit|`gen-full`.
		help_text:
			Short help text shown in command listings.
	Returns:
		|Must| return the configured generate subparser.
	Raises:
	"""
	prsr = subparsers.add_parser(
		command_name,
		help=help_text,
		parents=[parser_parts["global_opts"], parser_parts["basedir_group"]],
		formatter_class=parser_parts["formatter_class"],
	)
	prsr.add_argument(
		"--obj",
		required=True,
		nargs="+",
		action="append",
		metavar="QUALNAME",
		help="One or more qualified objects to generate docstring skeletons for. Option may be repeated.",
	)
	prsr.add_argument("--recursive", action="store_true", help="Recursively traverse documentable objects below each --obj.")
	prsr.add_argument("--missing-only", action="store_true", help="Generate only for objects without docstring.")
	prsr.add_argument("--format", choices=["raw", "json"], default=None, help="Output format. Default: raw, or json if --recursive is set.")
	prsr.add_argument("--out", dest="out_file", metavar="FILE", help="Write output to FILE instead of stdout.")
	prsr.add_argument("--indent", choices=["tab", "spc4"], default="spc4", help="Indent unit for generated docstring text (default: spc4).")
	prsr.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return prsr


def _generate_command(args: argparse.Namespace, mode: Literal["minimal", "full"], waterlint_version: str) -> int:
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)
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
				_emit_tracer(tr, out_diag, out_diag_json, waterlint_version, debug=bool(args.debug))
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
			wl_common.add_traceback(tr)
			_emit_tracer(tr, out_diag, out_diag_json, waterlint_version, debug=bool(args.debug))
			return 1
		raise
	except Exception as exc:
		tr.add_error("TOOL-821", "tool", f"[{get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, out_diag, out_diag_json, waterlint_version, debug=bool(args.debug))
		return 1
	_emit_tracer(tr, out_diag, out_diag_json, waterlint_version, debug=bool(args.debug))
	return _final_exit_code(0, tr, args.fail_on_warning)


def gen_minimal_command(args: argparse.Namespace, waterlint_version: str) -> int:
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
			|Must| run the gen-minimal command implementation.
	Parameters:
		args:
			Parsed gen-minimal command line options.
		waterlint_version:
			Version string supplied by the main program for tracer metadata.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	return _generate_command(args, "minimal", waterlint_version)


def gen_full_command(args: argparse.Namespace, waterlint_version: str) -> int:
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
			|Must| run the gen-full command implementation.
	Parameters:
		args:
			Parsed gen-full command line options.
		waterlint_version:
			Version string supplied by the main program for tracer metadata.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	return _generate_command(args, "full", waterlint_version)
