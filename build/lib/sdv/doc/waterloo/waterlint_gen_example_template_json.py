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
		|Must| generate template JSON for __WTRL_EXAMPLE_REFS__ mappings.
Public_functions:
	gen_example_template_json_command, build_parser
Function_overview:
	gen_example_template_json_command:
		Build and write a template JSON document for __WTRL_EXAMPLE_REFS__ mappings.
		The result can be checked with |cmd|`waterlint validate-json`.
	build_parser:
		Construct and return the argparse subparser for the gen-example-template-json command.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from sdv.doc.waterloo import docitem
from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo.docitem_helper import (
	get_obj_fully_qualified_name,
	tracer,
)

# Not relevant yet, but in case we set up a plugin concept,
# vendors should be encouraged to follow semantic versioning
# for their plugins.
__version__ = "0.1.0"


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


def _render_example_refs_template(org_or_project: str = "none", domain: str = "local") -> dict[str, Any]:
	nodes: dict[str, Any] = {}
	nodes["$schema"] = f"{wl_common.WTRL_SCHEMA_URI_BASE}/wtrl-example-refs-json-{wl_common.WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION}.schema.json"
	nodes["$id"] = f"urn:{org_or_project}:{domain}:wtrl-example-refs-json:{wl_common.WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION}"
	nodes["__WTRL_VERSION__"] = {
		"waterloo": wl_common.WTRL_DOCITEM_VERSION,
		"waterlint_min": __version__,
		"schema": wl_common.WTRL_EXAMPLE_REFS_JSON_SCHEMA_VERSION,
	}
	nodes["__WTRL_EXAMPLE_REFS__"] = {
		"my_module.my_function": ["path/to/example1.py", "path/to/example2.py"],
	}
	return nodes


def gen_example_template_json_command(args: argparse.Namespace, waterlint_version: str) -> int:
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)
	try:
		org_or_project = str(getattr(args, "org_or_project", "none"))
		domain = str(getattr(args, "domain", "local"))
		nodes = _render_example_refs_template(org_or_project=org_or_project, domain=domain)
		out_file = getattr(args, "out_file", None)
		if out_file:
			with open(out_file, "w", encoding="utf-8") as fh:
				json.dump(nodes, fh, indent=4)
				fh.write("\n")
			tr.add_info(f"Example refs template written to: {out_file}", "tool")
		else:
			json.dump(nodes, sys.stdout, indent=4)
			sys.stdout.write("\n")
	except OSError as exc:
		tr.add_error("AXMPL-004", "tool", str(exc))
		_emit_tracer(tr, out_diag, out_diag_json, waterlint_version, debug=getattr(args, "debug", False))
		return 1
	except Exception as exc:
		tr.add_error("AXMPL-000", "tool", f"[{get_obj_fully_qualified_name(exc)}] {exc}")
		_emit_tracer(tr, out_diag, out_diag_json, waterlint_version, debug=getattr(args, "debug", False))
		return 1
	_emit_tracer(tr, out_diag, out_diag_json, waterlint_version, debug=getattr(args, "debug", False))
	return _final_exit_code(0, tr, args.fail_on_warning)


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
			|Must| construct and return the argparse subparser for the gen-example-template-json command.
	Parameters:
		subparsers:
			The argparse subparser registry of the main command line interface.
		parser_parts:
			Shared parser parts provided by the main program. This command uses the formatter class and the global CLI options.
	Returns:
		|Must| return the configured gen-example-template-json subparser.
	Raises:
	"""
	prsr = subparsers.add_parser(
		"gen-example-template-json",
		help="Generate template JSON for __WTRL_EXAMPLE_REFS__ mappings.",
		parents=[parser_parts["global_opts"]],
		formatter_class=parser_parts["formatter_class"],
	)
	prsr.add_argument(
		"--org-or-project",
		default="none",
		metavar="TEXT",
		help="Value for $id segment <org-or-project> (default: none).",
	)
	prsr.add_argument(
		"--domain",
		default="local",
		metavar="TEXT",
		help="Value for $id segment <domain> (default: local).",
	)
	prsr.add_argument(
		"--out",
		dest="out_file",
		metavar="FILE",
		help="Write template JSON to FILE instead of stdout.",
	)
	prsr.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return prsr
